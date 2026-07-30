import asyncio
from typing import Any, Dict
from agents.base import BaseAgent

class EvacuationTransportAgent(BaseAgent):
    name: str = "evacuation_transport"

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coordinates autonomous evacuation transports (buses, boats, high-clearance vehicles) 
        to active safe zones and designated pick-up points.
        """
        await asyncio.sleep(0.01)  # Simulate logic
        
        safe_path = input_data.get("safe_path", [])
        disaster_type = input_data.get("disaster_type", "Flood").lower()
        
        transport_type = "Autonomous Amphibious Transport" if "flood" in disaster_type or "tsunami" in disaster_type else "Self-Driving Evacuation Bus"
        
        assigned_transports = [
            {"id": "EVAC-01", "type": transport_type, "capacity": 45, "status": "Dispatched", "eta_min": 12},
            {"id": "EVAC-02", "type": transport_type, "capacity": 45, "status": "Dispatched", "eta_min": 18}
        ]

        output = dict(input_data)
        output["evacuation_transport"] = {
            "assigned_transports": assigned_transports,
            "total_capacity": 90,
            "rendezvous_node": safe_path[-1] if safe_path else None
        }
        return output
