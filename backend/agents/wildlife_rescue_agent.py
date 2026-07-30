import asyncio
from typing import Any, Dict
from agents.base import BaseAgent

class WildlifeRescueAgent(BaseAgent):
    name: str = "wildlife_rescue"

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tracks displaced local wildlife and coordinates with animal 
        control and rescue organizations.
        """
        
        output = dict(input_data)
        from agents.nim_client import generate_agent_json
        
        fallback = {
            "displaced_animals_estimated": 150,
            "rescue_teams_deployed": 2,
            "safe_habitats_secured": 1
        }
        prompt = (
            f"You are the wildlife_rescue agent. Purpose: Tracks displaced local wildlife and coordinates with animal          control and rescue organizations.\n"
            f"Given the following disaster context/input data: {input_data}\n"
            f"Generate a realistic, real-time JSON response. Your JSON MUST match this exact schema/keys: {fallback}"
        )
        
        result = await generate_agent_json(prompt, fallback)
        
        output["wildlife_rescue"] = result
        return output
