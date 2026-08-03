from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


class DiceLoss(nn.Module):
    def __init__(self, smooth: float = 1.0) -> None:
        super().__init__()
        self.smooth = smooth

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        probs = torch.sigmoid(logits)
        probs = probs.flatten(start_dim=1)
        targets = targets.float().flatten(start_dim=1)

        intersection = (probs * targets).sum(dim=1)
        denominator = probs.sum(dim=1) + targets.sum(dim=1)
        dice = (2.0 * intersection + self.smooth) / (denominator + self.smooth)
        return 1.0 - dice.mean()


class FocalLossWithLogits(nn.Module):
    def __init__(self, alpha: float = 0.25, gamma: float = 2.0, reduction: str = "mean") -> None:
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.reduction = reduction

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        targets = targets.float()
        bce = F.binary_cross_entropy_with_logits(logits, targets, reduction="none")
        probs = torch.sigmoid(logits)
        p_t = probs * targets + (1.0 - probs) * (1.0 - targets)
        alpha_factor = self.alpha * targets + (1.0 - self.alpha) * (1.0 - targets)
        focal = alpha_factor * (1.0 - p_t).pow(self.gamma) * bce

        if self.reduction == "sum":
            return focal.sum()
        if self.reduction == "none":
            return focal
        return focal.mean()


class DiceBCELoss(nn.Module):
    def __init__(self, pos_weight: float = 1.0) -> None:
        super().__init__()
        self.dice = DiceLoss()
        self.bce = nn.BCEWithLogitsLoss(pos_weight=torch.tensor([pos_weight], dtype=torch.float32))

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        return 0.5 * self.dice(logits, targets) + 0.5 * self.bce(logits, targets.float())


class DiceFocalLoss(nn.Module):
    def __init__(self, alpha: float = 0.25, gamma: float = 2.0) -> None:
        super().__init__()
        self.dice = DiceLoss()
        self.focal = FocalLossWithLogits(alpha=alpha, gamma=gamma)

    def forward(self, logits: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        return 0.5 * self.dice(logits, targets) + 0.5 * self.focal(logits, targets)


def build_loss(loss_type: str, pos_weight: float, alpha: float = 0.25, gamma: float = 2.0) -> nn.Module:
    normalized = loss_type.strip().lower()
    if normalized in {"dice_focal", "focal", "dice+focal"}:
        return DiceFocalLoss(alpha=alpha, gamma=gamma)
    return DiceBCELoss(pos_weight=pos_weight)
