from __future__ import annotations

try:
    import albumentations as A
    from albumentations.pytorch import ToTensorV2
    import cv2
except Exception as exc:  # pragma: no cover - exercised only when dependency is missing.
    A = None
    ToTensorV2 = None
    cv2 = None
    _AUGMENTATION_IMPORT_ERROR = exc
else:
    _AUGMENTATION_IMPORT_ERROR = None


def _require_albumentations() -> None:
    if A is None or ToTensorV2 is None:
        raise RuntimeError(
            "Albumentations is required for the production road segmentation pipeline. "
            "Install backend requirements before training."
        ) from _AUGMENTATION_IMPORT_ERROR


def build_train_transforms(image_size: int):
    _require_albumentations()
    pad_size = image_size + 128
    return A.Compose(
        [
            A.PadIfNeeded(min_height=pad_size, min_width=pad_size, border_mode=cv2.BORDER_REFLECT_101, p=1.0),
            A.RandomCrop(height=image_size, width=image_size, p=1.0),
            A.HorizontalFlip(p=0.5),
            A.VerticalFlip(p=0.5),
            A.RandomRotate90(p=0.5),
            A.Rotate(limit=45, border_mode=cv2.BORDER_REFLECT_101, p=0.6),
            A.Affine(
                translate_percent=(-0.08, 0.08),
                scale=(0.88, 1.12),
                rotate=(-20, 20),
                border_mode=cv2.BORDER_REFLECT_101,
                p=0.7,
            ),
            A.RandomBrightnessContrast(brightness_limit=0.2, contrast_limit=0.2, p=0.7),
            A.CLAHE(clip_limit=(1, 4), tile_grid_size=(8, 8), p=0.35),
            A.GaussNoise(p=0.35),
            A.MotionBlur(blur_limit=7, p=0.25),
            A.ElasticTransform(alpha=18, sigma=6, border_mode=cv2.BORDER_REFLECT_101, p=0.25),
            A.GridDistortion(num_steps=5, distort_limit=0.12, border_mode=cv2.BORDER_REFLECT_101, p=0.25),
            A.RandomShadow(p=0.2),
            A.HueSaturationValue(hue_shift_limit=10, sat_shift_limit=20, val_shift_limit=15, p=0.35),
            A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225), max_pixel_value=255.0),
            ToTensorV2(),
        ]
    )


def build_validation_transforms(image_size: int):
    _require_albumentations()
    return A.Compose(
        [
            A.PadIfNeeded(min_height=image_size, min_width=image_size, border_mode=cv2.BORDER_REFLECT_101, p=1.0),
            A.CenterCrop(height=image_size, width=image_size, p=1.0),
            A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225), max_pixel_value=255.0),
            ToTensorV2(),
        ]
    )


def build_inference_transforms():
    _require_albumentations()
    return A.Compose(
        [
            A.Normalize(mean=(0.485, 0.456, 0.406), std=(0.229, 0.224, 0.225), max_pixel_value=255.0),
            ToTensorV2(),
        ]
    )
