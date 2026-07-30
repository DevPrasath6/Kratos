# Volunteer Healthcare Dispatch

**Agent ID:** `volunteer_healthcare_dispatch`
**Source File:** `backend/agents/volunteer_dispatch_agent.py`

## Core Purpose
Automated disaster response agent component.

## Data Flow & I/O Schema
The following defines the input parameters expected and output values returned by this agent in the pipeline flow.
```text
Input:
- graph_id: str
- incident_node: int (default 8)
- volunteers: list of volunteer dicts (optional)
```

