import asyncio
from typing import Any, Dict
from agents.base import BaseAgent

class MedicalTriageAgent(BaseAgent):
    name: str = "medical_triage"

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prioritizes casualties and medical emergencies based on severity reports 
        and directs closest medical assets.
        """
        
        output = dict(input_data)
        from agents.nim_client import generate_agent_json
        
        fallback = {
            "critical_cases": 12,
            "moderate_cases": 34,
            "dispatched_units": ["MED-01", "MED-04"]
        }
        prompt = (
            f"You are the medical_triage agent. Purpose: Prioritizes casualties and medical emergencies based on severity reports          and directs closest medical assets.\n"
            f"Given the following disaster context/input data: {input_data}\n"
            f"Generate a realistic, real-time JSON response. Your JSON MUST match this exact schema/keys: {fallback}"
        )
        
        result = await generate_agent_json(prompt, fallback)
        
        output["medical_triage"] = result
        return output
