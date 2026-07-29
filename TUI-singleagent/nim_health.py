import time
import httpx
from typing import Dict, Any

BACKEND_URL = "http://localhost:8000"


async def fetch_nim_health() -> Dict[str, Any]:
    """Pings backend /api/agents/nim/health and returns NIM endpoint telemetry."""
    async with httpx.AsyncClient(timeout=3.0) as client:
        try:
            t0 = time.time()
            resp = await client.get(f"{BACKEND_URL}/api/agents/nim/health")
            roundtrip_ms = round((time.time() - t0) * 1000, 2)

            if resp.status_code == 200:
                data = resp.json()
                data["roundtrip_ms"] = roundtrip_ms
                data["backend_online"] = True
                return data
        except Exception as e:
            pass

    return {
        "backend_online": False,
        "nim_api_key_present": False,
        "vlm_model": "nvidia/nemotron-nano-12b-v2-vl",
        "vlm_status": "offline",
        "vlm_latency_ms": -1.0,
        "reasoning_model": "nvidia/nemotron-3-super-120b-a12b",
        "reasoning_status": "offline",
        "reasoning_latency_ms": -1.0,
        "roundtrip_ms": -1.0,
    }
