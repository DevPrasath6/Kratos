from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Dict

import numpy as np
import torch


@dataclass
class BinarySegmentationMetrics:
    loss: float = 0.0
    iou: float = 0.0
    dice: float = 0.0
    precision: float = 0.0
    recall: float = 0.0
    f1: float = 0.0
    pixel_accuracy: float = 0.0

    def to_dict(self) -> Dict[str, float]:
        return asdict(self)


class RunningBinaryMetrics:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.loss_sum = 0.0
        self.sample_count = 0
        self.tp = 0.0
        self.fp = 0.0
        self.fn = 0.0
        self.tn = 0.0

    def update(self, logits: torch.Tensor, targets: torch.Tensor, loss: float, threshold: float = 0.5) -> None:
        with torch.no_grad():
            probs = torch.sigmoid(logits)
            preds = (probs >= threshold).float()
            targets = targets.float()

            self.tp += float((preds * targets).sum().item())
            self.fp += float((preds * (1.0 - targets)).sum().item())
            self.fn += float(((1.0 - preds) * targets).sum().item())
            self.tn += float(((1.0 - preds) * (1.0 - targets)).sum().item())
            self.loss_sum += float(loss)
            self.sample_count += int(targets.shape[0])

    def compute(self) -> BinarySegmentationMetrics:
        precision = self.tp / max(self.tp + self.fp, 1.0)
        recall = self.tp / max(self.tp + self.fn, 1.0)
        f1 = (2.0 * precision * recall) / max(precision + recall, 1e-8)
        iou = self.tp / max(self.tp + self.fp + self.fn, 1.0)
        dice = (2.0 * self.tp) / max((2.0 * self.tp) + self.fp + self.fn, 1.0)
        pixel_accuracy = (self.tp + self.tn) / max(self.tp + self.tn + self.fp + self.fn, 1.0)
        return BinarySegmentationMetrics(
            loss=self.loss_sum / max(self.sample_count, 1),
            iou=float(iou),
            dice=float(dice),
            precision=float(precision),
            recall=float(recall),
            f1=float(f1),
            pixel_accuracy=float(pixel_accuracy),
        )


def metrics_from_logits(logits: torch.Tensor, targets: torch.Tensor, loss_value: float, threshold: float = 0.5) -> BinarySegmentationMetrics:
    meter = RunningBinaryMetrics()
    meter.update(logits, targets, loss=loss_value, threshold=threshold)
    return meter.compute()


def normalize_metrics(metrics: Dict[str, float]) -> Dict[str, float]:
    return {key: float(np.nan_to_num(value, nan=0.0, posinf=0.0, neginf=0.0)) for key, value in metrics.items()}
