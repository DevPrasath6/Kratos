import pytest
from fastapi.testclient import TestClient
from agents.road_graph_agent import RoadGraphAgent
from agents.disaster_simulation_agent import DisasterSimulationAgent
from agents.route_planning_agent import RoutePlanningAgent
from agents.traffic_analysis_agent import TrafficAnalysisAgent
from main import app


@pytest.mark.asyncio
async def test_route_planning_before_and_after_disaster():
    road_agent = RoadGraphAgent()
    G, graph_id = road_agent.sample_graph()

    route_agent = RoutePlanningAgent()

    # Before disaster: shortest and safe path should match
    res_before = await route_agent.run({"graph_id": graph_id, "source": 0, "destination": 8})
    assert res_before["route_found"] is True
    assert res_before["shortest_path"] == res_before["safe_path"]

    # Apply flood disaster around middle node (4, 4) -> blocks edges like (1,4), (3,4), (4,5), (4,7), (4,8)
    sim_agent = DisasterSimulationAgent()
    await sim_agent.run({
        "graph_id": graph_id,
        "disaster_type": "flood",
        "severity": 4,
        "center": [100.0, 100.0],
        "radius": 50.0,
    })

    # After disaster: safe path should reroute around blocked edges
    res_after = await route_agent.run({"graph_id": graph_id, "source": 0, "destination": 8})
    assert res_after["route_found"] is True
    assert res_after["safe_path"] != res_after["shortest_path"]
    assert len(res_after["avoided_blocked_edges"]) > 0


@pytest.mark.asyncio
async def test_traffic_analysis_agent():
    traffic_agent = TrafficAnalysisAgent()
    res = await traffic_agent.run({"use_sample": True, "seed": 123})

    assert "traffic_map" in res
    assert len(res["traffic_map"]) > 0
    assert 0.0 <= res["average_congestion"] <= 1.0


def test_api_full_pipeline_run():
    client = TestClient(app)

    payload = {
        "use_sample": True,
        "disaster_type": "flood",
        "severity": 4,
        "source": 0,
        "destination": 8,
    }

    resp = client.post("/api/agents/pipeline/run", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert "road_graph" in data["pipeline"]
    assert "route_planning" in data["pipeline"]

    res = data["result"]
    assert isinstance(res, dict)
