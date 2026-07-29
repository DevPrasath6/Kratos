import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_get_agents_status():
    response = client.get("/api/agents/status")
    assert response.status_code == 200
    status_data = response.json()
    # Ensure all 13 core agents are returned
    assert len(status_data) >= 13
    for agent_name, info in status_data.items():
        assert "name" in info
        assert "purpose" in info
        assert "status" in info
        assert len(info["purpose"]) > 5


def test_standalone_agent_runs():
    test_cases = [
        ("ping", {}),
        ("image_ingestion", {}),
        ("road_extraction", {"image_b64": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="}),
        ("road_graph", {"use_sample": True}),
        ("disaster_simulation", {"disaster_type": "flood", "severity": 4}),
        ("route_planning", {"start_node": 0, "target_node": 8}),
        ("traffic_analysis", {"seed": 42}),
        ("resource_allocation", {"vehicle_count": 5}),
        ("volunteer_healthcare_dispatch", {"volunteer_count": 10}),
        ("radio_frequency_alert", {"disaster_type": "flood", "severity": 4}),
        ("notification", {"disaster_type": "flood"}),
        ("report_generation", {"disaster_type": "flood", "severity": 4}),
        ("audit", {"limit": 10}),
    ]

    for agent_name, payload in test_cases:
        res = client.post(f"/api/agents/{agent_name}/run", json=payload)
        assert res.status_code == 200, f"Agent {agent_name} failed with status {res.status_code}: {res.text}"
        data = res.json()
        assert data.get("status") == "success"
        assert "result" in data


def test_full_12_agent_pipeline_e2e():
    pipeline_payload = {
        "use_sample": True,
        "disaster_type": "flood",
        "severity": 4,
        "start_node": 0,
        "target_node": 8,
    }

    res = client.post("/api/agents/pipeline/run", json=pipeline_payload)
    assert res.status_code == 200, f"Pipeline failed: {res.text}"
    body = res.json()
    assert body.get("status") == "success"
    result = body.get("result", {})

    # Assert outputs from key stages are present in the unified pipeline output
    assert "image_b64" in result
    assert "segments" in result
    assert "graph_id" in result
    assert "blocked_edges" in result
    assert "safe_path" in result
    assert "traffic_map" in result
    assert "assigned_unit" in result
    assert "assigned_volunteer" in result
    assert "rf_alert" in result
    assert "channels_sent" in result
    assert "pdf_filename" in result
