import pytest
from fastapi.testclient import TestClient
from agents.road_graph_agent import RoadGraphAgent
from agents.disaster_simulation_agent import DisasterSimulationAgent
from agents.graph_store import graph_store
from main import app


@pytest.mark.asyncio
async def test_disaster_simulation_determinism():
    road_agent = RoadGraphAgent()
    G, graph_id = road_agent.sample_graph()

    sim_agent = DisasterSimulationAgent()
    params = {
        "graph_id": graph_id,
        "disaster_type": "flood",
        "severity": 4,
        "center": [100.0, 100.0],
        "radius": 120.0,
    }

    res1 = await sim_agent.run(params)
    res2 = await sim_agent.run(params)

    assert res1["blocked_edges"] == res2["blocked_edges"]
    assert res1["degraded_edges"] == res2["degraded_edges"]
    assert res1["affected_edge_count"] == res2["affected_edge_count"]
    assert len(res1["blocked_edges"]) > 0


@pytest.mark.asyncio
async def test_flood_blocks_subset_of_sample_graph():
    road_agent = RoadGraphAgent()
    G, graph_id = road_agent.sample_graph()

    sim_agent = DisasterSimulationAgent()
    res = await sim_agent.run({
        "graph_id": graph_id,
        "disaster_type": "flood",
        "severity": 5,
        "center": [50.0, 50.0],
        "radius": 80.0,
    })

    assert res["disaster_type"] == "flood"
    assert res["severity"] == 5
    # Must block a subset of edges, not all
    total_edges = len(G.edges())
    blocked_count = len(res["blocked_edges"])
    assert 0 < blocked_count < total_edges

    # Check updated graph state in graph_store
    stored_G = graph_store.get_graph(graph_id)
    blocked_in_graph = [ (u, v) for u, v, d in stored_G.edges(data=True) if d.get("blocked") ]
    assert len(blocked_in_graph) == blocked_count


def test_api_disaster_simulate():
    client = TestClient(app)

    # Initialize graph first
    graph_resp = client.post("/api/agents/graph", json={"use_sample": True})
    assert graph_resp.status_code == 200
    graph_id = graph_resp.json()["result"]["graph_id"]

    # Trigger disaster simulation via endpoint
    sim_resp = client.post(
        "/api/agents/disaster/simulate",
        json={
            "graph_id": graph_id,
            "disaster_type": "flood",
            "severity": 4,
            "center": [100.0, 100.0],
            "radius": 120.0,
        }
    )
    assert sim_resp.status_code == 200
    data = sim_resp.json()
    assert data["status"] == "success"
    assert data["result"]["graph_id"] == graph_id
    assert len(data["result"]["blocked_edges"]) > 0
