import base64
import io
import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import cv2
import numpy as np
from agents.base import BaseAgent
from agents.nim_client import vision_client, NIM_API_KEY
from infer import RoadSegmentationInferencer

_road_inferencer: Optional[RoadSegmentationInferencer] = None


def _get_road_inferencer() -> Optional[RoadSegmentationInferencer]:
    global _road_inferencer
    if _road_inferencer is not None:
        return _road_inferencer

    backend_dir = Path(__file__).resolve().parent.parent
    checkpoint_path = backend_dir / "models" / "best_model.pt"
    if not checkpoint_path.exists():
        latest_path = backend_dir / "models" / "latest.pt"
        if latest_path.exists():
            checkpoint_path = latest_path
        else:
            return None

    try:
        _road_inferencer = RoadSegmentationInferencer(checkpoint_path=checkpoint_path)
    except Exception:
        _road_inferencer = None
    return _road_inferencer


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

        inferencer = _get_road_inferencer()
        if inferencer is not None:
            try:
                prediction = inferencer.predict_b64(image_b64)
                res = dict(input_data) if input_data else {}
                res.update({
                    "segments": prediction.segments,
                    "source": "pytorch_model",
                    "confidence": prediction.confidence,
                    "binary_mask_shape": list(prediction.binary_mask.shape),
                    "graph": prediction.graph,
                })
                return res
            except Exception:
                pass

        return self._cv_fallback(image_b64, input_data)

    def _cv_fallback(self, image_b64: str, input_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Classical CV fallback for environments without trained segmentation weights."""
        try:
            img_bytes = base64.b64decode(image_b64)
            image_array = cv2.imdecode(np.frombuffer(img_bytes, dtype=np.uint8), cv2.IMREAD_COLOR)
            if image_array is None:
                raise ValueError("Unable to decode input image.")
            gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            edges = cv2.Canny(blurred, 40, 120)
            kernel = np.ones((3, 3), np.uint8)
            cleaned = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel, iterations=2)
            cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_OPEN, kernel, iterations=1)

            lines = cv2.HoughLinesP(
                cleaned,
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
            res.update({"segments": segments, "source": "cv_fallback", "confidence": 0.5})
            return res
        except Exception as e:
            print(f"CV fallback failed: {e}")
            res = dict(input_data) if input_data else {}
            res.update({"segments": [], "source": "cv_fallback_error", "confidence": 0.0})
            return res
