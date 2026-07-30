import asyncio
from typing import Any, Dict
from agents.base import BaseAgent

class PublicRelationsAgent(BaseAgent):
    name: str = "public_relations"

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Drafts automated public safety broadcasts and press releases 
        based on real-time incident data.
        """
        
        output = dict(input_data)
        from agents.nim_client import generate_agent_json
        
        fallback = {
            "broadcasts_issued": 3,
            "media_briefings_prepared": 1,
            "sentiment_analysis": "Anxious but informed"
        }
        prompt = (
            f"You are the public_relations agent. Purpose: Drafts automated public safety broadcasts and press releases          based on real-time incident data.\n"
            f"Given the following disaster context/input data: {input_data}\n"
            f"Generate a realistic, real-time JSON response. Your JSON MUST match this exact schema/keys: {fallback}"
        )
        
        result = await generate_agent_json(prompt, fallback)
        
        output["public_relations"] = result
        return output
