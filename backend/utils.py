from __future__ import annotations

import csv
import os
import random
import shutil
import warnings
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

import numpy as np
import torch


def ensure_dir(path: Path | str) -> Path:
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.benchmark = True
    torch.backends.cudnn.deterministic = False


def select_num_workers(requested: int | None = None) -> int:
    return requested or max(2, min(8, (os.cpu_count() or 4) // 2 or 2))


def estimate_batch_size(image_size: int, architecture: str, device: torch.device, requested: int | str | None = None) -> int:
    if isinstance(requested, int) and requested > 0:
        return requested
    if requested == "auto" or requested is None or requested <= 0:
        if device.type != "cuda":
            return 2
        free_bytes, _ = torch.cuda.mem_get_info()
        free_gb = free_bytes / (1024 ** 3)
        if architecture.startswith("segformer"):
            scale = 5.5 if image_size >= 1024 else 3.5
        elif architecture.startswith("deeplab"):
            scale = 4.5 if image_size >= 1024 else 3.0
        else:
            scale = 4.0 if image_size >= 1024 else 2.5
        batch = max(1, int(free_gb / scale))
        return min(batch, 16)
    return int(requested)


def save_checkpoint(path: Path | str, payload: Dict[str, object]) -> None:
    path = Path(path)
    ensure_dir(path.parent)
    torch.save(payload, path)


def load_checkpoint(path: Path | str, map_location: str | torch.device = "cpu") -> Dict[str, object]:
    return torch.load(Path(path), map_location=map_location)


def copy_checkpoint(source: Path | str, destination: Path | str) -> None:
    source_path = Path(source)
    destination_path = Path(destination)
    if source_path.exists():
        ensure_dir(destination_path.parent)
        shutil.copy2(source_path, destination_path)


def append_metrics_csv(csv_path: Path | str, row: Dict[str, object]) -> None:
    csv_path = Path(csv_path)
    ensure_dir(csv_path.parent)
    write_header = not csv_path.exists()
    with csv_path.open("a", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(row.keys()))
        if write_header:
            writer.writeheader()
        writer.writerow(row)


def plot_training_curves(metrics_rows: Sequence[Dict[str, object]], output_path: Path | str) -> None:
    if not metrics_rows:
        return

    import matplotlib.pyplot as plt

    output_path = Path(output_path)
    ensure_dir(output_path.parent)

    epochs = [row["epoch"] for row in metrics_rows]
    train_loss = [row["train_loss"] for row in metrics_rows]
    val_loss = [row["val_loss"] for row in metrics_rows]
    iou = [row["val_iou"] for row in metrics_rows]
    dice = [row["val_dice"] for row in metrics_rows]

    fig, axes = plt.subplots(1, 2, figsize=(14, 5), dpi=160)
    axes[0].plot(epochs, train_loss, label="Train Loss", linewidth=2)
    axes[0].plot(epochs, val_loss, label="Val Loss", linewidth=2)
    axes[0].set_title("Training Curves")
    axes[0].set_xlabel("Epoch")
    axes[0].set_ylabel("Loss")
    axes[0].grid(alpha=0.3)
    axes[0].legend()

    axes[1].plot(epochs, iou, label="IoU", linewidth=2)
    axes[1].plot(epochs, dice, label="Dice", linewidth=2)
    axes[1].set_title("Validation Quality")
    axes[1].set_xlabel("Epoch")
    axes[1].set_ylabel("Score")
    axes[1].set_ylim(0.0, 1.0)
    axes[1].grid(alpha=0.3)
    axes[1].legend()

    fig.tight_layout()
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)


def denormalize_image(image_tensor: torch.Tensor) -> np.ndarray:
    tensor = image_tensor.detach().cpu().float()
    mean = torch.tensor([0.485, 0.456, 0.406], dtype=tensor.dtype).view(3, 1, 1)
    std = torch.tensor([0.229, 0.224, 0.225], dtype=tensor.dtype).view(3, 1, 1)
    tensor = tensor * std + mean
    tensor = torch.clamp(tensor, 0.0, 1.0)
    array = (tensor.permute(1, 2, 0).numpy() * 255.0).astype(np.uint8)
    return array


def overlay_mask(image_rgb: np.ndarray, mask: np.ndarray, color: tuple[int, int, int] = (0, 255, 0), alpha: float = 0.45) -> np.ndarray:
    overlay = image_rgb.copy().astype(np.float32)
    mask_bool = mask.astype(bool)
    color_array = np.array(color, dtype=np.float32).reshape(1, 1, 3)
    overlay[mask_bool] = overlay[mask_bool] * (1.0 - alpha) + color_array * alpha
    return overlay.astype(np.uint8)


def save_epoch_visualization(
    output_path: Path | str,
    image_tensor: torch.Tensor,
    target_mask: torch.Tensor,
    predicted_prob_map: np.ndarray,
    predicted_mask: np.ndarray,
) -> None:
    import matplotlib.pyplot as plt

    output_path = Path(output_path)
    ensure_dir(output_path.parent)

    image_rgb = denormalize_image(image_tensor)
    target = target_mask.detach().cpu().numpy().squeeze()
    overlay = overlay_mask(image_rgb, predicted_mask)

    fig, axes = plt.subplots(1, 5, figsize=(22, 5), dpi=160)
    panels = [
        (image_rgb, "Input Image", None),
        (target, "Ground Truth", "gray"),
        (predicted_mask, "Prediction", "gray"),
        (overlay, "Overlay", None),
        (predicted_prob_map, "Probability Map", "magma"),
    ]

    for axis, (panel, title, cmap) in zip(axes, panels):
        axis.imshow(panel, cmap=cmap)
        axis.set_title(title)
        axis.axis("off")

    fig.tight_layout()
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)


def warn_suspicious_prediction(prob_map: np.ndarray, threshold: float = 0.5) -> None:
    mean_prob = float(prob_map.mean())
    positive_ratio = float((prob_map >= threshold).mean())
    if mean_prob >= 0.97 or positive_ratio >= 0.95:
        warnings.warn("Collapsed prediction detected: model is predicting nearly all-road.")
    if mean_prob <= 0.03 or positive_ratio <= 0.01:
        warnings.warn("Collapsed prediction detected: model is predicting nearly all-background.")
