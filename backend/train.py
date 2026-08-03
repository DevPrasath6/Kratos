from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
from typing import Dict, List

import numpy as np
import torch
from torch.utils.data import DataLoader
from tqdm import tqdm

from augmentations import build_train_transforms, build_validation_transforms
from config import DEFAULT_CONFIG, RoadSegmentationConfig
from dataset import (
    CorruptedMaskError,
    RoadExtractionDataset,
    compute_positive_pixel_weight,
    discover_road_samples,
    split_samples,
)
from losses import build_loss
from metrics import RunningBinaryMetrics, normalize_metrics
from model import KRATOSRoadSegModel
from utils import (
    append_metrics_csv,
    copy_checkpoint,
    ensure_dir,
    estimate_batch_size,
    plot_training_curves,
    save_checkpoint,
    save_epoch_visualization,
    set_seed,
)


def _build_dataloaders(config: RoadSegmentationConfig):
    samples = discover_road_samples(config.dataset_root)
    if not samples:
        return None, None, [], 0.0

    train_samples, val_samples = split_samples(samples, config.validation_split, config.seed)
    pos_weight = compute_positive_pixel_weight(train_samples)
    train_dataset = RoadExtractionDataset(train_samples, transform=build_train_transforms(config.image_size))
    val_dataset = RoadExtractionDataset(val_samples, transform=build_validation_transforms(config.image_size))

    pin_memory = torch.cuda.is_available()
    persistent_workers = config.num_workers > 0
    train_loader = DataLoader(
        train_dataset,
        batch_size=config.batch_size,
        shuffle=True,
        num_workers=config.num_workers,
        pin_memory=pin_memory,
        persistent_workers=persistent_workers,
        drop_last=False,
    )
    val_loader = DataLoader(
        val_dataset,
        batch_size=max(1, config.batch_size // 2),
        shuffle=False,
        num_workers=config.num_workers,
        pin_memory=pin_memory,
        persistent_workers=persistent_workers,
        drop_last=False,
    )
    return train_loader, val_loader, samples, pos_weight


def _compute_warmup_scheduler(optimizer, total_epochs: int, warmup_epochs: int):
    if total_epochs <= 1:
        return None
    warmup_epochs = max(0, min(warmup_epochs, total_epochs - 1))
    cosine_epochs = max(total_epochs - warmup_epochs, 1)
    if warmup_epochs <= 0:
        return torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=cosine_epochs, eta_min=1e-6)
    warmup = torch.optim.lr_scheduler.LinearLR(optimizer, start_factor=0.1, end_factor=1.0, total_iters=warmup_epochs)
    cosine = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=cosine_epochs, eta_min=1e-6)
    return torch.optim.lr_scheduler.SequentialLR(optimizer, schedulers=[warmup, cosine], milestones=[warmup_epochs])


@torch.no_grad()
def _validate(model, val_loader, criterion, device, threshold: float):
    model.eval()
    meter = RunningBinaryMetrics()
    example_batch = None
    for images, masks in val_loader:
        images = images.to(device, non_blocking=True)
        masks = masks.to(device, non_blocking=True)
        with torch.autocast(device_type=device.type, enabled=device.type == "cuda"):
            logits = model(images)
            loss = criterion(logits, masks)
        meter.update(logits, masks, loss=float(loss.item()), threshold=threshold)
        if example_batch is None:
            example_batch = (images.detach().cpu(), masks.detach().cpu(), logits.detach().cpu())
    return meter.compute(), example_batch


def _train_one_epoch(model, train_loader, criterion, optimizer, device, scaler, grad_clip_norm: float, threshold: float):
    model.train()
    meter = RunningBinaryMetrics()
    running_loss = 0.0
    optimizer.zero_grad(set_to_none=True)
    for images, masks in tqdm(train_loader, desc="train", leave=False):
        images = images.to(device, non_blocking=True)
        masks = masks.to(device, non_blocking=True)

        with torch.autocast(device_type=device.type, enabled=device.type == "cuda"):
            logits = model(images)
            loss = criterion(logits, masks)

        if torch.isnan(loss) or torch.isinf(loss):
            raise FloatingPointError("NaN or infinite training loss detected.")

        loss_to_backprop = loss / 1.0
        if scaler is not None:
            scaler.scale(loss_to_backprop).backward()
            scaler.unscale_(optimizer)
            grad_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip_norm)
            if not torch.isfinite(grad_norm):
                raise FloatingPointError("Non-finite gradient norm detected.")
            scaler.step(optimizer)
            scaler.update()
        else:
            loss_to_backprop.backward()
            grad_norm = torch.nn.utils.clip_grad_norm_(model.parameters(), grad_clip_norm)
            if not torch.isfinite(grad_norm):
                raise FloatingPointError("Non-finite gradient norm detected.")
            optimizer.step()

        optimizer.zero_grad(set_to_none=True)
        meter.update(logits.detach(), masks.detach(), loss=float(loss.item()), threshold=threshold)
        running_loss += float(loss.item())

    return meter.compute(), running_loss / max(len(train_loader), 1)


def train_model(
    dataset_dir: str | Path | None = None,
    epochs: int | None = None,
    batch_size: int | str | None = None,
    lr: float | None = None,
    architecture: str | None = None,
    loss_type: str | None = None,
    dry_run: bool = False,
    download_kaggle: bool = False,
    output_dir: str | Path | None = None,
):
    config = DEFAULT_CONFIG
    if dataset_dir is not None:
        config = RoadSegmentationConfig(**{**config.__dict__, "dataset_root": Path(dataset_dir)})
    if output_dir is not None:
        config = RoadSegmentationConfig(**{**config.__dict__, "output_dir": Path(output_dir)})
    if epochs is not None:
        config = RoadSegmentationConfig(**{**config.__dict__, "num_epochs": int(epochs)})
    if lr is not None:
        config = RoadSegmentationConfig(**{**config.__dict__, "learning_rate": float(lr)})
    if architecture is not None:
        config = RoadSegmentationConfig(**{**config.__dict__, "architecture": architecture})
    if loss_type is not None:
        config = RoadSegmentationConfig(**{**config.__dict__, "loss_type": loss_type})

    ensure_dir(config.output_dir)
    ensure_dir(config.visualization_dir)
    set_seed(config.seed)

    if dry_run:
        raise NotImplementedError("Synthetic dry-run was removed in favor of the production road segmentation pipeline.")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if batch_size is not None:
        resolved_batch_size = estimate_batch_size(config.image_size, config.architecture, device, batch_size)
        config = RoadSegmentationConfig(**{**config.__dict__, "batch_size": resolved_batch_size})
    else:
        resolved_batch_size = estimate_batch_size(config.image_size, config.architecture, device, "auto")
        config = RoadSegmentationConfig(**{**config.__dict__, "batch_size": resolved_batch_size})

    train_loader, val_loader, samples, pos_weight = _build_dataloaders(config)
    if train_loader is None or val_loader is None or not samples:
        raise FileNotFoundError(
            f"No DeepGlobe road samples found under {config.dataset_root}. Provide a valid Kaggle dataset directory."
        )

    model = KRATOSRoadSegModel(config.architecture, pretrained=True).to(device)
    should_compile = bool(config.use_compile and hasattr(torch, "compile") and device.type == "cuda")
    if should_compile:
        try:
            import importlib.util

            if importlib.util.find_spec("triton") is None:
                should_compile = False
        except Exception:
            should_compile = False
    if should_compile:
        try:
            model = torch.compile(model)
        except Exception:
            pass

    criterion = build_loss(config.loss_type, pos_weight=pos_weight, alpha=config.focal_alpha, gamma=config.focal_gamma)
    optimizer = torch.optim.AdamW(model.parameters(), lr=config.learning_rate, weight_decay=config.weight_decay)
    scheduler = _compute_warmup_scheduler(optimizer, config.num_epochs, config.warmup_epochs)
    scaler = torch.amp.GradScaler("cuda", enabled=config.use_amp and device.type == "cuda")

    summary = {
        "architecture": config.architecture,
        "image_size": config.image_size,
        "batch_size": config.batch_size,
        "pos_weight": pos_weight,
        "dataset_samples": len(samples),
        "train_samples": len(train_loader.dataset),
        "val_samples": len(val_loader.dataset),
        "loss_type": config.loss_type,
    }
    print(json.dumps(summary, indent=2))

    history: List[Dict[str, object]] = []
    best_score = -1.0
    best_epoch = -1
    patience_counter = 0

    for epoch in range(1, config.num_epochs + 1):
        start_time = time.time()
        train_metrics, train_loss = _train_one_epoch(
            model,
            train_loader,
            criterion,
            optimizer,
            device,
            scaler if config.use_amp and device.type == "cuda" else None,
            config.grad_clip_norm,
            config.mask_threshold,
        )
        val_metrics, example_batch = _validate(model, val_loader, criterion, device, config.mask_threshold)
        if scheduler is not None:
            scheduler.step()

        train_loss = float(train_loss)
        val_loss = float(val_metrics.loss)
        score = (val_metrics.iou + val_metrics.dice) / 2.0
        elapsed = time.time() - start_time
        current_lr = optimizer.param_groups[0]["lr"]

        if example_batch is not None:
            images_cpu, masks_cpu, logits_cpu = example_batch
            prob_map = torch.sigmoid(logits_cpu[0, 0]).numpy()
            pred_mask = (prob_map >= config.mask_threshold).astype(np.uint8)
            save_epoch_visualization(
                config.visualization_dir / f"epoch_{epoch:03d}.png",
                images_cpu[0],
                masks_cpu[0],
                prob_map,
                pred_mask,
            )

        row = {
            "epoch": epoch,
            "train_loss": round(train_loss, 6),
            "val_loss": round(val_loss, 6),
            "train_iou": round(train_metrics.iou, 6),
            "train_dice": round(train_metrics.dice, 6),
            "val_iou": round(val_metrics.iou, 6),
            "val_dice": round(val_metrics.dice, 6),
            "val_precision": round(val_metrics.precision, 6),
            "val_recall": round(val_metrics.recall, 6),
            "val_f1": round(val_metrics.f1, 6),
            "val_pixel_accuracy": round(val_metrics.pixel_accuracy, 6),
            "learning_rate": round(current_lr, 8),
            "epoch_seconds": round(elapsed, 2),
            "pos_weight": round(pos_weight, 4),
        }
        history.append(row)
        append_metrics_csv(config.metrics_csv_path, row)
        plot_training_curves(history, config.curves_path)

        latest_payload = {
            "epoch": epoch,
            "architecture": config.architecture,
            "config": config.__dict__,
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "scheduler_state_dict": scheduler.state_dict() if scheduler is not None else None,
            "metrics": row,
            "history": history,
        }
        save_checkpoint(config.latest_checkpoint_path, latest_payload)

        if score > best_score:
            best_score = score
            best_epoch = epoch
            patience_counter = 0
            save_checkpoint(config.best_checkpoint_path, latest_payload)
            copy_checkpoint(config.best_checkpoint_path, config.legacy_checkpoint_path)
        else:
            patience_counter += 1

        print(
            f"Epoch {epoch:03d}/{config.num_epochs:03d} | "
            f"train_loss={train_loss:.4f} val_loss={val_loss:.4f} "
            f"IoU={val_metrics.iou:.4f} Dice={val_metrics.dice:.4f} "
            f"Prec={val_metrics.precision:.4f} Rec={val_metrics.recall:.4f} F1={val_metrics.f1:.4f} "
            f"Acc={val_metrics.pixel_accuracy:.4f} lr={current_lr:.2e}"
        )

        if epoch > 1 and (val_metrics.iou <= 1e-4 and val_metrics.dice <= 1e-4):
            print("[WARN] Validation prediction collapse detected: metrics are near zero.")
        if patience_counter >= config.patience:
            print(f"[INFO] Early stopping triggered after {config.patience} epochs without improvement.")
            break

    plot_training_curves(history, config.curves_path)
    return {
        "best_epoch": best_epoch,
        "best_score": best_score,
        "history": history,
        "best_checkpoint": str(config.best_checkpoint_path),
        "latest_checkpoint": str(config.latest_checkpoint_path),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Production road extraction trainer")
    parser.add_argument("--dataset-dir", type=str, default=str(DEFAULT_CONFIG.dataset_root))
    parser.add_argument("--output-dir", type=str, default=str(DEFAULT_CONFIG.output_dir))
    parser.add_argument("--epochs", type=int, default=DEFAULT_CONFIG.num_epochs)
    parser.add_argument("--batch-size", type=str, default="auto")
    parser.add_argument("--lr", type=float, default=DEFAULT_CONFIG.learning_rate)
    parser.add_argument("--architecture", type=str, default=DEFAULT_CONFIG.architecture)
    parser.add_argument("--loss-type", type=str, default=DEFAULT_CONFIG.loss_type)
    parser.add_argument("--download-kaggle", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.download_kaggle:
        try:
            import kagglehub

            downloaded_path = kagglehub.dataset_download("balraj98/deepglobe-road-extraction-dataset")
            dataset_dir = downloaded_path
        except Exception:
            dataset_dir = args.dataset_dir
    else:
        dataset_dir = args.dataset_dir

    result = train_model(
        dataset_dir=dataset_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        architecture=args.architecture,
        loss_type=args.loss_type,
        dry_run=args.dry_run,
        download_kaggle=args.download_kaggle,
        output_dir=args.output_dir,
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
