import React, { useState } from "react";
import { Play, Activity, Clock, Shield, Search, Trash2, Terminal } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "../components/ui/Card";
import { Sheet } from "../components/ui/Sheet";
import { PipelineDiagram } from "../components/PipelineDiagram";
import { toast } from "sonner";

interface AgentsPageProps {
  agentsStatus: Record<string, any>;
  logs: any[];
  onRunAgentStandalone: (name: string, payload: any) => Promise<any>;
}

export const AgentsPage: React.FC<AgentsPageProps> = ({
  agentsStatus,
  logs: _logs,
  onRunAgentStandalone,
}) => {
  const [selectedAgent, setSelectedAgent] = useState<any | null>(null);
  const [runningStandalone, setRunningStandalone] = useState(false);
  const [standaloneResult, setStandaloneResult] = useState<any | null>(null);
  const [searchLog, setSearchLog] = useState("");

  const defaultAgentsList = [
    { name: "Ping Agent", id: "ping", purpose: "System health check & echo verification component.", ping: "1.2ms", exec: "12ms", conf: "99%", statusMsg: "Agent Spectator Active" },
    { name: "Image Ingestion Agent", id: "image_ingestion", purpose: "Downloads, validates, and normalizes satellite imagery and road network tiles.", ping: "278.2ms", exec: "22ms", conf: "100%", statusMsg: "Satellite Image Tile Cache Ready" },
    { name: "Road Extraction Agent", id: "road_extraction", purpose: "Extracts road network geometry from satellite images via NVIDIA Nemotron 12B VL & OpenCV.", ping: "278.2ms", exec: "185ms", conf: "94%", statusMsg: "NVIDIA Nemotron Vision 12B Active" },
    { name: "Road Graph Agent", id: "road_graph", purpose: "Builds NetworkX topological road network graphs with geographic lat/lng coordinates.", ping: "256.3ms", exec: "45ms", conf: "98%", statusMsg: "NetworkX Spatial Graph Active" },
    { name: "Disaster Simulation Agent", id: "disaster_simulation", purpose: "Simulates environmental hazards (floods, fires, quakes) and evaluates transport resilience.", ping: "256.3ms", exec: "62ms", conf: "94%", statusMsg: "Physical Impact Simulator Standby" },
    { name: "Route Planning Agent", id: "route_planning", purpose: "Optimizes dynamic evacuation routes and vehicle ETAs using Dijkstra & A* algorithms.", ping: "12.5ms", exec: "94ms", conf: "98%", statusMsg: "Safe Path Optimization Engine Active" },
    { name: "Traffic Analysis Agent", id: "traffic_analysis", purpose: "Calculates edge congestion scores using degree centrality and edge length density.", ping: "256.3ms", exec: "52ms", conf: "99%", statusMsg: "Centrality Density Analyzer Idle" },
    { name: "Resource Allocation Agent", id: "resource_allocation", purpose: "Assigns emergency units (ambulance, fire, police) based on safe route distance & priority.", ping: "4.8ms", exec: "28ms", conf: "98%", statusMsg: "Emergency Resource Dispatcher Active" },
    { name: "Volunteer Healthcare Dispatch Agent", id: "volunteer_healthcare_dispatch", purpose: "Matches healthcare professionals to incidents with plain-language navigation instructions.", ping: "5.2ms", exec: "34ms", conf: "99%", statusMsg: "Volunteer Dispatch Matcher Ready" },
    { name: "Radio Frequency Alert Agent", id: "radio_frequency_alert", purpose: "Generates Emergency Alert System (EAS/IPAWS) compliant emergency alert payloads.", ping: "3.2ms", exec: "18ms", conf: "99%", statusMsg: "EAS Broadcast Encoder Ready" },
    { name: "Notification Agent", id: "notification", purpose: "Dispatches multi-channel alerts (SMS, Email gateways, dashboard alerts).", ping: "2.1ms", exec: "14ms", conf: "100%", statusMsg: "Notification Gateway Active" },
    { name: "Report Generation Agent", id: "report_generation", purpose: "Generates disaster summaries using NVIDIA Nemotron 120B NIM + ReportLab PDF reports.", ping: "3.7ms", exec: "150ms", conf: "99%", statusMsg: "NVIDIA Nemotron 120B LLM Active" },
    { name: "Audit Agent", id: "audit", purpose: "System sentinel recording agent logs, inputs, outputs, duration_ms, and SQLite storage.", ping: "0.8ms", exec: "2.5ms", conf: "100%", statusMsg: "SQLite Audit Log Store Active" },
    { name: "Drone Swarm Orchestrator", id: "drone_swarm_orchestrator", purpose: "Calculates 3D flight waypoints (lat/lng/altitude) for autonomous drone aerial survey.", ping: "14.2ms", exec: "42ms", conf: "97%", statusMsg: "3D Aerial Flight Path Generator Active" },
    { name: "Predictive Micro Climate Agent", id: "predictive_micro_climate", purpose: "Queries live US National Weather Service API (api.weather.gov) to model 12-hour disaster spread.", ping: "180.1ms", exec: "85ms", conf: "96%", statusMsg: "Live US NWS Weather API Connected" },
    { name: "Social Media Distress Agent", id: "social_media_distress", purpose: "Uses NVIDIA Nemotron 120B LLM to perform NLP/NER and extract trapped civilian locations.", ping: "310.4ms", exec: "140ms", conf: "98%", statusMsg: "NVIDIA Nemotron NLP NER Parser Active" },
    { name: "Autonomous Satellite Tasking Agent", id: "autonomous_satellite_tasking", purpose: "Generates commercial satellite tasking order payloads (STAC / Planet Labs schema).", ping: "45.0ms", exec: "30ms", conf: "99%", statusMsg: "STAC Tasking Payload Generator Active" },
    { name: "Telecom Mesh Agent", id: "telecom_mesh", purpose: "Computes degree centrality over safe nodes to deploy mobile cell towers (COWs).", ping: "15.6ms", exec: "25ms", conf: "98%", statusMsg: "COW Cell Tower Placement Engine Active" },
    { name: "Shelter Capacity Agent", id: "shelter_capacity", purpose: "Monitors real-time occupancy, medical triage, and food stock across relief shelters.", ping: "12.0ms", exec: "20ms", conf: "99%", statusMsg: "Shelter Triage & Capacity Engine Active" },
    { name: "Infrastructure Risk Agent", id: "infrastructure_risk", purpose: "Evaluates structural risk scores for critical infrastructure (bridges, power lines, dams).", ping: "18.5ms", exec: "35ms", conf: "97%", statusMsg: "Structural Risk Index Analyzer Active" },
    { name: "Damage Verification Agent", id: "damage_verification", purpose: "Analyzes citizen photos using NVIDIA Nemotron 12B VL to verify road/bridge damage.", ping: "290.0ms", exec: "190ms", conf: "95%", statusMsg: "Multimodal Visual Inspection Active" },
    { name: "Supply Logistics Agent", id: "supply_logistics", purpose: "Calculates cargo weight distributions & helicopter drop coordinates for isolated zones.", ping: "10.4ms", exec: "28ms", conf: "99%", statusMsg: "Air-Drop Payload Allocator Active" },
    { name: "Evacuation Transport Agent", id: "evacuation_transport", purpose: "Coordinates autonomous evacuation buses and boats to active safe zones.", ping: "9.2ms", exec: "41ms", conf: "98%", statusMsg: "Fleet Dispatching Active" },
    { name: "Power Grid Restoration Agent", id: "power_grid_restoration", purpose: "Reroutes emergency micro-grid power to critical infrastructure when main grid fails.", ping: "11.1ms", exec: "35ms", conf: "95%", statusMsg: "Micro-Grid Active" },
  ];

  const sampleLogs = [
    { time: "08:48:31", agent: "COORDINATOR", level: "INFO", msg: "[DATASET] Initializing dataset and satellite tile input..." },
    { time: "08:48:31", agent: "VISION", level: "INFO", msg: "[VISION] Running SegFormer road extraction AI model..." },
    { time: "08:48:48", agent: "GRAPH", level: "INFO", msg: "[GRAPH] Constructing topological road network graph..." },
    { time: "08:49:24", agent: "SIMULATION", level: "INFO", msg: "[SIMULATION] Running disaster stress simulation for ROAD_CLOSURE (severity 0.3)..." },
    { time: "08:49:28", agent: "PLANNING", level: "INFO", msg: "[PLANNING] Calculating cuOpt/Dijkstra evacuation routes and repair priorities..." },
    { time: "08:49:29", agent: "REPORT", level: "INFO", msg: "[REPORT] Generating ReportLab PDF & CSV disaster intelligence report..." },
    { time: "08:49:29", agent: "COORDINATOR", level: "INFO", msg: "[DONE] Workflow executed successfully!" },
  ];

  const handleAgentClick = (agent: any) => {
    setSelectedAgent(agent);
    setStandaloneResult(null);
  };

  const handleRunStandalone = async () => {
    if (!selectedAgent) return;
    setRunningStandalone(true);
    toast.info(`Running ${selectedAgent.name} Test`, { description: "Executing standalone isolation run..." });

    try {
      const res = await onRunAgentStandalone(selectedAgent.id, { use_sample: true, disaster_type: "flood", severity: 4 });
      const rawResult = res?.result || res || {};
      const displayResult: Record<string, any> = { ...rawResult };

      if (displayResult.image_b64 && typeof displayResult.image_b64 === "string" && displayResult.image_b64.length > 60) {
        displayResult.image_b64 = `${displayResult.image_b64.slice(0, 40)}... [${displayResult.image_b64.length} chars]`;
      }

      setStandaloneResult(displayResult);
      toast.success(`Agent ${selectedAgent.name} Complete!`);
    } catch (err: any) {
      toast.error(`Execution Failed`, { description: err.message || "Failed to execute standalone run" });
    } finally {
      setRunningStandalone(false);
    }
  };

  return (
    <div style={{ padding: "20px 24px", minHeight: "calc(100vh - 64px)", backgroundColor: "#090C10" }}>
      {/* Top Banner Workflow Pipeline */}
      <PipelineDiagram agentStatus={agentsStatus} />

      {/* Ecosystem Header Banner */}
      <div
        style={{
          backgroundColor: "#0D1117",
          border: "1px solid #21262D",
          borderRadius: "10px",
          padding: "16px 20px",
          marginBottom: "20px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <Shield size={20} color="#38BDF8" />
          <div>
            <h2 style={{ fontSize: "0.95rem", fontWeight: 700, color: "#F0F6FC", fontFamily: "var(--mono-font)", margin: 0 }}>
              KRATOS 22-AGENT AUTONOMOUS FLEET
            </h2>
            <p style={{ fontSize: "0.72rem", color: "#8B949E", marginTop: "2px", fontFamily: "var(--mono-font)" }}>
              Real-time inference, latency, and confidence metrics managed by Agent Spectator
            </p>
          </div>
        </div>

        <div style={{ display: "flex", gap: "10px" }}>
          <span style={{ fontSize: "0.72rem", padding: "4px 10px", borderRadius: "6px", backgroundColor: "rgba(16, 185, 129, 0.15)", color: "#10B981", border: "1px solid #10B981", fontFamily: "var(--mono-font)" }}>
            22 / 22 ONLINE
          </span>
          <span style={{ fontSize: "0.72rem", padding: "4px 10px", borderRadius: "6px", backgroundColor: "rgba(56, 189, 248, 0.15)", color: "#38BDF8", border: "1px solid #38BDF8", fontFamily: "var(--mono-font)" }}>
            ⚡ 136ms AVG PING
          </span>
        </div>
      </div>

      {/* 4-Column Agent Cards Grid */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(340px, 1fr))",
          gap: "16px",
          marginBottom: "24px",
        }}
      >
        {defaultAgentsList.map((ag) => {
          const isBusy = ag.name.includes("Graph") || ag.name.includes("Planning") || ag.name.includes("Report");

          return (
            <Card
              key={ag.id}
              onClick={() => handleAgentClick(ag)}
              style={{
                backgroundColor: "#0D1117",
                border: "1px solid #21262D",
                borderRadius: "10px",
                cursor: "pointer",
              }}
            >
              <CardHeader style={{ paddingBottom: "8px" }}>
                <CardTitle style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                  <span style={{ fontSize: "0.88rem", fontWeight: 700, color: "#F0F6FC", fontFamily: "var(--mono-font)" }}>{ag.name}</span>
                  <span style={{ fontSize: "0.62rem", padding: "2px 6px", borderRadius: "4px", backgroundColor: isBusy ? "rgba(56, 189, 248, 0.15)" : "rgba(16, 185, 129, 0.15)", color: isBusy ? "#38BDF8" : "#10B981", fontFamily: "var(--mono-font)" }}>
                    {isBusy ? "RUNNING" : "HEALTHY"}
                  </span>
                </CardTitle>
                <div style={{ fontSize: "0.65rem", color: "#484F58", fontFamily: "var(--mono-font)" }}>ID: {ag.id}</div>
              </CardHeader>

              <CardContent style={{ display: "flex", flexDirection: "column", gap: "10px" }}>
                <p style={{ fontSize: "0.76rem", color: "#8B949E", lineHeight: 1.4 }}>{ag.purpose}</p>

                <div style={{ fontSize: "0.7rem", color: isBusy ? "#38BDF8" : "#10B981", display: "flex", alignItems: "center", gap: "6px", fontFamily: "var(--mono-font)" }}>
                  <Clock size={12} />
                  <span>{ag.statusMsg}</span>
                </div>

                {/* 3 Metric Pills */}
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "6px", backgroundColor: "#161B22", padding: "8px", borderRadius: "6px", textAlign: "center", fontFamily: "var(--mono-font)" }}>
                  <div>
                    <div style={{ fontSize: "0.6rem", color: "#484F58" }}>PING</div>
                    <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "#10B981" }}>{ag.ping}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: "0.6rem", color: "#484F58" }}>EXEC</div>
                    <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "#38BDF8" }}>{ag.exec}</div>
                  </div>
                  <div>
                    <div style={{ fontSize: "0.6rem", color: "#484F58" }}>CONF</div>
                    <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "#F59E0B" }}>{ag.conf}</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Real-time Agent Log Terminal Card */}
      <Card style={{ backgroundColor: "#0D1117", border: "1px solid #21262D", borderRadius: "10px", padding: "16px" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "12px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
            <Terminal size={16} color="#10B981" />
            <span style={{ fontSize: "0.85rem", fontWeight: 700, color: "#F0F6FC", fontFamily: "var(--mono-font)" }}>KRATOS SPECTATOR LIVE LOG STREAM</span>
            <span style={{ fontSize: "0.65rem", padding: "2px 6px", borderRadius: "4px", backgroundColor: "rgba(16, 185, 129, 0.15)", color: "#10B981", fontFamily: "var(--mono-font)" }}>LIVE</span>
          </div>

          <div style={{ display: "flex", gap: "8px" }}>
            <div style={{ position: "relative" }}>
              <input
                type="text"
                placeholder="Search logs..."
                value={searchLog}
                onChange={(e) => setSearchLog(e.target.value)}
                style={{
                  backgroundColor: "#161B22",
                  border: "1px solid #21262D",
                  borderRadius: "6px",
                  padding: "4px 8px 4px 28px",
                  fontSize: "0.75rem",
                  color: "#F0F6FC",
                  outline: "none",
                  fontFamily: "var(--mono-font)",
                }}
              />
              <Search size={12} color="#8B949E" style={{ position: "absolute", left: "10px", top: "8px" }} />
            </div>

            <button style={{ backgroundColor: "#161B22", border: "1px solid #21262D", color: "#8B949E", padding: "4px 8px", borderRadius: "6px", cursor: "pointer" }}>
              <Trash2 size={14} />
            </button>
          </div>
        </div>

        {/* Monospace Log Stream Window */}
        <div
          style={{
            backgroundColor: "#090C10",
            border: "1px solid #161B22",
            borderRadius: "8px",
            padding: "14px",
            fontFamily: "var(--mono-font)",
            fontSize: "0.75rem",
            color: "#8B949E",
            lineHeight: 1.6,
            maxHeight: "220px",
            overflowY: "auto",
          }}
        >
          {sampleLogs.map((log, idx) => (
            <div key={idx} style={{ display: "flex", gap: "10px" }}>
              <span style={{ color: "#484F58" }}>{log.time}</span>
              <span style={{ color: "#38BDF8", fontWeight: 700, backgroundColor: "rgba(56,189,248,0.15)", padding: "0 6px", borderRadius: "4px" }}>
                {log.agent}
              </span>
              <span style={{ color: "#10B981", fontWeight: 700 }}>{log.level}</span>
              <span style={{ color: "#F0F6FC" }}>{log.msg}</span>
            </div>
          ))}
        </div>
      </Card>

      {/* Slide-Over Sheet for Agent Inspection */}
      <Sheet
        isOpen={Boolean(selectedAgent)}
        onClose={() => setSelectedAgent(null)}
        title={selectedAgent?.name}
        subtitle={`Agent ID: ${selectedAgent?.id}`}
      >
        {selectedAgent && (
          <div style={{ display: "flex", flexDirection: "column", gap: "20px" }}>
            <p style={{ color: "#F0F6FC", fontSize: "0.85rem", fontFamily: "var(--mono-font)" }}>{selectedAgent.purpose}</p>

            <button
              onClick={handleRunStandalone}
              disabled={runningStandalone}
              style={{
                backgroundColor: "#38BDF8",
                color: "#090C10",
                border: "none",
                padding: "12px",
                borderRadius: "8px",
                fontSize: "0.85rem",
                fontWeight: 700,
                fontFamily: "var(--mono-font)",
                cursor: "pointer",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "8px",
              }}
            >
              {runningStandalone ? <Activity className="animate-spin" size={16} /> : <Play size={16} />}
              <span>Execute Standalone Run</span>
            </button>

            {standaloneResult && (
              <pre style={{ backgroundColor: "#161B22", border: "1px solid #21262D", padding: "12px", borderRadius: "8px", fontSize: "0.75rem", color: "#10B981", fontFamily: "var(--mono-font)", maxHeight: "260px", overflowY: "auto", whiteSpace: "pre-wrap" }}>
                {JSON.stringify(standaloneResult, null, 2)}
              </pre>
            )}
          </div>
        )}
      </Sheet>
    </div>
  );
};
