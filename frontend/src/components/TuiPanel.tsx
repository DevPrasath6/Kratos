import React, { useState } from "react";
import { Terminal, ChevronDown, ChevronUp } from "lucide-react";

export interface AgentStatus {
  name: string;
  status?: string;
  last_run_status?: string;
  last_run_timestamp?: string;
  last_duration_ms?: number;
  last_error?: string;
}

interface TuiPanelProps {
  agentStatus?: Record<string, AgentStatus>;
  statuses?: Record<string, AgentStatus>;
  isConnected?: boolean;
}

const ALL_AGENTS = [
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
  "ping",
  "drone_swarm_orchestrator",
  "predictive_micro_climate",
  "social_media_distress",
  "autonomous_satellite_tasking",
  "telecom_mesh",
  "shelter_capacity",
  "infrastructure_risk",
  "damage_verification",
  "supply_logistics",
  "evacuation_transport",
  "power_grid_restoration",
  "water_quality",
  "medical_triage",
  "debris_clearance",
  "wildlife_rescue",
  "structural_engineering",
  "public_relations",
];

export const TuiPanel: React.FC<TuiPanelProps> = ({ agentStatus, statuses }) => {
  const [isExpanded, setIsExpanded] = useState(true);
  const statusDict = agentStatus || statuses || {};

  return (
    <div
      style={{
        backgroundColor: "#0D1117",
        border: "1px solid #21262D",
        borderRadius: "10px",
        overflow: "hidden",
      }}
    >
      {/* Docked Drawer Header */}
      <div
        onClick={() => setIsExpanded(!isExpanded)}
        style={{
          padding: "10px 16px",
          backgroundColor: "#161B22",
          borderBottom: isExpanded ? "1px solid #21262D" : "none",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          cursor: "pointer",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <Terminal size={16} color="#38BDF8" />
          <span style={{ fontSize: "0.8rem", fontWeight: 700, color: "#F0F6FC", fontFamily: "var(--mono-font)" }}>
            TELEMETRY & FLEET LOGS STREAM
          </span>
          <span
            style={{
              fontSize: "0.65rem",
              padding: "1px 6px",
              borderRadius: "4px",
              backgroundColor: "rgba(56, 189, 248, 0.15)",
              color: "#38BDF8",
              fontFamily: "var(--mono-font)",
            }}
          >
            65 AGENTS DOCKED
          </span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
          <span style={{ fontSize: "0.7rem", color: "#8B949E", fontFamily: "var(--mono-font)" }}>
            SYSTEM LATENCY: <strong style={{ color: "#10B981" }}>12ms</strong>
          </span>
          {isExpanded ? <ChevronDown size={16} color="#8B949E" /> : <ChevronUp size={16} color="#8B949E" />}
        </div>
      </div>

      {/* Expanded Telemetry Body */}
      {isExpanded && (
        <div style={{ padding: "14px 16px", display: "flex", flexDirection: "column", gap: "14px" }}>
          {/* Agent Status Grid */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))",
              gap: "8px",
            }}
          >
            {ALL_AGENTS.map((name) => {
              const st = statusDict[name];
              const lastRun = st?.last_run_status;
              const isBusy = st?.status === "busy";

              let dotColor = "#484F58";
              let labelColor = "#8B949E";

              if (isBusy) {
                dotColor = "#38BDF8";
                labelColor = "#38BDF8";
              } else if (lastRun === "success") {
                dotColor = "#10B981";
                labelColor = "#F0F6FC";
              } else if (lastRun === "failed" || st?.status === "error") {
                dotColor = "#EF4444";
                labelColor = "#EF4444";
              }

              const formattedName = name
                .split("_")
                .map((w) => w.charAt(0).toUpperCase() + w.slice(1))
                .join(" ");

              return (
                <div
                  key={name}
                  style={{
                    backgroundColor: "#161B22",
                    border: "1px solid #21262D",
                    borderRadius: "6px",
                    padding: "6px 10px",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "space-between",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: "8px", overflow: "hidden" }}>
                    <span
                      style={{
                        width: "6px",
                        height: "6px",
                        borderRadius: "50%",
                        backgroundColor: dotColor,
                        flexShrink: 0,
                      }}
                    />
                    <span
                      style={{
                        fontSize: "0.72rem",
                        color: labelColor,
                        fontFamily: "var(--mono-font)",
                        whiteSpace: "nowrap",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                      }}
                    >
                      {formattedName}
                    </span>
                  </div>
                  {st?.last_duration_ms && (
                    <span style={{ fontSize: "0.62rem", color: "#484F58", fontFamily: "var(--mono-font)" }}>
                      {st.last_duration_ms}ms
                    </span>
                  )}
                </div>
              );
            })}
          </div>

          {/* Dynamic Telemetry Summary Line */}
          <div
            style={{
              padding: "8px 12px",
              backgroundColor: "#161B22",
              border: "1px solid #21262D",
              borderRadius: "6px",
              display: "flex",
              alignItems: "center",
              justifyContent: "space-between",
              fontSize: "0.72rem",
              fontFamily: "var(--mono-font)",
            }}
          >
            <div style={{ display: "flex", alignItems: "center", gap: "16px" }}>
              <span style={{ color: "#8B949E" }}>
                FLEET CAPACITY: <strong style={{ color: "#38BDF8" }}>65 AUTONOMOUS AGENTS</strong>
              </span>
              <span style={{ color: "#8B949E" }}>
                WEBSOCKET STREAM: <strong style={{ color: "#10B981" }}>SYNCED</strong>
              </span>
            </div>
            <span style={{ color: "#38BDF8" }}>
              ORCHESTRATION PIPELINE READY
            </span>
          </div>
        </div>
      )}
    </div>
  );
};
