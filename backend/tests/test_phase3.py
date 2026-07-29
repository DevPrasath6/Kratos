import pytest
from fastapi.testclient import TestClient
from agents.road_graph_agent import RoadGraphAgent
from main import app


@pytest.mark.asyncio
async def test_sample_graph_generation():
    agent = RoadGraphAgent()
    res = await agent.run({"use_sample": True})

    assert res["graph_id"] == "sample_graph_default"
    assert res["node_count"] == 9
    assert res["edge_count"] == 14
    assert len(res["nodes"]) == 9
    assert len(res["edges"]) == 14


@pytest.mark.asyncio
async def test_graph_snapping_from_segments():
    agent = RoadGraphAgent()
    # Segments that should snap together at near endpoints
    segments = [
        [0, 0, 100, 0],
        [102, 1, 102, 100],  # (102,1) should snap to (100,0) with tolerance=15
    ]
    res = await agent.run({"segments": segments, "tolerance": 15.0})

    assert "graph_id" in res
    assert res["node_count"] == 3  # (0,0), snapped (100,0), and (102,100)
    assert res["edge_count"] == 2


def test_api_graph_endpoints():
    client = TestClient(app)

    # Test POST /api/agents/graph with sample
    resp = client.post("/api/agents/graph", json={"use_sample": True})
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    graph_id = data["result"]["graph_id"]
    assert graph_id == "sample_graph_default"

    # Test GET /api/agents/graph/{graph_id}
    get_resp = client.get(f"/api/agents/graph/{graph_id}")
    assert get_resp.status_code == 200
    get_data = get_resp.json()
    assert get_data["status"] == "success"
    assert get_data["result"]["graph_id"] == graph_id
    assert get_data["result"]["node_count"] == 9
