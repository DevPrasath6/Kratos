from typing import Any, Dict
from agents.base import BaseAgent


class PingAgent(BaseAgent):
    name: str = "ping"

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        return {"echo": input_data}
