import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

# Add TUI-singleagent to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "TUI-singleagent"))

from ascii_banner import KRATOS_BLOCK_BANNER
from nim_health import fetch_nim_health
from main import app


def test_tui_singleagent_banner():
    assert "Dzio" in KRATOS_BLOCK_BANNER
    assert "Knowledge-driven Road Analysis" in KRATOS_BLOCK_BANNER


def test_nim_health_endpoint():
    client = TestClient(app)
    resp = client.get("/api/agents/nim/health")
    assert resp.status_code == 200
    data = resp.json()
    assert "vlm_model" in data
    assert "reasoning_model" in data
    assert "vlm_status" in data
