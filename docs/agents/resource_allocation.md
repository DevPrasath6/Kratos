# Resource Allocation

**Agent ID:** `resource_allocation`
**Source File:** `backend/agents/resource_allocation_agent.py`

## Core Purpose
Automated disaster response agent component.

## Data Flow & I/O Schema
The following defines the input parameters expected and output values returned by this agent in the pipeline flow.
```text
Input:
- graph_id: str
- incident_node: int (default 8)
- incident_type: "medical" | "casualty" | "fire" | "security" | "general" (default "medical")
- units: list of unit dicts (optional)
```

