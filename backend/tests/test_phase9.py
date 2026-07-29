import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

tui_path = Path(__file__).parent.parent.parent / "tui"
sys.path.insert(0, str(tui_path))

from ascii_banner import KRATOS_BLOCK_BANNER
from main import app


def test_tui_ascii_banner():
    assert "Knowledge-driven Road Analysis" in KRATOS_BLOCK_BANNER


def test_websocket_status_endpoint():
    client = TestClient(app)
    with client.websocket_connect("/ws/status") as websocket:
        data = websocket.receive_json()
        assert isinstance(data, dict)
