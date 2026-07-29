import pytest
from fastapi.testclient import TestClient
from agents.road_graph_agent import RoadGraphAgent
from agents.resource_allocation_agent import ResourceAllocationAgent
from agents.volunteer_dispatch_agent import VolunteerHealthcareDispatchAgent
from main import app


@pytest.mark.asyncio
async def test_resource_allocation_skips_busy_unit():
    road_agent = RoadGraphAgent()
    G, graph_id = road_agent.sample_graph()

    # Unit 1 is closer (Node 0) but BUSY.
    # Unit 2 is further (Node 2) and AVAILABLE.
    # Incident is at Node 8.
    units = [
        {"id": "amb_01", "name": "Ambulance 1", "type": "medical", "location_node": 0, "status": "busy"},
        {"id": "amb_02", "name": "Ambulance 2", "type": "medical", "location_node": 2, "status": "available"},
    ]

    alloc_agent = ResourceAllocationAgent()
    res = await alloc_agent.run({
        "graph_id": graph_id,
        "incident_node": 8,
        "incident_type": "medical",
        "units": units,
    })

    assert res["allocation_status"] == "assigned"
    # Must assign Ambulance 2, skipping Ambulance 1 because it's busy
    assert res["assigned_unit"]["id"] == "amb_02"


@pytest.mark.asyncio
async def test_volunteer_dispatch_instructions():
    road_agent = RoadGraphAgent()
    G, graph_id = road_agent.sample_graph()

    dispatch_agent = VolunteerHealthcareDispatchAgent()
    res = await dispatch_agent.run({
        "graph_id": graph_id,
        "incident_node": 8,
    })

    assert res["dispatch_status"] == "dispatched"
    assert res["assigned_volunteer"] is not None
    assert "DISPATCH ORDER" in res["instructions"]
    assert "ETA:" in res["instructions"]


def test_api_resource_and_volunteer_endpoints():
    client = TestClient(app)

    # Initialize graph first
    graph_resp = client.post("/api/agents/graph", json={"use_sample": True})
    graph_id = graph_resp.json()["result"]["graph_id"]

    # Test Resource Allocate endpoint
    alloc_resp = client.post(
        "/api/agents/resource/allocate",
        json={"graph_id": graph_id, "incident_node": 8, "incident_type": "medical"}
    )
    assert alloc_resp.status_code == 200
    alloc_data = alloc_resp.json()
    assert alloc_data["status"] == "success"
    assert alloc_data["result"]["allocation_status"] == "assigned"

    # Test Volunteer Dispatch endpoint
    vol_resp = client.post(
        "/api/agents/volunteer/dispatch",
        json={"graph_id": graph_id, "incident_node": 8}
    )
    assert vol_resp.status_code == 200
    vol_data = vol_resp.json()
    assert vol_data["status"] == "success"
    assert vol_data["result"]["dispatch_status"] == "dispatched"
