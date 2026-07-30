import base64
import io
import os
import json
import numpy as np
import cv2
import torch
import torchvision.transforms as T
from PIL import Image
from typing import Any, Dict, List
from agents.base import BaseAgent
from agents.nim_client import vision_client, NIM_API_KEY
from models.road_seg_model import KRATOSRoadSegModel

_road_model = None
_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def _get_road_model():
    global _road_model
    if _road_model is None:
        model_path = os.path.join(os.path.dirname(__file__), "..", "models", "kratos_finetuned_segmentation.pt")
        model = KRATOSRoadSegModel().to(_device)
        if os.path.exists(model_path):
            model.load_state_dict(torch.load(model_path, map_location=_device))
        model.eval()
        _road_model = model
    return _road_model


class RoadExtractionAgent(BaseAgent):
    name: str = "road_extraction"

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Input: { "image_b64": "<base64_string>" }
        Returns: {
            "segments": [[x1, y1, x2, y2], ...],
            "source": "nim_vlm" | "cv_fallback",
            "confidence": float
        }
        """
        image_b64 = input_data.get("image_b64")
        if not image_b64:
            from agents.image_ingestion_agent import ImageIngestionAgent
            ingest_res = await ImageIngestionAgent().run({"use_sample": True})
            image_b64 = ingest_res.get("image_b64")
            input_data = dict(input_data)
            input_data["image_b64"] = image_b64

        # Try NIM VLM endpoint if API key and client exist
        if NIM_API_KEY and vision_client:
            try:
                response = vision_client.invoke([
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Identify visible road-like linear structures in this satellite image. Return approximate pixel line coordinates as JSON list of lists [[x1,y1,x2,y2], ...] and a overall confidence score float (0-1). Format: {\"segments\": [...], \"confidence\": 0.8}",
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/png;base64,{image_b64}"},
                            },
                        ],
                    }
                ])

                content_str = response.content if isinstance(response.content, str) else str(response.content)
                # Attempt to parse JSON from VLM output
                parsed = json.loads(content_str)
                if "segments" in parsed and isinstance(parsed["segments"], list):
                    res = dict(input_data)
                    res.update({
                        "segments": parsed["segments"],
                        "source": "nim_vlm",
                        "confidence": float(parsed.get("confidence", 0.8)),
                    })
                    return res
            except Exception:
                pass  # Fallback to OpenCV on any error

        # PyTorch model inference path
        return self._pytorch_inference(image_b64, input_data)

    def _pytorch_inference(self, image_b64: str, input_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """PyTorch Model Inference + OpenCV Post-Processing."""
        try:
            model = _get_road_model()
            
            img_bytes = base64.b64decode(image_b64)
            image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            
            transform = T.Compose([
                T.Resize((256, 256)),
                T.ToTensor(),
                T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ])
            
            input_tensor = transform(image).unsqueeze(0).to(_device)
            
            with torch.no_grad():
                output = model(input_tensor)
                mask = (output > 0.5).float().squeeze().cpu().numpy()
                
            original_width, original_height = image.size
            mask_uint8 = (mask * 255).astype(np.uint8)
            mask_resized = cv2.resize(mask_uint8, (original_width, original_height), interpolation=cv2.INTER_NEAREST)
            
            lines = cv2.HoughLinesP(
                mask_resized,
                rho=1,
                theta=np.pi / 180,
                threshold=5,
                minLineLength=5,
                maxLineGap=20,
            )

            segments: List[List[int]] = []
            if lines is not None:
                for line in lines:
                    coords = line[0] if len(line.shape) > 1 else line
                    x1, y1, x2, y2 = int(coords[0]), int(coords[1]), int(coords[2]), int(coords[3])
                    segments.append([x1, y1, x2, y2])

            res = dict(input_data) if input_data else {}
            res.update({
                "segments": segments,
                "source": "pytorch_model",
                "confidence": 0.9,
            })
            return res
        except Exception as e:
            print(f"PyTorch inference failed: {e}")
            res = dict(input_data) if input_data else {}
            res.update({"segments": [], "source": "pytorch_model_error", "confidence": 0.0})
            return res
