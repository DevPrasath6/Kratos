import random\nimport asyncio
from typing import Any, Dict
from agents.base import BaseAgent

class ChemicalSpillAgent(BaseAgent):
    name: str = "chemical_spill"

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Models toxic plume dispersion in urban areas.
        """
        await asyncio.sleep(0.01)  # Simulate logic
        
        output = dict(input_data)
        output["chemical_spill"] = {
            "status": "completed",
            "toxic_plume_sq_km": round(random.uniform(0.5, 5.5), 1),
            "dispersion_rate": "Fast",
            "recommended_ppe": "Level A"
        }
        return output
