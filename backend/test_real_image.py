import asyncio
import base64
import sys
import json
from pathlib import Path

# Add backend to sys.path
sys.path.insert(0, str(Path(__file__).parent))

from main import orchestrator

async def run_real_test(image_filename="7004_sat.jpg"):
    image_path = Path(image_filename)
    if not image_path.is_absolute():
        # Try to find it relative to current dir or fallback to data/dataset/train
        if not image_path.exists():
            image_path = Path(__file__).parent.parent.parent / "data" / "dataset" / "train" / image_filename
    
    if not image_path.exists():
        print(f"[ERROR] Image not found at: {image_path.absolute()}")
        return

    print(f"Loading image from: {image_path.absolute()}")
    with open(image_path, "rb") as f:
        image_b64 = base64.b64encode(f.read()).decode("utf-8")

    # DO NOT include 'use_sample': True so the AI model runs
    payload = {
        "image_b64": image_b64,
        "disaster_type": "flood",
        "severity": 4
    }

    print("Running pipeline with real image data (AI models activated)...")
    
    # We will run the most critical path of the pipeline
    pipeline = [
        "image_ingestion",
        "road_extraction",
        "road_graph",
        "disaster_simulation",
        "route_planning",
        "infrastructure_risk"
    ]
    
    try:
        res = await orchestrator.run_pipeline(pipeline, payload)
        print("\n=== PIPELINE EXECUTION SUCCESS ===")
        print(f"Graph ID generated: {res.get('graph_id')}")
        print(f"Number of road segments detected: {len(res.get('segments', []))}")
        print(f"Safest route nodes: {res.get('safe_path')}")
        
        if 'infrastructure_evaluations' in res:
            print("\nReal Infrastructure Evaluations (based on detected nodes):")
            print(json.dumps(res['infrastructure_evaluations'], indent=2))
        else:
            print("\nNo critical infrastructure was detected near the extracted roads.")
            
    except Exception as e:
        print(f"\n[ERROR] Pipeline failed: {e}")

if __name__ == "__main__":
    # You can pass a different filename as a command-line argument
    img_name = sys.argv[1] if len(sys.argv) > 1 else "7004_sat.jpg"
    asyncio.run(run_real_test(img_name))
