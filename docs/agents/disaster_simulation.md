# Disaster Simulation

**Agent ID:** `disaster_simulation`
**Source File:** `backend/agents/disaster_simulation_agent.py`

## Core Purpose
Automated disaster response agent component.

## Data Flow & I/O Schema
The following defines the input parameters expected and output values returned by this agent in the pipeline flow.
```text
Input:
- graph_id: str (default: "sample_graph_default")
- disaster_type: "flood" | "earthquake" | "cyclone" | "landslide" | "wildfire"
- severity: 1 to 5 (default 3)
- center: [x, y] (optional, defaults to graph center)
- radius: float (optional, defaults to 120.0)
```

