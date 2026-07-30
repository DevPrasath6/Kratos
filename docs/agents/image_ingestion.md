# Image Ingestion

**Agent ID:** `image_ingestion`
**Source File:** `backend/agents/image_ingestion_agent.py`

## Core Purpose
Automated disaster response agent component.

## Data Flow & I/O Schema
The following defines the input parameters expected and output values returned by this agent in the pipeline flow.
```text
Expects input_data containing either:
- "image_bytes": raw bytes of PNG/JPEG, or
- "image_b64": base64 encoded string of PNG/JPEG.
Validates the format, resizes if larger than max_dim (default 1024), and returns base64.
```

