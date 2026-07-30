# Road Extraction

**Agent ID:** `road_extraction`
**Source File:** `backend/agents/road_extraction_agent.py`

## Core Purpose
Automated disaster response agent component.

## Data Flow & I/O Schema
The following defines the input parameters expected and output values returned by this agent in the pipeline flow.
```text
Input: { "image_b64": "<base64_string>" }
Returns: {
    "segments": [[x1, y1, x2, y2], ...],
    "source": "nim_vlm" | "cv_fallback",
    "confidence": float
}
```

