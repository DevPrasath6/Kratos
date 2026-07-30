# KRATOS: Autonomous Disaster Response & Infrastructure Resilience Platform

> **Knowledge-driven Road Analysis for Terrain Occlusion & Security**
> A state-of-the-art multi-agent AI system for real-time disaster simulation, aerial damage verification, dynamic evacuation pathfinding, and autonomous emergency logistics.

---

## 🏛️ System Architecture

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                         KRATOS FRONTEND DASHBOARD                                │
│                   React 18 + Vite + TailwindCSS + Leaflet                        │
│                           (http://localhost:5173)                                │
│                                                                                  │
│   ├── Dynamic Leaflet Map Container (Live Node Lat/Lng & Evacuation Polylines)   │
│   ├── 22-Stage Interactive Pipeline Visualizer                                   │
│   ├── Monospace CLI TUI Panel & Telemetry Charts                                 │
│   └── NVIDIA Nemotron LLM Disaster Response Chatbot                              │
└──────────────────────────────────────┬───────────────────────────────────────────┘
                                       │ WebSocket & REST APIs
┌──────────────────────────────────────▼───────────────────────────────────────────┐
│                      FASTAPI AGENT ORCHESTRATION SERVER                          │
│                           (http://localhost:8000)                                │
│                                                                                  │
│   ┌──────────────────────────────────────────────────────────────────────────┐   │
│   │                 22 AUTONOMOUS DISASTER RESPONSE AGENTS                   │   │
│   ├──────────────────────────────────────────────────────────────────────────┤   │
│   │  1. Image Ingestion Agent           12. Drone Swarm Orchestrator Agent   │   │
│   │  2. Road Extraction Agent           13. Predictive Micro-Climate Agent   │   │
│   │  3. Road Graph NetworkX Agent       14. Social Media Distress NLP Agent  │   │
│   │  4. Disaster Simulation Agent       15. Autonomous Satellite Tasking     │   │
│   │  5. Dynamic Route Planning Agent    16. Telecom Mesh COW Agent           │   │
│   │  6. Traffic Congestion Agent        17. Relief Shelter Capacity Agent    │   │
│   │  7. Resource Allocation Agent       18. Infrastructure Collapse Risk     │   │
│   │  8. Volunteer Dispatch Agent        19. Multimodal Vision Damage Agent   │   │
│   │  9. RF Broadcast Alert Agent        20. Supply Helicopter Cargo Agent    │   │
│   │ 10. PDF Report Generation Agent     21. Audit & SQLite Logging Agent     │   │
│   │ 11. Multi-Channel Notification      22. Standalone Ping Diagnostic       │   │
│   └──────────────────────────────────────────────────────────────────────────┘   │
│                                                                                  │
│   ├── SQLite Event Audit Database                                                │
│   └── NVIDIA NIM Integration (Nemotron 120B LLM & Nemotron 12B Vision VLM)       │
└──────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🤖 Full 22-Agent Pipeline Breakdown

| # | Agent Name | Key Purpose & Functionality | Underlying Tech / Models |
|---|------------|-----------------------------|--------------------------|
| **1** | **Image Ingestion** | Validates, normalizes, and resizes satellite/drone imagery (PNG/JPEG). | PIL / OpenCV / Base64 |
| **2** | **Road Extraction** | Identifies visible road segments from satellite tiles. | SegFormer AI / CV Fallback |
| **3** | **Road Graph NetworkX** | Constructs spatial topological graph with lat/lng node metadata. | NetworkX / Spatial Math |
| **4** | **Disaster Simulation** | Simulates flood, landslide, or earthquake road blockages. | Dynamic Hazard Engine |
| **5** | **Route Planning** | Calculates optimal safe evacuation paths avoiding blocked edges. | Dijkstra / cuOpt Math |
| **6** | **Traffic Congestion** | Computes deterministic road congestion via node degree centrality. | Degree Centrality Math |
| **7** | **Resource Allocation** | Allocates emergency ambulances, fire trucks, and rescue squads. | Optimization Solver |
| **8** | **Volunteer Dispatch** | Dispatches doctors/nurses to incidents avoiding hazardous nodes. | Network Routing |
| **9** | **Radio Frequency Alert** | Generates IPAWS CAP emergency alert broadcast scripts. | NVIDIA Nemotron 120B NIM |
| **10** | **PDF Report Generation** | Generates formal PDF intelligence reports with download links. | ReportLab / Nemotron LLM |
| **11** | **Multi-Channel Notification** | Dispatches SMS, Email, and Push notifications to field teams. | Async Dispatcher |
| **12** | **Drone Swarm Orchestrator** | Calculates 3D aerial search-and-rescue waypoints and altitudes. | 3D Flight Spatial Math |
| **13** | **Predictive Micro-Climate** | Queries live US NWS Weather API for 12-hour disaster forecasting. | `api.weather.gov` API |
| **14** | **Social Media Distress** | Extracts emergency locations and urgency scores from social feeds. | Nemotron 120B NLP NER |
| **15** | **Satellite Tasking** | Formulates STAC/Planet Labs tasking orders for satellite re-tasking. | STAC / ISO Timestamps |
| **16** | **Telecom Mesh COW** | Places Cell-On-Wheels (COWs) at high-centrality intersections. | Graph Centrality Math |
| **17** | **Relief Shelter Capacity** | Tracks real-time shelter bed occupancy and assigns evacuees. | Capacity Allocator |
| **18** | **Infrastructure Risk** | Computes structural collapse risk scores for bridges and power lines. | Risk Factor Analysis |
| **19** | **Damage Verification** | Analyzes ground photos to classify bridge/road collapse severity. | NVIDIA Nemotron 12B VL |
| **20** | **Supply Logistics** | Calculates helicopter cargo weight and air-drop coordinates. | Payload Allocation |
| **21** | **Audit Logging** | Persists all agent execution events into an SQLite audit store. | SQLite3 / JSON Store |
| **22** | **Ping Diagnostic** | Health check agent verifying agent network availability. | System Diagnostic |

---

## ⚡ Quick Start Guide

### Prerequisites
- Python 3.10+
- Node.js 18+ & npm

### 1. Environment Setup
Create a `.env` file in the `backend/` directory:

```ini
NIM_API_KEY=******************************************
NIM_VL_API_KEY=**********************************************
```

### 2. Launch Backend API Server
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
Backend will start at **`http://localhost:8000`**.

### 3. Launch Frontend Dashboard
```bash
cd frontend
npm install
npm run dev
```
Frontend will start at **`http://localhost:5173`**.

### 4. Launch Standalone TUI Terminal (Optional)
```bash
cd tui
python app.py
```

---

## 🧪 Testing

Run the full automated test suite covering all 22 agents and end-to-end multi-agent pipelines:

```bash
cd backend
python -m pytest
```
*Output: `36 passed in ~4.2s` (100% test pass rate).*

To test frontend TypeScript compilation and production bundle build:
```bash
cd frontend
npm run build
```

---

## 📡 REST API Reference

### 1. Execute Full 22-Agent Response Pipeline
```bash
curl -X POST http://localhost:8000/api/agents/pipeline/run \
  -H "Content-Type: application/json" \
  -d '{
    "use_sample": true,
    "disaster_type": "flood",
    "severity": 4,
    "start_node": 0,
    "target_node": 8
  }'
```

### 2. Query Live Graph Topology
```bash
curl http://localhost:8000/api/agents/graph/sample_graph_default
```

### 3. Test Standalone Agent Isolation (e.g. Drone Swarm)
```bash
curl -X POST http://localhost:8000/api/agents/drone_swarm_orchestrator/run \
  -H "Content-Type: application/json" \
  -d '{"drone_count": 4, "target_zone": "Sector Alpha"}'
```

### 4. Query All Agents Health Status
```bash
curl http://localhost:8000/api/agents/status
```

### 5. Fetch Real-time Telemetry Metrics
```bash
curl http://localhost:8000/api/agents/telemetry
```
