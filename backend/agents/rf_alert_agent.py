from datetime import datetime, timedelta, timezone
import uuid
from typing import Any, Dict
from agents.base import BaseAgent
from agents.nim_client import reasoning_client, NIM_API_KEY


# SIMULATION LAYER DISCLAIMER:
# Real IPAWS (Integrated Public Alert and Warning System) and Emergency Alert System (EAS) RF broadcasts
# require government-partner API keys, FCC certification, and licensed radio hardware infrastructure.
# This agent simulates the generation and formatting of standard IPAWS CAP (Common Alerting Protocol) JSON payloads.


class RadioFrequencyAlertAgent(BaseAgent):
    name: str = "radio_frequency_alert"

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Input:
        - disaster_type: str (e.g. "flood", "earthquake")
        - severity: int (1-5)
        - safe_path: list (e.g. [0, 3, 6, 7, 8])
        - avoided_blocked_edges: list
        """
        disaster_type = input_data.get("disaster_type", "general emergency").upper()
        severity_num = int(input_data.get("severity", 3))

        severity_label = "EXTREME" if severity_num >= 4 else "MODERATE" if severity_num >= 3 else "MINOR"
        headline = f"GOVERNMENT EMERGENCY ALERT: {severity_label} {disaster_type} WARNING"

        safe_path = input_data.get("safe_path", [])
        blocked_edges = input_data.get("avoided_blocked_edges", [])

        if safe_path:
            route_str = f"Evacuate via designated Safe Route {safe_path}."
        else:
            route_str = "Stay indoors and await further rescue instructions."

        avoid_str = f" Avoid {len(blocked_edges)} damaged/flooded road segment(s)." if blocked_edges else ""
        description = f"{headline}. {route_str}{avoid_str} Do not attempt to cross submerged roads."

        # NIM reasoning integration for radio alert optimization
        if NIM_API_KEY and reasoning_client:
            try:
                prompt = (
                    f"Create an emergency broadcast radio script for a {severity_label} {disaster_type} alert. "
                    f"Safe route: {safe_path}. Blocked segments: {blocked_edges}. Keep under 3 sentences."
                )
                res = reasoning_client.invoke([{"role": "user", "content": prompt}])
                content = res.content if isinstance(res.content, str) else str(res.content)
                if content.strip():
                    description = content.strip()
            except Exception:
                pass  # Fallback to string template description


        alert_id = f"rf_alert_{uuid.uuid4().hex[:8]}"
        now = datetime.now(timezone.utc)
        expires = now + timedelta(hours=4)

        alert_payload = {
            "alert_id": alert_id,
            "identifier": f"US-EAS-{alert_id}",
            "sender": "KRATOS-EMERGENCY-MANAGEMENT-SYSTEM",
            "sent_timestamp": now.isoformat(),
            "expires_timestamp": expires.isoformat(),
            "status": "Actual",
            "msg_type": "Alert",
            "scope": "Public",
            "headline": headline,
            "severity": severity_label,
            "broadcast_frequency_mhz": 162.550,  # NOAA Weather / Emergency Alert FM Frequency
            "safe_route_description": description,
            "simulation_note": (
                "SIMULATED BROADCAST LAYER - Live RF/IPAWS transmission requires government API credentials and FCC licensing."
            ),
        }

        output = dict(input_data)  # Preserve pipeline chain
        output.update({
            "rf_alert": alert_payload,
            "broadcast_status": "simulated_broadcast_success",
        })
        return output
