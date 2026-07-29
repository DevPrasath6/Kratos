from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseAgent(ABC):
    name: str
    purpose: str = "Automated disaster response agent component."

    def __init__(self, name: str | None = None, purpose: str | None = None):
        if name:
            self.name = name
        if purpose:
            self.purpose = purpose

    @abstractmethod
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run the agent logic given input parameters."""
        pass

