from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Sequence, Tuple

import numpy as np
import torch
from PIL import Image
from torch.utils.data import Dataset

try:
    import cv2
except Exception:  # pragma: no cover - cv2 is already a project dependency.
    cv2 = None


@dataclass(frozen=True)
class RoadSample:
    image_path: Path
    mask_path: Path


class CorruptedMaskError(ValueError):
    pass


def _candidate_mask_paths(image_path: Path) -> List[Path]:
    stem = image_path.stem
    if stem.endswith("_sat"):
        base = stem[:-4]
    else:
        base = stem
    candidates = [
        image_path.with_name(f"{base}_mask.png"),
        image_path.with_name(f"{base}_mask.jpg"),
        image_path.with_name(f"{base}_mask.jpeg"),
    ]
    return candidates


def discover_road_samples(dataset_root: Path | str) -> List[RoadSample]:
    root = Path(dataset_root)
    if not root.exists():
        return []

    image_paths: List[Path] = []
    for suffix in ("*_sat.jpg", "*_sat.jpeg", "*_sat.png", "*_sat.JPG", "*_sat.JPEG", "*_sat.PNG"):
        image_paths.extend(root.rglob(suffix))

    samples: List[RoadSample] = []
    for image_path in sorted({path.resolve() for path in image_paths}):
        mask_path = next((candidate for candidate in _candidate_mask_paths(image_path) if candidate.exists()), None)
        if mask_path is None:
            continue
        try:
            with Image.open(image_path) as image:
                image.verify()
            with Image.open(mask_path) as mask:
                mask.verify()
        except Exception:
            continue
        samples.append(RoadSample(image_path=image_path, mask_path=mask_path))
    return samples


def load_binary_mask(mask_path: Path, target_size: Tuple[int, int] | None = None) -> np.ndarray:
    try:
        with Image.open(mask_path) as mask_image:
            mask = mask_image.convert("L")
            mask_array = np.asarray(mask, dtype=np.uint8)
    except Exception as exc:
        raise CorruptedMaskError(f"Unable to read mask {mask_path}: {exc}") from exc

    if mask_array.ndim != 2 or mask_array.size == 0:
        raise CorruptedMaskError(f"Mask {mask_path} is not a valid 2D binary image.")

    unique_values = np.unique(mask_array)
    if not np.array_equal(unique_values, np.array([0], dtype=np.uint8)):
        if unique_values.max() > 1:
            mask_array = (mask_array > 127).astype(np.uint8)
        else:
            mask_array = (mask_array > 0).astype(np.uint8)

    if target_size is not None and tuple(mask_array.shape[::-1]) != target_size:
        if cv2 is None:
            raise CorruptedMaskError(
                f"Mask {mask_path} size {mask_array.shape[::-1]} does not match image size {target_size}."
            )
        mask_array = cv2.resize(mask_array, target_size, interpolation=cv2.INTER_NEAREST).astype(np.uint8)

    mask_array = (mask_array > 0).astype(np.uint8)
    return mask_array


class RoadExtractionDataset(Dataset):
    def __init__(
        self,
        samples: Sequence[RoadSample],
        transform=None,
        return_paths: bool = False,
    ) -> None:
        self.samples = list(samples)
        self.transform = transform
        self.return_paths = return_paths

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, index: int):
        sample = self.samples[index]
        try:
            with Image.open(sample.image_path) as image_file:
                image = image_file.convert("RGB")
                image_size = image.size
        except Exception as exc:
            raise CorruptedMaskError(f"Unable to read image {sample.image_path}: {exc}") from exc

        mask = load_binary_mask(sample.mask_path, target_size=image_size)
        image_array = np.asarray(image, dtype=np.uint8)

        if self.transform is not None:
            augmented = self.transform(image=image_array, mask=mask)
            image_tensor = augmented["image"]
            mask_tensor = augmented["mask"]
        else:
            image_tensor = torch.from_numpy(image_array.transpose(2, 0, 1)).float() / 255.0
            mask_tensor = torch.from_numpy(mask[None, ...].astype(np.float32))

        if mask_tensor.ndim == 2:
            mask_tensor = mask_tensor.unsqueeze(0)
        mask_tensor = mask_tensor.float()

        if self.return_paths:
            return image_tensor, mask_tensor, str(sample.image_path), str(sample.mask_path)
        return image_tensor, mask_tensor


def split_samples(
    samples: Sequence[RoadSample],
    validation_split: float,
    seed: int,
) -> tuple[list[RoadSample], list[RoadSample]]:
    items = list(samples)
    if not items:
        return [], []

    generator = torch.Generator().manual_seed(seed)
    permutation = torch.randperm(len(items), generator=generator).tolist()
    shuffled = [items[index] for index in permutation]
    val_count = max(1, int(round(len(shuffled) * validation_split))) if len(shuffled) > 1 else 0
    val_samples = shuffled[:val_count]
    train_samples = shuffled[val_count:] if val_count < len(shuffled) else shuffled[:1]
    return train_samples, val_samples


def compute_positive_pixel_weight(samples: Sequence[RoadSample]) -> float:
    positive_pixels = 0
    total_pixels = 0

    for sample in samples:
        try:
            mask = load_binary_mask(sample.mask_path)
            positive_pixels += int(mask.sum())
            total_pixels += int(mask.size)
        except CorruptedMaskError:
            continue

    if positive_pixels == 0:
        return 1.0

    negative_pixels = max(total_pixels - positive_pixels, 1)
    weight = float(negative_pixels / positive_pixels)
    return float(np.clip(weight, 1.0, 100.0))
