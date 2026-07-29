from typing import Any, Dict
from agents.base import BaseAgent
from agents.audit_store import audit_store


class AuditAgent(BaseAgent):
    name: str = "audit"

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Input:
        - limit: int (optional, default 100)
        """
        limit = int(input_data.get("limit", 100))
        logs = audit_store.get_logs(limit=limit)

        output = dict(input_data)
        output.update({
            "total_logs": len(logs),
            "logs": logs,
        })
        return output
