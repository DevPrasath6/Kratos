import random\nimport asyncio
from typing import Any, Dict
from agents.base import BaseAgent

class FirePropagationAgent(BaseAgent):
    name: str = "fire_propagation"

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Simulates fire spread based on wind and terrain.
        """
        await asyncio.sleep(0.01)  # Simulate logic
        
        output = dict(input_data)
        output["fire_propagation"] = {
            "status": "completed",
            "burn_radius_km": round(random.uniform(2.5, 12.0), 2),
            "containment_percentage": random.randint(10, 85),
            "wind_factor_multiplier": round(random.uniform(1.1, 2.5), 2)
        }
        return output
