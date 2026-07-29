from datetime import datetime, timezone
import time
import asyncio
from typing import Any, Dict, List, Optional, Set, Callable
from agents.base import BaseAgent


AGENT_ALIASES = {
    "disaster_sim": "disaster_simulation",
    "volunteer_dispatch": "volunteer_healthcare_dispatch",
    "radio_alert": "radio_frequency_alert",
}


class AgentOrchestrator:
    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}
        self._status: Dict[str, Dict[str, Any]] = {}
        self._listeners: Set[Callable[[Dict[str, Any]], None]] = set()

    def register_agent(self, agent: BaseAgent) -> None:
        self._agents[agent.name] = agent
        purpose = getattr(agent, "purpose", f"{agent.name} agent component.")
        if agent.name not in self._status:
            self._status[agent.name] = {
                "name": agent.name,
                "purpose": purpose,
                "status": "idle",
                "last_run_status": "never_run",
                "last_run_timestamp": None,
                "last_duration_ms": None,
                "last_error": None,
            }

    def resolve_name(self, name: str) -> str:
        return AGENT_ALIASES.get(name, name)

    def get_agent(self, name: str) -> Optional[BaseAgent]:
        resolved = self.resolve_name(name)
        return self._agents.get(resolved)

    def add_listener(self, listener: Callable[[Dict[str, Any]], None]) -> None:
        self._listeners.add(listener)

    def remove_listener(self, listener: Callable[[Dict[str, Any]], None]) -> None:
        self._listeners.discard(listener)

    def _broadcast_event(self, event: Dict[str, Any]) -> None:
        for listener in list(self._listeners):
            try:
                if asyncio.iscoroutinefunction(listener):
                    asyncio.create_task(listener(event))
                else:
                    listener(event)
            except Exception:
                pass

    async def run_agent(self, name: str, input_data: Dict[str, Any], next_agent: Optional[str] = None) -> Dict[str, Any]:
        resolved = self.resolve_name(name)
        agent = self.get_agent(resolved)
        if not agent:
            raise KeyError(f"Agent '{name}' (resolved: '{resolved}') not found.")

        start_time = time.time()
        purpose = getattr(agent, "purpose", f"{resolved} agent component.")

        # Update status to running/busy
        self._status[resolved]["status"] = "busy"
        self._status[resolved]["purpose"] = purpose

        start_event = {
            "type": "agent_start",
            "agent": resolved,
            "original_name": name,
            "status": "busy",
            "step_description": f"Executing {resolved} agent processing...",
            "next_agent": next_agent,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self._broadcast_event(start_event)

        try:
            result = await agent.run(input_data)
            duration_ms = round((time.time() - start_time) * 1000, 2)
            timestamp = datetime.now(timezone.utc).isoformat()

            self._status[resolved].update({
                "name": resolved,
                "purpose": purpose,
                "status": "idle",
                "last_run_status": "success",
                "last_run_timestamp": timestamp,
                "last_duration_ms": duration_ms,
                "last_error": None,
            })

            end_event = {
                "type": "agent_finish",
                "agent": resolved,
                "original_name": name,
                "status": "idle",
                "step_description": f"Completed {resolved} in {duration_ms}ms.",
                "next_agent": next_agent,
                "timestamp": timestamp,
                "duration_ms": duration_ms,
            }
            self._broadcast_event(end_event)

            # Log to SQLite Audit Database
            try:
                from agents.audit_store import audit_store
                audit_store.log_event(resolved, input_data, result, duration_ms)
            except Exception:
                pass

            return result

        except Exception as e:
            duration_ms = round((time.time() - start_time) * 1000, 2)
            timestamp = datetime.now(timezone.utc).isoformat()

            self._status[resolved].update({
                "name": resolved,
                "purpose": purpose,
                "status": "error",
                "last_run_status": "failed",
                "last_run_timestamp": timestamp,
                "last_duration_ms": duration_ms,
                "last_error": str(e),
            })

            error_event = {
                "type": "agent_error",
                "agent": resolved,
                "original_name": name,
                "status": "error",
                "step_description": f"Error in {resolved}: {str(e)}",
                "next_agent": next_agent,
                "timestamp": timestamp,
                "error": str(e),
            }
            self._broadcast_event(error_event)

            try:
                from agents.audit_store import audit_store
                audit_store.log_event(resolved, input_data, {"error": str(e)}, duration_ms)
            except Exception:
                pass
            raise e

    async def run_pipeline(self, agent_names: List[str], input_data: Dict[str, Any]) -> Dict[str, Any]:
        current_input = input_data
        total_steps = len(agent_names)
        for idx, name in enumerate(agent_names):
            next_agent = agent_names[idx + 1] if idx + 1 < total_steps else None
            resolved_next = self.resolve_name(next_agent) if next_agent else None
            current_input = await self.run_agent(name, current_input, next_agent=resolved_next)
        return current_input

    def get_status(self) -> Dict[str, Dict[str, Any]]:
        return self._status
