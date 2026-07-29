import io
import pytest
import numpy as np
import cv2
from PIL import Image
from fastapi.testclient import TestClient
from agents.image_ingestion_agent import ImageIngestionAgent
from agents.road_extraction_agent import RoadExtractionAgent
from main import app


def create_synthetic_image_bytes() -> bytes:
    """Create a 200x200 black PNG image with high-contrast white roads."""
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    # Draw high-contrast white lines (roads)
    cv2.line(img, (10, 100), (190, 100), (255, 255, 255), 2)
    cv2.line(img, (100, 10), (100, 190), (255, 255, 255), 2)

    is_success, buffer = cv2.imencode(".png", img)
    return buffer.tobytes()


@pytest.mark.asyncio
async def test_image_ingestion_agent():
    agent = ImageIngestionAgent()
    img_bytes = create_synthetic_image_bytes()

    res = await agent.run({"image_bytes": img_bytes, "max_dim": 100})
    assert "image_b64" in res
    assert res["width"] <= 100
    assert res["height"] <= 100
    assert res["format"] == "PNG"


@pytest.mark.asyncio
async def test_road_extraction_agent_fallback():
    ingestion = ImageIngestionAgent()
    road_agent = RoadExtractionAgent()
    img_bytes = create_synthetic_image_bytes()

    ingest_res = await ingestion.run({"image_bytes": img_bytes})
    b64_str = ingest_res["image_b64"]

    # Without NIM_API_KEY set, it must fallback to OpenCV
    extract_res = await road_agent.run({"image_b64": b64_str})
    assert extract_res["source"] == "cv_fallback"
    assert extract_res["confidence"] == 0.5
    assert isinstance(extract_res["segments"], list)
    assert len(extract_res["segments"]) > 0


def test_api_upload_and_segment():
    client = TestClient(app)
    img_bytes = create_synthetic_image_bytes()

    # Test Upload endpoint
    upload_resp = client.post(
        "/api/agents/upload",
        files={"file": ("synthetic.png", img_bytes, "image/png")}
    )
    assert upload_resp.status_code == 200
    upload_data = upload_resp.json()
    assert upload_data["status"] == "success"
    b64_str = upload_data["result"]["image_b64"]

    # Test Segment endpoint
    segment_resp = client.post(
        "/api/agents/segment",
        json={"image_b64": b64_str}
    )
    assert segment_resp.status_code == 200
    segment_data = segment_resp.json()
    assert segment_data["status"] == "success"
    assert len(segment_data["result"]["segments"]) > 0
    assert segment_data["result"]["source"] == "cv_fallback"
