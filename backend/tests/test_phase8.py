import pytest
from pathlib import Path
from fastapi.testclient import TestClient
from agents.report_generation_agent import ReportGenerationAgent, REPORTS_DIR
from agents.audit_agent import AuditAgent
from agents.audit_store import audit_store
from main import app


@pytest.mark.asyncio
async def test_report_generation_agent_summary_and_pdf():
    agent = ReportGenerationAgent()
    res = await agent.run({
        "incident_id": "test_inc_123",
        "disaster_type": "flood",
        "severity": 4,
        "avoided_blocked_edges": [[1, 4]],
        "safe_path": [0, 3, 6, 7, 8],
        "safe_eta": 5.2,
    })

    assert res["incident_id"] == "test_inc_123"
    assert "EXECUTIVE SUMMARY" in res["report_summary"] or "incident report" in res["report_summary"]
    assert res["pdf_filename"] == "report_test_inc_123.pdf"

    pdf_file = REPORTS_DIR / "report_test_inc_123.pdf"
    assert pdf_file.exists()
    assert pdf_file.stat().st_size > 0


@pytest.mark.asyncio
async def test_audit_store_logging():
    audit_store.clear_logs()

    # Log two sample events
    audit_store.log_event("ping", {"msg": "hello"}, {"echo": {"msg": "hello"}}, 1.5)
    audit_store.log_event("road_graph", {"use_sample": True}, {"node_count": 9}, 12.3)

    logs = audit_store.get_logs()
    assert len(logs) == 2
    assert logs[0]["agent_name"] == "ping"
    assert logs[1]["agent_name"] == "road_graph"
    assert logs[0]["duration_ms"] == 1.5


def test_api_report_and_logs_endpoints():
    client = TestClient(app)

    # 1. Test GET /api/agents/report
    report_resp = client.get("/api/agents/report?incident_id=test_api_inc_999")
    assert report_resp.status_code == 200
    report_data = report_resp.json()
    assert report_data["status"] == "success"
    assert report_data["result"]["incident_id"] == "test_api_inc_999"

    # 2. Test GET /api/agents/reports/download/test_api_inc_999
    download_resp = client.get("/api/agents/reports/download/test_api_inc_999")
    assert download_resp.status_code == 200
    assert download_resp.headers["content-type"] == "application/pdf"

    # 3. Test GET /api/agents/logs
    logs_resp = client.get("/api/agents/logs")
    assert logs_resp.status_code == 200
    logs_data = logs_resp.json()
    assert logs_data["status"] == "success"
    assert logs_data["count"] > 0
    assert isinstance(logs_data["logs"], list)
