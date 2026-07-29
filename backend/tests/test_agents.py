import pytest
from fastapi.testclient import TestClient
from agents.base import BaseAgent
from agents.ping_agent import PingAgent
from agents.orchestrator import AgentOrchestrator
from main import app


@pytest.mark.asyncio
async def test_ping_agent_direct():
    agent = PingAgent()
    res = await agent.run({"msg": "hello"})
    assert res == {"echo": {"msg": "hello"}}


@pytest.mark.asyncio
async def test_orchestrator_run():
    orchestrator = AgentOrchestrator()
    agent = PingAgent()
    orchestrator.register_agent(agent)

    res = await orchestrator.run_agent("ping", {"msg": "test"})
    assert res == {"echo": {"msg": "test"}}

    status = orchestrator.get_status()
    assert "ping" in status
    assert status["ping"]["last_run_status"] == "success"
    assert status["ping"]["last_run_timestamp"] is not None


@pytest.mark.asyncio
async def test_orchestrator_pipeline():
    class AppendAgent(BaseAgent):
        name = "append"
        async def run(self, input_data: dict) -> dict:
            return {"data": input_data.get("data", "") + "_appended"}

    orchestrator = AgentOrchestrator()
    orchestrator.register_agent(AppendAgent())
    orchestrator.register_agent(PingAgent())

    pipeline_res = await orchestrator.run_pipeline(["append", "ping"], {"data": "start"})
    assert pipeline_res == {"echo": {"data": "start_appended"}}


def test_api_ping_and_status():
    client = TestClient(app)

    # Health check
    health_resp = client.get("/api/health")
    assert health_resp.status_code == 200
    assert health_resp.json() == {"status": "ok"}

    # Run ping agent via API
    run_resp = client.post("/api/agents/ping/run", json={"msg": "hi"})
    assert run_resp.status_code == 200
    json_data = run_resp.json()
    assert json_data["status"] == "success"
    assert json_data["agent"] == "ping"
    assert json_data["result"] == {"echo": {"msg": "hi"}}

    # Get status via API
    status_resp = client.get("/api/agents/status")
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    assert "ping" in status_data
    assert status_data["ping"]["last_run_status"] == "success"
