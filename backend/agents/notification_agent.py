from datetime import datetime, timezone
import uuid
from typing import Any, Dict
from agents.base import BaseAgent


class NotificationAgent(BaseAgent):
    name: str = "notification"

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Input:
        - rf_alert: dict (optional alert payload from RadioFrequencyAlertAgent)
        - instructions: str (optional dispatch instruction string)
        """
        rf_alert = input_data.get("rf_alert", {})
        headline = rf_alert.get("headline", "KRATOS EMERGENCY ALERT")
        body = rf_alert.get("safe_route_description", input_data.get("instructions", "Emergency evacuation advisory in effect."))

        notif_id = f"notif_{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc)

        # Mock multi-channel dispatch
        channels_sent = {
            "sms": {
                "sent": True,
                "recipients_count": 250,
                "sample_text": f"[SMS ALERT] {headline}: {body[:100]}...",
            },
            "email": {
                "sent": True,
                "recipients_count": 85,
                "subject": headline,
                "sample_preview": body,
            },
            "dashboard_push": {
                "sent": True,
                "active_banner": True,
                "banner_text": headline,
            },
        }

        output = dict(input_data)  # Preserve pipeline chain
        output.update({
            "notification_id": notif_id,
            "timestamp": now.isoformat(),
            "channels_sent": channels_sent,
            "notification_status": "delivered_all_channels",
        })
        return output
