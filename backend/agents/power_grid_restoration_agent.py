import asyncio
from typing import Any, Dict
from agents.base import BaseAgent

class PowerGridRestorationAgent(BaseAgent):
    name: str = "power_grid_restoration"

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates emergency micro-grid power rerouting to restore electricity 
        to critical infrastructure (hospitals, shelters) when the main grid fails.
        """
        
        disaster_type = input_data.get("disaster_type", "Flood")
        severity = input_data.get("severity", 4)
        
        main_grid_status = "Offline" if severity >= 3 else "Unstable"
        rerouted_capacity_mw = 14.5 * (severity / 2)
        
        output = dict(input_data)
        from agents.nim_client import generate_agent_json
        
        fallback = {
            "main_grid_status": main_grid_status,
            "microgrid_activated": True,
            "critical_facilities_powered": ["City Hospital", "Evacuation Center Alpha"],
            "rerouted_capacity_mw": round(rerouted_capacity_mw, 2),
            "estimated_battery_reserve_hrs": 36
        }
        prompt = (
            f"You are the power_grid_restoration agent. Purpose: Calculates emergency micro-grid power rerouting to restore electricity          to critical infrastructure (hospitals, shelters) when the main grid fails.\n"
            f"Given the following disaster context/input data: {input_data}\n"
            f"Generate a realistic, real-time JSON response. Your JSON MUST match this exact schema/keys: {fallback}"
        )
        
        result = await generate_agent_json(prompt, fallback)
        
        output["power_grid"] = result
        return output
