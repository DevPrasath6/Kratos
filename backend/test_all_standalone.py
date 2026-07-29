import asyncio
import sys
from pathlib import Path

# Add backend to sys.path
sys.path.insert(0, str(Path(__file__).parent))

from main import orchestrator

ALL_22_AGENTS = [
    "ping",
    "image_ingestion",
    "road_extraction",
    "road_graph",
    "disaster_simulation",
    "route_planning",
    "traffic_analysis",
    "resource_allocation",
    "volunteer_healthcare_dispatch",
    "radio_frequency_alert",
    "notification",
    "report_generation",
    "audit",
    "drone_swarm_orchestrator",
    "predictive_micro_climate",
    "social_media_distress",
    "autonomous_satellite_tasking",
    "telecom_mesh",
    "shelter_capacity",
    "infrastructure_risk",
    "damage_verification",
    "supply_logistics",
]

async def test_standalone():
    print(f"Testing {len(ALL_22_AGENTS)} agents in standalone mode...")
    passed = 0
    failed = []

    for name in ALL_22_AGENTS:
        try:
            res = await orchestrator.run_agent(name, {"use_sample": True, "disaster_type": "flood", "severity": 4})
            print(f"  [PASS] {name}: keys -> {list(res.keys())[:4]}")
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {name}: {e}")
            failed.append((name, str(e)))

    print(f"\nResult: {passed}/{len(ALL_22_AGENTS)} passed.")
    if failed:
        print(f"Failed agents: {failed}")

if __name__ == "__main__":
    asyncio.run(test_standalone())
