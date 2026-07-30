# Road Graph

**Agent ID:** `road_graph`
**Source File:** `backend/agents/road_graph_agent.py`

## Core Purpose
Automated disaster response agent component.

## Data Flow & I/O Schema
The following defines the input parameters expected and output values returned by this agent in the pipeline flow.
```text
Input options:
- { "use_sample": True }
- { "segments": [[x1, y1, x2, y2], ...], "tolerance": 15.0 }

Output:
GeoJSON-like dict representation of the graph + graph_id.
```

