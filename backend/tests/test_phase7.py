import pytest
from fastapi.testclient import TestClient
from agents.rf_alert_agent import RadioFrequencyAlertAgent
from agents.notification_agent import NotificationAgent
from main import app


@pytest.mark.asyncio
async def test_rf_alert_payload_generation():
    agent = RadioFrequencyAlertAgent()
    res = await agent.run({
        "disaster_type": "flood",
        "severity": 4,
        "safe_path": [0, 3, 6, 7, 8],
        "avoided_blocked_edges": [[1, 4], [3, 4]],
    })

    assert res["broadcast_status"] == "simulated_broadcast_success"
    alert = res["rf_alert"]
    assert "EMERGENCY ALERT" in alert["headline"]
    assert alert["severity"] == "EXTREME"
    assert "Safe Route [0, 3, 6, 7, 8]" in alert["safe_route_description"]
    assert "SIMULATED BROADCAST" in alert["simulation_note"]


@pytest.mark.asyncio
async def test_notification_agent_channels():
    agent = NotificationAgent()
    res = await agent.run({
        "rf_alert": {
            "headline": "TEST ALERT",
            "safe_route_description": "Evacuate north.",
        }
    })

    assert res["notification_status"] == "delivered_all_channels"
    channels = res["channels_sent"]
    assert channels["sms"]["sent"] is True
    assert channels["email"]["sent"] is True
    assert channels["dashboard_push"]["sent"] is True


def test_api_rf_and_notification_endpoints():
    client = TestClient(app)

    # Test RF Alert endpoint
    rf_resp = client.post(
        "/api/agents/rf/alert",
        json={"disaster_type": "wildfire", "severity": 5, "safe_path": [0, 1, 2]}
    )
    assert rf_resp.status_code == 200
    rf_data = rf_resp.json()
    assert rf_data["status"] == "success"
    assert "rf_alert" in rf_data["result"]

    # Test Notification endpoint
    notif_resp = client.post(
        "/api/agents/notification/send",
        json={"rf_alert": rf_data["result"]["rf_alert"]}
    )
    assert notif_resp.status_code == 200
    notif_data = notif_resp.json()
    assert notif_data["status"] == "success"
    assert notif_data["result"]["notification_status"] == "delivered_all_channels"
