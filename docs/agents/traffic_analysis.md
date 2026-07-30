# Traffic Analysis

**Agent ID:** `traffic_analysis`
**Source File:** `backend/agents/traffic_analysis_agent.py`

## Core Purpose
Automated disaster response agent component.

## Data Flow & I/O Schema
The following defines the input parameters expected and output values returned by this agent in the pipeline flow.
```text
Input:
- graph_id: str
- assigned_vehicles: dict/list (optional vehicle density updates)
- seed: int (default 42)
```

