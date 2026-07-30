import random\nimport asyncio
from typing import Any, Dict
from agents.base import BaseAgent

class EmergencyGeneratorAgent(BaseAgent):
    name: str = "emergency_generator"

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dispatches diesel generators to hospitals.
        """
        await asyncio.sleep(0.01)  # Simulate logic
        
        output = dict(input_data)
        output["emergency_generator"] = {
            "status": "completed",
            "generators_dispatched": random.randint(2, 20),
            "fuel_levels_pct": random.randint(20, 95),
            "hospitals_powered": random.randint(1, 5)
        }
        return output
