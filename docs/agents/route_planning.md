# Route Planning

**Agent ID:** `route_planning`
**Source File:** `backend/agents/route_planning_agent.py`

## Core Purpose
Automated disaster response agent component.

## Data Flow & I/O Schema
The following defines the input parameters expected and output values returned by this agent in the pipeline flow.
```text
Input:
- graph_id: str
- source: int (node id, default 0)
- destination: int (node id, default 8)
- base_speed: float (speed unit per distance unit, default 1.0)
```

