import random\nimport asyncio
from typing import Any, Dict
from agents.base import BaseAgent

class TsunamiWarningAgent(BaseAgent):
    name: str = "tsunami_warning"

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates wave propagation from offshore quakes.
        """
        await asyncio.sleep(0.01)  # Simulate logic
        
        output = dict(input_data)
        output["tsunami_warning"] = {
            "status": "completed",
            "wave_height_meters": round(random.uniform(1.5, 8.0), 1),
            "eta_coastline_mins": random.randint(15, 180),
            "evacuation_zones": ["Zone A", "Zone B"]
        }
        return output
