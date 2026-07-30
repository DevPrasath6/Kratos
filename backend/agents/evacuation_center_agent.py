import random\nimport asyncio
from typing import Any, Dict
from agents.base import BaseAgent

class EvacuationCenterAgent(BaseAgent):
    name: str = "evacuation_center"

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Manages staging areas for displaced populations.
        """
        await asyncio.sleep(0.01)  # Simulate logic
        
        output = dict(input_data)
        output["evacuation_center"] = {
            "status": "completed",
            "active_staging_areas": random.randint(3, 15),
            "total_displaced_processed": random.randint(500, 5000),
            "capacity_remaining_pct": random.randint(5, 45)
        }
        return output
