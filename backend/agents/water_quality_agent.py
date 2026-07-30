import asyncio
from typing import Any, Dict
from agents.base import BaseAgent

class WaterQualityAgent(BaseAgent):
    name: str = "water_quality"

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes contamination levels in floodwaters based on multispectral data 
        to warn against hazardous zones.
        """
        
        output = dict(input_data)
        from agents.nim_client import generate_agent_json
        
        fallback = {
            "contamination_detected": True,
            "hazardous_zones": ["Zone A", "Industrial Park B"],
            "risk_level": "High"
        }
        prompt = (
            f"You are the water_quality agent. Purpose: Analyzes contamination levels in floodwaters based on multispectral data          to warn against hazardous zones.\n"
            f"Given the following disaster context/input data: {input_data}\n"
            f"Generate a realistic, real-time JSON response. Your JSON MUST match this exact schema/keys: {fallback}"
        )
        
        result = await generate_agent_json(prompt, fallback)
        
        output["water_quality"] = result
        return output
