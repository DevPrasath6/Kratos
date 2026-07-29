from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from routes.agents import router as agents_router, orchestrator
import asyncio
import json
from typing import Set

app = FastAPI(title="KRATOS API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agents_router)

active_websockets: Set[WebSocket] = set()


async def broadcast_ws_message(event: dict):
    message = json.dumps(event)
    for ws in list(active_websockets):
        try:
            await ws.send_text(message)
        except Exception:
            active_websockets.discard(ws)


orchestrator.add_listener(broadcast_ws_message)


@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "KRATOS Autonomous Disaster Response Platform API",
        "health": "/api/health",
        "docs_url": "/docs",
        "agents_count": 22
    }


@app.get("/api/health")
async def health_check():
    return {"status": "ok"}


@app.post("/api/upload")
async def srs_upload(file=None):
    from routes.agents import upload_image
    return await upload_image(file=file)


@app.post("/api/segment")
async def srs_segment(payload: dict):
    from routes.agents import segment_image
    return await segment_image(payload)


@app.post("/api/graph")
async def srs_graph(payload: dict = None):
    from routes.agents import build_graph
    return await build_graph(payload)


@app.post("/api/simulate")
async def srs_simulate(payload: dict = None):
    from routes.agents import simulate_disaster
    return await simulate_disaster(payload)


@app.post("/api/route")
async def srs_route(payload: dict = None):
    from routes.agents import plan_route
    return await plan_route(payload)


@app.post("/api/resources")
async def srs_resources(payload: dict = None):
    from routes.agents import allocate_resource
    return await allocate_resource(payload)


@app.get("/api/report")
async def srs_report(incident_id: str = None):
    from routes.agents import generate_report
    return await generate_report(incident_id=incident_id)


@app.get("/api/dashboard")
async def srs_dashboard():
    from routes.agents import get_telemetry
    return await get_telemetry()


@app.websocket("/ws/agents")
async def websocket_agents(websocket: WebSocket):
    await websocket.accept()
    active_websockets.add(websocket)
    # Send current initial status snapshot upon connection
    initial_payload = {
        "type": "status_snapshot",
        "agents": orchestrator.get_status(),
    }
    await websocket.send_text(json.dumps(initial_payload))
    try:
        while True:
            # Keep connection open & receive potential client messages
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
    except WebSocketDisconnect:
        active_websockets.discard(websocket)
    except Exception:
        active_websockets.discard(websocket)


@app.websocket("/ws/status")
async def websocket_status(websocket: WebSocket):
    await websocket.accept()
    active_websockets.add(websocket)
    try:
        while True:
            status = orchestrator.get_status()
            await websocket.send_text(json.dumps(status))
            await asyncio.sleep(1.0)
    except WebSocketDisconnect:
        active_websockets.discard(websocket)
    except Exception:
        active_websockets.discard(websocket)
