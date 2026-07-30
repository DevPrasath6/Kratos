# Notification

**Agent ID:** `notification`
**Source File:** `backend/agents/notification_agent.py`

## Core Purpose
Automated disaster response agent component.

## Data Flow & I/O Schema
The following defines the input parameters expected and output values returned by this agent in the pipeline flow.
```text
Input:
- rf_alert: dict (optional alert payload from RadioFrequencyAlertAgent)
- instructions: str (optional dispatch instruction string)
```

