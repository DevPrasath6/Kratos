import base64
import io
import json
import numpy as np
import cv2
from typing import Any, Dict, List
from agents.base import BaseAgent
from agents.nim_client import vision_client, NIM_API_KEY


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

        # OpenCV Fallback path
        return self._cv_fallback(image_b64, input_data)

    def _cv_fallback(self, image_b64: str, input_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Classical CV: grayscale -> Canny edge detection -> Probabilistic Hough Line Transform."""
        try:
            img_bytes = base64.b64decode(image_b64)
            nparr = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            if img is None:
                res = dict(input_data) if input_data else {}
                res.update({"segments": [], "source": "cv_fallback", "confidence": 0.5})
                return res

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # Blur & Canny edge detection
            edges = cv2.Canny(gray, threshold1=10, threshold2=100)

            # Hough Line Transform
            lines = cv2.HoughLinesP(
                edges,
                rho=1,
                theta=np.pi / 180,
                threshold=10,
                minLineLength=5,
                maxLineGap=15,
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
                "source": "cv_fallback",
                "confidence": 0.5,
            })
            return res
        except Exception:
            res = dict(input_data) if input_data else {}
            res.update({"segments": [], "source": "cv_fallback", "confidence": 0.5})
            return res
