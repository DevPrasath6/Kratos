# KRATOS DeepGlobe Road Extraction Model Training Guide

This guide details how to automatically download and train Kaggle's 4GB **DeepGlobe Road Extraction Dataset** (`balraj98/deepglobe-road-extraction-dataset`) using PyTorch with CPU + GPU mixed precision acceleration for KRATOS satellite vision agents (`RoadExtractionAgent` & `DamageVerificationAgent`).

---

## ⚡ 1. Direct KaggleHub Automated Training

KRATOS includes built-in dataset downloading via `kagglehub`. Simply run:

```bash
cd backend
python train_kratos_model.py --download-kaggle --epochs 5 --batch-size 8
```

This command automatically:
1. Downloads `balraj98/deepglobe-road-extraction-dataset` directly from Kaggle.
2. Loads satellite RGB tiles (`*_sat.jpg`) and target road masks (`*_mask.png`).
3. Trains a high-efficiency PyTorch Segmentation Model using FP16 mixed-precision CUDA GPU acceleration + multi-worker CPU data loading.
4. Saves fine-tuned weights directly to `backend/models/kratos_finetuned_segmentation.pt`.

---

## 🧪 2. Fast Dry-Run Pipeline Validation

To test the training pipeline locally with synthetic satellite data before running full training:

```bash
cd backend
python train_kratos_model.py --dry-run
```

---

## 🔌 3. Dynamic Weight Ingestion into KRATOS

Once training completes, the saved model weights (`backend/models/kratos_finetuned_segmentation.pt`) are automatically loaded by:
- `RoadExtractionAgent` (`backend/agents/road_extraction_agent.py`)
- `DamageVerificationAgent` (`backend/agents/damage_verification_agent.py`)

No additional configuration is needed — KRATOS detects the saved `.pt` weights on startup and utilizes them for instant local road segmentation & damage classification!

---

## 🚀 4. Launching Mission Control

```bash
# Terminal 1: Backend
cd backend
uvicorn main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

Visit `http://localhost:5173` to test live satellite inference on the NASA Mission-Control Dashboard!
