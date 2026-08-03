from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F


def _build_segformer_binary_model(pretrained: bool = True) -> nn.Module:
    try:
        from transformers import SegformerConfig, SegformerForSemanticSegmentation
    except Exception as exc:  # pragma: no cover - only raised if dependency missing.
        raise RuntimeError(
            "transformers is required for SegFormer-B3. Install backend requirements first."
        ) from exc

    model_name = "nvidia/segformer-b3-finetuned-ade-512-512"
    if pretrained:
        try:
            return SegformerForSemanticSegmentation.from_pretrained(
                model_name,
                num_labels=1,
                ignore_mismatched_sizes=True,
                local_files_only=False,
            )
        except Exception:
            pass

    config = SegformerConfig(
        num_labels=1,
        num_channels=3,
        depths=[3, 4, 18, 3],
        hidden_sizes=[64, 128, 320, 512],
        decoder_hidden_size=768,
        mlp_ratios=[4, 4, 4, 4],
        num_attention_heads=[1, 2, 5, 8],
        sr_ratios=[8, 4, 2, 1],
        drop_path_rate=0.1,
    )
    return SegformerForSemanticSegmentation(config)


def _build_deeplabv3plus_resnet101(pretrained: bool = True) -> nn.Module:
    try:
        import segmentation_models_pytorch as smp
    except Exception as exc:  # pragma: no cover - only raised if dependency missing.
        raise RuntimeError(
            "segmentation-models-pytorch is required for DeepLabV3+ and U-Net++. Install backend requirements first."
        ) from exc

    encoder_weights = "imagenet" if pretrained else None
    return smp.DeepLabV3Plus(
        encoder_name="resnet101",
        encoder_weights=encoder_weights,
        in_channels=3,
        classes=1,
        activation=None,
    )


def _build_unetpp_efficientnet_b5(pretrained: bool = True) -> nn.Module:
    try:
        import segmentation_models_pytorch as smp
    except Exception as exc:  # pragma: no cover - only raised if dependency missing.
        raise RuntimeError(
            "segmentation-models-pytorch is required for DeepLabV3+ and U-Net++. Install backend requirements first."
        ) from exc

    encoder_weights = "imagenet" if pretrained else None
    return smp.UnetPlusPlus(
        encoder_name="efficientnet-b5",
        encoder_weights=encoder_weights,
        in_channels=3,
        classes=1,
        activation=None,
    )


class KRATOSRoadSegModel(nn.Module):
    def __init__(self, architecture: str = "segformer_b3", pretrained: bool = True):
        super().__init__()
        self.architecture = architecture.lower().strip()
        self.pretrained = pretrained
        self.model = build_segmentation_model(self.architecture, pretrained=self.pretrained)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        logits = self.model(x)
        if isinstance(logits, tuple):
            logits = logits[0]
        if hasattr(logits, "logits"):
            logits = logits.logits
        if logits.ndim == 4 and logits.shape[-2:] != x.shape[-2:]:
            logits = F.interpolate(logits, size=x.shape[-2:], mode="bilinear", align_corners=False)
        return logits


def build_segmentation_model(architecture: str, pretrained: bool = True) -> nn.Module:
    normalized = architecture.strip().lower()
    if normalized in {"segformer_b3", "segformer-b3", "segformer"}:
        return _build_segformer_binary_model(pretrained=pretrained)
    if normalized in {"deeplabv3plus_resnet101", "deeplabv3+", "deeplabv3plus"}:
        return _build_deeplabv3plus_resnet101(pretrained=pretrained)
    if normalized in {"unetpp_efficientnet_b5", "unet++", "unetplusplus"}:
        return _build_unetpp_efficientnet_b5(pretrained=pretrained)
    raise ValueError(
        f"Unsupported architecture '{architecture}'. Expected SegFormer-B3, DeepLabV3+ ResNet101, or U-Net++ EfficientNet-B5."
    )
