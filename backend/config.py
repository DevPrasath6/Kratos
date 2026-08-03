from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import os


@dataclass(frozen=True)
class RoadSegmentationConfig:
    project_root: Path = field(default_factory=lambda: Path(__file__).resolve().parent)
    dataset_root: Path = field(default_factory=lambda: Path(__file__).resolve().parent / "data" / "dataset")
    output_dir: Path = field(default_factory=lambda: Path(__file__).resolve().parent / "models")
    checkpoint_name: str = "best_model.pt"
    latest_checkpoint_name: str = "latest.pt"
    legacy_checkpoint_name: str = "kratos_finetuned_segmentation.pt"
    architecture: str = "segformer_b3"
    image_size: int = 1024
    tile_size: int = 1024
    tile_overlap: int = 256
    mask_threshold: float = 0.5
    min_component_size: int = 128
    batch_size: int = 2
    num_epochs: int = 50
    learning_rate: float = 1e-4
    weight_decay: float = 1e-4
    warmup_epochs: int = 2
    patience: int = 10
    grad_clip_norm: float = 1.0
    validation_split: float = 0.2
    seed: int = 42
    num_workers: int = max(2, min(8, (os.cpu_count() or 4)))
    use_amp: bool = True
    use_compile: bool = True
    loss_type: str = "dice_bce"
    focal_alpha: float = 0.25
    focal_gamma: float = 2.0
    sample_visualization_limit: int = 1
    cosine_min_lr: float = 1e-6
    max_gradient_norm_warning: float = 25.0

    @property
    def visualization_dir(self) -> Path:
        return self.output_dir / "visualizations"

    @property
    def metrics_csv_path(self) -> Path:
        return self.output_dir / "metrics.csv"

    @property
    def curves_path(self) -> Path:
        return self.output_dir / "training_curves.png"

    @property
    def best_checkpoint_path(self) -> Path:
        return self.output_dir / self.checkpoint_name

    @property
    def latest_checkpoint_path(self) -> Path:
        return self.output_dir / self.latest_checkpoint_name

    @property
    def legacy_checkpoint_path(self) -> Path:
        return self.output_dir / self.legacy_checkpoint_name


DEFAULT_CONFIG = RoadSegmentationConfig()
