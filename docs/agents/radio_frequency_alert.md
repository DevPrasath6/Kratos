# Radio Frequency Alert

**Agent ID:** `radio_frequency_alert`
**Source File:** `backend/agents/rf_alert_agent.py`

## Core Purpose
Automated disaster response agent component.

## Data Flow & I/O Schema
The following defines the input parameters expected and output values returned by this agent in the pipeline flow.
```text
Input:
- disaster_type: str (e.g. "flood", "earthquake")
- severity: int (1-5)
- safe_path: list (e.g. [0, 3, 6, 7, 8])
- avoided_blocked_edges: list
```

