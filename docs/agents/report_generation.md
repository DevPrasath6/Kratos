# Report Generation

**Agent ID:** `report_generation`
**Source File:** `backend/agents/report_generation_agent.py`

## Core Purpose
Automated disaster response agent component.

## Data Flow & I/O Schema
The following defines the input parameters expected and output values returned by this agent in the pipeline flow.
```text
Input: Accepts pipeline data or incident parameters.
Generates executive summary using NIM reasoning LLM (or string fallback) and PDF report.
```

