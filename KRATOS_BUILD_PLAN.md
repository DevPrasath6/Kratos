# KRATOS Build Plan — Phase-by-Phase Prompts

**KRATOS** = Knowledge-driven Road Analysis for Terrain Occlusion & Security

This replaces the old multi-uvicorn / self-trained-model approach. Two servers only. NVIDIA NIM hosted endpoints instead of training your own segmentation model — that's almost certainly why the "deep earth dataset" training and route prediction failed: road segmentation from raw satellite imagery is a genuinely hard, data-hungry CV problem, not a hackathon-weekend problem. Route around it, don't fight it.

---

## 0. Architecture (final, simplified)

```
┌─────────────────────────┐        ┌──────────────────────────────────────┐
│   FRONTEND SERVER        │  HTTP  │   BACKEND + AI/ML AGENT SERVER        │
│   React + Vite (:5173)   │◄──────►│   FastAPI + Uvicorn (:8000)           │
│                          │  WS    │                                       │
│  - Dashboard (map/charts)│        │  AgentOrchestrator                    │
│  - React "TUI panel"     │        │   ├─ 1. Coordinator Agent             │
│    (styled like a        │        │   ├─ 2. Image Ingestion Agent         │
│    terminal, renders     │        │   ├─ 3. Road Extraction Agent (NIM)   │
│    live agent status)    │        │   ├─ 4. Road Graph Agent (NetworkX)   │
│  - ASCII banner on load  │        │   ├─ 5. Disaster Simulation Agent     │
└─────────────────────────┘        │   ├─ 6. Route Planning Agent          │
                                     │   ├─ 7. Traffic Analysis Agent        │
┌─────────────────────────┐        │   ├─ 8. Resource Allocation Agent     │
│  STANDALONE TERMINAL TUI │        │   ├─ 9. Volunteer/Healthcare Dispatch │
│  Python (Rich/Textual)   │◄──WS──►│   ├─ 10. Radio-Frequency Alert Agent  │
│  Runs against same       │        │   ├─ 11. Report Generation Agent      │
│  backend as the frontend │        │   ├─ 12. Notification Agent           │
└─────────────────────────┘        │   └─ 13. Audit/Logging Agent          │
                                     │                                       │
                                     │  SQLite (swap Postgres later)         │
                                     │  In-process dict cache (swap Redis)   │
                                     └──────────────────────────────────────┘
```

13 agents (comfortably clears your "minimum 12"). Every agent is:
- a plain Python class with one `run(input) -> output` method — testable standalone from a script or pytest, no server needed
- also registered on the Orchestrator so the API/TUI/React can call it live
- given its own `/api/agents/{name}/run` endpoint for the "test in isolation" requirement

Drop Postgres/Redis/SUMO/GeoTIFF for the hackathon build — SQLite + in-memory + OSM road data + simple physics-free disaster rules get you a working demo. Swap upward later if there's time (Future Scope, not Phase 1).

---

## 1. NVIDIA NIM — what replaces "train a segmentation model"

You do **not** need a custom-trained model. Use a hosted NIM vision/VLM endpoint (e.g. a segmentation or vision-language model on build.nvidia.com's free tier) for two jobs only:
1. **Road/obstruction description from satellite image** — ask the hosted VLM to identify visible roads, flooding, blockages as structured JSON (bounding regions or a text description), not pixel-perfect segmentation.
2. **Fallback with zero external dependency**: classical CV (OpenCV Canny edge detection + morphological thinning) to pull road-like lines from the image if the NIM call fails or the model doesn't return usable output. This fallback is what makes Phase 2 demoable even with no internet.

Never block the whole pipeline on perfect road extraction — downstream agents should work fine off a synthetic/mocked road graph if extraction confidence is low. This is the fix for "route prediction failed": route planning was probably starving because it depended on a road graph that never successfully got built. Decouple them (Phase 3 ships with a hardcoded sample graph so Phases 4–8 aren't blocked on Phase 2 ever working perfectly).

---

## 1a. NIM model choice + LangChain client config

Two free-tier NIM models, two different jobs — don't mix them up:

- **`nvidia/nemotron-nano-12b-v2-vl`** — vision-language model (the `vl` suffix). This is your *image-input* model. It belongs in **Road Extraction Agent** only.
- **`nvidia/nemotron-3-super-120b-a12b`** — large reasoning model (no vision, has a `reasoning_budget`/thinking mode). This is your *text-generation* model. It belongs in **Recommendation Agent**, **Report Generation Agent**, and **Radio-Frequency Alert Agent** (turning structured data into plain-language safe-route instructions).

Everything else in the pipeline (Road Graph, Disaster Simulation, Route Planning, Traffic Analysis, Resource Allocation, Volunteer Dispatch, Audit) is pure algorithmic logic — NetworkX/Dijkstra/rule tables. Don't route those through an LLM; it only adds latency, cost, and a new way to fail during a demo.

Shared client module, used via `langchain-nvidia-ai-endpoints` so both models go through one consistent interface:

```python
# backend/agents/nim_client.py
import os
from langchain_nvidia_ai_endpoints import ChatNVIDIA

NIM_API_KEY = os.environ.get("NIM_API_KEY")  # never hardcode this — env var only

# Vision model — used by RoadExtractionAgent to read satellite images
vision_client = ChatNVIDIA(
    model="nvidia/nemotron-nano-12b-v2-vl",
    api_key=NIM_API_KEY,
    temperature=0.2,        # low temp: consistent, factual reads of the image, not creativity
    top_p=0.9,
    max_completion_tokens=2048,
)

# Reasoning/text model — used by Recommendation, Report Generation, and Radio Alert agents
reasoning_client = ChatNVIDIA(
    model="nvidia/nemotron-3-super-120b-a12b",
    api_key=NIM_API_KEY,
    temperature=0.7,
    top_p=0.95,
    max_tokens=4096,
    reasoning_budget=4096,
    chat_template_kwargs={"enable_thinking": True},
)
```

Road Extraction Agent usage (image sent as a base64 data URL in the message content — NIM's multimodal message format):

```python
def analyze_satellite_image(image_b64: str) -> dict | None:
    if not NIM_API_KEY:
        return None  # triggers the OpenCV fallback from Phase 2
    try:
        response = vision_client.invoke([
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Identify visible road-like linear structures in this satellite image. Return approximate pixel line coordinates and a confidence score as JSON."},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_b64}"}},
                ],
            }
        ])
        return response.content
    except Exception:
        return None  # falls back to CV, per Phase 2 design — never let this raise unhandled
```

Report/Recommendation/Radio Alert agent usage (streaming; reasoning tokens kept separate from the final text):

```python
def generate_text_summary(prompt: str) -> str:
    result = ""
    for chunk in reasoning_client.stream([{"role": "user", "content": prompt}]):
        if chunk.additional_kwargs.get("reasoning_content"):
            pass  # optionally log/show as "agent thinking" in the TUI
        if chunk.content:
            result += chunk.content
    return result
```

**Free-tier caveat**: expect rate limits on both endpoints. Wrap every call in try/except with a fallback (CV fallback for vision, a template string for text) so a rate-limit hit mid-demo degrades gracefully instead of crashing the pipeline — this is the same "never hard-fail on the AI call" principle as the rest of this plan.

---

## 2. Phase Gate Rule

Do not start phase *N+1* until phase *N*'s tests pass. Each phase below has an exact prompt to hand to your coding assistant, plus a "Definition of Done" test checklist. If a phase's tests fail, stay on it — don't let a broken phase quietly become the next phase's dependency (that's what happened before).

---

### Phase 0 — Repo & Skeleton (no AI yet)

**Prompt:**
> Create a repo with two top-level folders: `backend/` (FastAPI + Uvicorn, Python 3.11) and `frontend/` (React + Vite + TypeScript + TailwindCSS). Backend has `main.py` exposing `GET /api/health` returning `{"status":"ok"}`. Frontend has a single page that fetches `/api/health` on load and displays the result. Add a root `README.md` with run instructions for both servers on two different ports. No agents yet — just prove the two servers talk to each other.

**Definition of Done:**
- [ ] `uvicorn main:app --reload` starts backend on :8000
- [ ] `npm run dev` starts frontend on :5173
- [ ] Frontend page shows "ok" fetched from backend (proves CORS is configured)

---

### Phase 1 — Agent Framework

**Prompt:**
> In `backend/agents/`, create a `BaseAgent` abstract class with `name: str` and `async def run(self, input: dict) -> dict`. Create an `AgentOrchestrator` class that registers agents in a dict by name and exposes `async def run_agent(name, input)` and `async def run_pipeline(agent_names: list, input)` (chains output of one into input of next). Expose two FastAPI routes: `POST /api/agents/{name}/run` (runs one agent standalone) and `GET /api/agents/status` (lists all registered agents and last-run status/timestamp, stored in a simple in-memory dict). Create one dummy agent `PingAgent` that just echoes its input, register it, and write a pytest test that calls it both directly and through the orchestrator.

**Definition of Done:**
- [ ] `pytest` passes for PingAgent (direct call + orchestrator call)
- [ ] `POST /api/agents/ping/run` with `{"msg":"hi"}` returns the echo via curl/Postman
- [ ] `GET /api/agents/status` shows PingAgent with a timestamp after it's run

---

### Phase 2 — Image Ingestion + Road Extraction Agent (NIM + CV fallback)

**Prompt:**
> Build `ImageIngestionAgent` (validates PNG/JPEG upload, resizes, returns base64) and `RoadExtractionAgent`. RoadExtractionAgent uses the `vision_client` (`langchain-nvidia-ai-endpoints` `ChatNVIDIA`, model `nvidia/nemotron-nano-12b-v2-vl`) from `backend/agents/nim_client.py` (see section 1a) to ask the hosted vision model to identify road-like linear structures in the image and return them as a list of approximate line segments (pixel coordinates) plus a confidence score. If the call fails, returns unusable output, or `NIM_API_KEY` is unset, fall back to OpenCV: grayscale → Canny edge detection → probabilistic Hough line transform → return the detected line segments with `source: "cv_fallback"` and `confidence: 0.5`. Never raise an unhandled exception — always return *some* line segment list. Add `POST /api/upload` and `POST /api/segment` routes. Write a test using a small synthetic test image (e.g. a PNG with a few straight white lines on black) and assert the fallback path returns non-empty line segments even with no API key set.

**Definition of Done:**
- [ ] Upload a real satellite PNG via the React page (simple file input is fine, doesn't need styling yet) → get back line segments + confidence
- [ ] Unset `NIM_API_KEY`, confirm fallback still returns usable line segments (this proves the demo never hard-fails on the AI call)
- [ ] Test passes on the synthetic image

---

### Phase 3 — Road Graph Agent

**Prompt:**
> Build `RoadGraphAgent` using NetworkX: takes the line segments from Phase 2 (or, independently, a hardcoded sample set of segments for testing without Phase 2), snaps nearby endpoints together into shared nodes, and builds an undirected weighted graph (weight = segment length) with intersections as nodes. Return the graph as GeoJSON-like `{nodes: [...], edges: [...]}` for the frontend to draw, and store the live NetworkX graph object in memory keyed by a `graph_id`. Include a hardcoded `sample_graph()` method returning a fixed small graph (8-10 nodes) so every later phase can be developed and demoed without depending on Phases 2 working.

**Definition of Done:**
- [ ] `POST /api/graph` with Phase 2's output produces a connected graph with reasonable node/edge counts
- [ ] `sample_graph()` works with zero upstream dependency — this is your safety net for the demo

---

### Phase 4 — Disaster Simulation Agent

**Prompt:**
> Build `DisasterSimulationAgent`. Input: `graph_id`, `disaster_type` (flood/earthquake/cyclone/landslide/wildfire), `severity` (1-5), and optionally a center point + radius. Apply simple rule-based effects on the graph: edges within radius get `blocked=True` (severity 4-5) or `speed_multiplier` reduced (severity 1-3), based on a small lookup table per disaster type (e.g. flood blocks low-lying edges harder than earthquake). Return an "impact map": which edges are blocked/degraded. No SUMO, no physics — a lookup-table simulation is enough and is easy to demo/explain.

**Definition of Done:**
- [ ] Running the same disaster twice with same params gives same result (deterministic)
- [ ] `sample_graph()` + a flood simulation visibly blocks a subset of edges

---

### Phase 5 — Route Planning + Traffic Analysis Agents

**Prompt:**
> Build `RoutePlanningAgent`: given source node, destination node, and the impacted graph from Phase 4, compute shortest path (Dijkstra) and a "safe path" that excludes blocked edges (A* with blocked edges removed/weight=infinity). Return distance, ETA (using edge speed_multiplier), and the blocked segments that were avoided. Build `TrafficAnalysisAgent`: a lightweight congestion estimate per edge (random-but-seeded density scaled by how many "vehicles" the Resource Allocation agent later assigns to that edge — for now, stub with a seeded pseudo-random congestion score per edge). Wire both into `run_pipeline(["road_graph","disaster_sim","route_planning","traffic_analysis"])`.

**Definition of Done:**
- [ ] Route request between two nodes on `sample_graph()` returns a real path both before and after a disaster is applied, and the safe path differs from the shortest path once edges are blocked
- [ ] Full pipeline runs end-to-end via one API call

---

### Phase 6 — Resource Allocation + Volunteer/Healthcare Dispatch Agents

**Prompt:**
> Build `ResourceAllocationAgent`: given a list of available units (ambulance/fire/police/medical team, each with a location node and status), and an incident location, assign the nearest available unit(s) by shortest safe-route distance from Phase 5, respecting a priority order (medical > fire > police for casualties). Build `VolunteerHealthcareDispatchAgent`: same idea but for a registered pool of volunteers/healthcare professionals (name, role, current location, availability) — matches them to nearby incidents using the same safe-route distance, and returns for each match: assigned person, incident, safe route to follow, ETA, and a plain-language instruction string (e.g. "Proceed via Route B, Route A is flooded near Node 7"). Keep the data model simple: an in-memory list of dicts is fine, no auth/registration UI needed yet.

**Definition of Done:**
- [ ] Given 3 sample units and 1 incident, the nearest available unit is assigned correctly (verify with a case where the geometrically-closer unit is unavailable and the second-closest gets picked)
- [ ] Volunteer dispatch returns a human-readable instruction string with the safe route baked in

---

### Phase 7 — Radio-Frequency Alert Agent + Notification Agent

**Prompt:**
> Build `RadioFrequencyAlertAgent`: simulates broadcasting a safe-route alert over a government emergency alert channel (model it as: given disaster impact + safe routes, generate a structured alert payload matching a plausible Emergency Alert System / IPAWS-style schema — headline, affected area, safe route description, expiry time — and log it as "broadcast" rather than actually transmitting anything; this is a simulation layer, be upfront in code comments that real RF/IPAWS integration needs a government-partner API key and licensing, out of scope for the hackathon). Build `NotificationAgent`: takes the same alert payload and "sends" it via mocked SMS/email (print/log, or use a free-tier email API if one is on hand) plus a dashboard alert entry. Both agents write their output into the audit log from Phase 8.

**Definition of Done:**
- [ ] Running a disaster simulation produces a radio-alert-shaped JSON payload with a safe-route description in plain language
- [ ] Notification agent's mocked send is visible in the API response / logs
- [ ] Code/README clearly states this is a simulated integration point, not a live government radio interface (protects you in Q&A/judging — this is a legitimate scope boundary, not a shortcut you need to hide)

---

### Phase 8 — Report Generation + Audit Agent

**Prompt:**
> Build `ReportGenerationAgent`: assembles a JSON + PDF incident report combining outputs from graph, simulation, routing, resource allocation, and alert agents (use a simple PDF library, e.g. reportlab). For the report's plain-language summary paragraph, use the `reasoning_client` (`langchain-nvidia-ai-endpoints` `ChatNVIDIA`, model `nvidia/nemotron-3-super-120b-a12b`) from `backend/agents/nim_client.py` (see section 1a) via the streaming `generate_text_summary()` helper; fall back to a plain string template (e.g. `f"{disaster_type} incident at {location}, {len(blocked_edges)} roads affected, {len(units_assigned)} units dispatched."`) if the call fails or `NIM_API_KEY` is unset. Build `AuditAgent`: every agent call anywhere in the orchestrator writes a log row (agent name, input hash, output summary, duration_ms, timestamp) to SQLite; expose `GET /api/logs`.

**Definition of Done:**
- [ ] `GET /api/report?incident_id=...` returns both a JSON summary and a downloadable PDF
- [ ] `GET /api/logs` shows every agent call made during a full pipeline run, in order, with timings

---

### Phase 9 — Standalone Terminal TUI

**Prompt:**
> Build a Python Textual (or Rich, if you want something lighter) TUI app in `tui/` that connects to the backend's `/api/agents/status` and a WebSocket for live updates. Layout should match this reference exactly in spirit — box-drawn panels, a header banner, agent checklist with ✓/✗/… status icons, an active-vehicles panel, and a current safe-route panel:
> ```
> ╔══════════════════════════════════════════╗
> ║               KRATOS                      ║
> ╠══════════════════════════════════════════╣
> ║ Disaster : Flood      Time: 15:20         ║
> ║ Status   : Running                        ║
> ╠══════════════════════════════════════════╣
> ║ Agent Status                              ║
> ║ ✓ Satellite   ✓ Road Detection             ║
> ║ ✓ Graph       ✓ Disaster Sim               ║
> ║ … Route Plan  … Resource Alloc             ║
> ╠══════════════════════════════════════════╣
> ║ Active Units:  Ambulance 12  Police 8      ║
> ╠══════════════════════════════════════════╣
> ║ Safe Route → ETA 7 min · 4.3 km            ║
> ╚══════════════════════════════════════════╝
> ```
> Style choices (going for a clean coding-agent-CLI look — box-drawing borders, monospace, muted palette, a status color per line: green=done, yellow=running, red=blocked): use a dark background, off-white text, a single accent color for headers/borders, green/yellow/red only for status. Add an ASCII-art "KRATOS" banner (use a block/standard figlet-style font) that renders on startup before the panels appear.

**Definition of Done:**
- [ ] Launching `python tui/app.py` shows the ASCII banner, then live-updating panels as you trigger pipeline runs from a second terminal (curl) or the React app
- [ ] Killing/restarting the backend doesn't crash the TUI (graceful reconnect or clear "disconnected" state)

---

### Phase 10 — React Frontend: Dashboard + Matching TUI Panel + ASCII Banner

**Prompt:**
> Build the React dashboard: Leaflet map (road graph + disaster overlay + unit markers), Chart.js panels (road availability, response time, vehicle usage), and a live agent-status list. Additionally add a "TUI panel" component — a monospace, box-drawn panel replicating the same layout/status icons as the Phase 9 terminal TUI (same color rules: green/yellow/red status, single accent border color), so a user can toggle between "Dashboard view" and "Terminal view" of the same live data. Render the same ASCII "KRATOS" banner as a `<pre>` block in a splash screen on load, matching the terminal version's font/art.

**Definition of Done:**
- [ ] Toggling between Dashboard and Terminal-style views shows the same underlying live agent status, no separate data path
- [ ] ASCII banner renders identically (same characters) in both the terminal and the browser

---

### Phase 11 — End-to-End Integration Test

**Prompt:**
> Write one end-to-end pytest that: uploads a sample image → segments → builds graph → runs a flood simulation → plans a route → allocates a resource → dispatches a volunteer → fires a radio alert → generates a report — all through the orchestrator's `run_pipeline`, asserting each step produced non-empty, well-formed output. This is your single "does the whole thing still work" regression test to run before any demo.

**Definition of Done:**
- [ ] This one test passes locally and takes under ~10 seconds (mock the NIM call in the test so it doesn't depend on network/API availability)

---

### Phase 12 — Demo Polish

- Seed a couple of realistic scenarios (a small real neighborhood via OSM export, or `sample_graph()`) so the demo never depends on a live upload working perfectly on stage
- Rehearse the "NIM fails → CV fallback → demo continues" path on purpose once, so you know it's actually safe
- One-page README: architecture diagram (from section 0 above), how to start both servers, how to start the standalone TUI, and the two `curl` commands that trigger a full pipeline run

---

## Notes on scope decisions made for you

- **Dropped for hackathon**: SUMO, PostgreSQL, Redis, GeoTIFF parsing, JWT auth, role-based access. All listed in your SRS as "Future Scope" or infra — none of them are needed to demonstrate the 13 agents working end-to-end, and each one adds a new failure surface. Add them back only if time remains after Phase 12.
- **Radio-frequency alert agent is explicitly a simulation layer.** Real IPAWS/government EAS integration requires a partnership/licensing agreement — building a realistic-looking simulated payload is the right scope for a hackathon and is honest to present as such.
- **Route prediction failure root cause**: almost certainly Route Planning being hard-dependent on Road Extraction succeeding. Phase 3's `sample_graph()` breaks that dependency so you can build and demo Phases 4–12 regardless of whether the vision side is perfect.
- **LangChain scope**: used narrowly, only for the two NIM model calls (`backend/agents/nim_client.py`, section 1a) — not as the orchestration framework. The `BaseAgent`/`AgentOrchestrator` from Phase 1 stays plain Python. Install with `pip install langchain-nvidia-ai-endpoints` in `backend/requirements.txt`.
