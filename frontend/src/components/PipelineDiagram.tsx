import React from "react";


export interface PipelinePhase {
  phaseName: string;
  badge: string;
  agents: { id: string; name: string; agentName: string }[];
}

interface PipelineDiagramProps {
  agentStatus: Record<string, any>;
  onNodeClick?: (agentName: string) => void;
}

export const PipelineDiagram: React.FC<PipelineDiagramProps> = ({
  agentStatus,
  onNodeClick,
}) => {
  const phases: PipelinePhase[] = [
    {
      phaseName: "1. Ingestion & Imagery",
      badge: "DATA LAYER",
      agents: [
        { id: "ingest", name: "Image Ingestion", agentName: "image_ingestion" },
        { id: "vlm", name: "Road Extraction", agentName: "road_extraction" },
        { id: "sat", name: "Satellite Tasking", agentName: "autonomous_satellite_tasking" },
        { id: "dmg", name: "Damage Verify", agentName: "damage_verification" },
        { id: "climate", name: "Micro Climate", agentName: "predictive_micro_climate" },
      ],
    },
    {
      phaseName: "2. Risk & Intel",
      badge: "ANALYTICS",
      agents: [
        { id: "graph", name: "Road Graph NX", agentName: "road_graph" },
        { id: "infra", name: "Infra Collapse Risk", agentName: "infrastructure_risk" },
        { id: "struct", name: "Structural Eng.", agentName: "structural_engineering" },
        { id: "traffic", name: "Traffic Congestion", agentName: "traffic_analysis" },
        { id: "water", name: "Water Quality", agentName: "water_quality" },
      ],
    },
    {
      phaseName: "3. Simulation & Pathing",
      badge: "DISASTER ENGINE",
      agents: [
        { id: "sim", name: "Hazard Simulation", agentName: "disaster_simulation" },
        { id: "route", name: "Route Planning", agentName: "route_planning" },
        { id: "drone", name: "Drone 3D Swarm", agentName: "drone_swarm_orchestrator" },
        { id: "mesh", name: "Telecom COW Mesh", agentName: "telecom_mesh" },
        { id: "power", name: "Power Grid Rest.", agentName: "power_grid_restoration" },
      ],
    },
    {
      phaseName: "4. Logistics & Dispatch",
      badge: "OPS DISPATCH",
      agents: [
        { id: "res", name: "Resource Allocation", agentName: "resource_allocation" },
        { id: "triage", name: "Medical Triage", agentName: "medical_triage" },
        { id: "shelter", name: "Shelter Occupancy", agentName: "shelter_capacity" },
        { id: "supply", name: "Helicopter Cargo", agentName: "supply_logistics" },
        { id: "evac", name: "Evacuation Trans.", agentName: "evacuation_transport" },
      ],
    },
    {
      phaseName: "5. Comms & Alerting",
      badge: "IPAWS & NLP",
      agents: [
        { id: "social", name: "Social Distress NER", agentName: "social_media_distress" },
        { id: "vol", name: "Volunteer Dispatch", agentName: "volunteer_healthcare_dispatch" },
        { id: "wild", name: "Wildlife Rescue", agentName: "wildlife_rescue" },
        { id: "debris", name: "Debris Clearance", agentName: "debris_clearance" },
        { id: "rf", name: "RF IPAWS Alert", agentName: "radio_frequency_alert" },
      ],
    },
    {
      phaseName: "6. Report & Audit",
      badge: "GOVERNANCE",
      agents: [
        { id: "notify", name: "Multi-Channel Notif", agentName: "notification" },
        { id: "pr", name: "Public Relations", agentName: "public_relations" },
        { id: "pdf", name: "Nemotron PDF Report", agentName: "report_generation" },
        { id: "audit", name: "SQLite Audit Log", agentName: "audit" },
        { id: "ping", name: "Ping Diagnostic", agentName: "ping" },
      ],
    },
  ];

  const activeCount = Object.values(agentStatus).filter(
    (s: any) => s?.last_run_status === "success" || s?.status === "busy"
  ).length;

  return (
    <div
      style={{
        backgroundColor: "#0D1117",
        border: "1px solid #21262D",
        borderRadius: "12px",
        padding: "16px 20px",
        marginBottom: "20px",
      }}
    >
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "16px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          <span style={{ width: "8px", height: "8px", borderRadius: "50%", backgroundColor: "#38BDF8" }} />
          <h3
            style={{
              fontSize: "0.85rem",
              fontWeight: 700,
              color: "#F0F6FC",
              letterSpacing: "0.05em",
              fontFamily: "var(--mono-font)",
              margin: 0,
            }}
          >
            30-AGENT WORKFLOW PIPELINE
          </h3>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: "16px", fontSize: "0.75rem", fontFamily: "var(--mono-font)" }}>
          <span style={{ color: "#8B949E" }}>
            ACTIVE: <strong style={{ color: "#38BDF8" }}>{activeCount} / 30</strong>
          </span>
          <span style={{ color: "#10B981" }}>● COMPLETED</span>
          <span style={{ color: "#38BDF8" }}>● RUNNING</span>
          <span style={{ color: "#EF4444" }}>● ALERT</span>
        </div>
      </div>

      {/* 6-Phase Horizontal Grid */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
          gap: "12px",
        }}
      >
        {phases.map((phase, pIdx) => (
          <div
            key={pIdx}
            style={{
              backgroundColor: "#161B22",
              border: "1px solid #21262D",
              borderRadius: "8px",
              padding: "12px",
            }}
          >
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "space-between",
                marginBottom: "10px",
                paddingBottom: "6px",
                borderBottom: "1px solid #21262D",
              }}
            >
              <span
                style={{
                  fontSize: "0.7rem",
                  fontWeight: 700,
                  color: "#F0F6FC",
                  fontFamily: "var(--mono-font)",
                }}
              >
                {phase.phaseName}
              </span>
              <span
                style={{
                  fontSize: "0.6rem",
                  fontWeight: 600,
                  color: "#38BDF8",
                  backgroundColor: "rgba(56, 189, 248, 0.1)",
                  padding: "1px 5px",
                  borderRadius: "4px",
                }}
              >
                {phase.badge}
              </span>
            </div>

            {/* Agents inside Phase */}
            <div style={{ display: "flex", flexDirection: "column", gap: "8px" }}>
              {phase.agents.map((agent) => {
                const st = agentStatus[agent.agentName];
                const isBusy = st?.status === "busy" || st?.status === "running";
                const isSuccess = st?.last_run_status === "success";
                const isError = st?.status === "error";

                let dotColor = "#484F58";
                if (isBusy) dotColor = "#38BDF8";
                else if (isSuccess) dotColor = "#10B981";
                else if (isError) dotColor = "#EF4444";

                return (
                  <div
                    key={agent.id}
                    onClick={() => onNodeClick && onNodeClick(agent.agentName)}
                    style={{
                      display: "flex",
                      alignItems: "center",
                      gap: "8px",
                      cursor: "pointer",
                      padding: "4px 6px",
                      borderRadius: "4px",
                      backgroundColor: isBusy ? "rgba(56, 189, 248, 0.1)" : "transparent",
                      transition: "background 0.2s ease",
                    }}
                    onMouseEnter={(e) => (e.currentTarget.style.backgroundColor = "rgba(255, 255, 255, 0.03)")}
                    onMouseLeave={(e) =>
                      (e.currentTarget.style.backgroundColor = isBusy ? "rgba(56, 189, 248, 0.1)" : "transparent")
                    }
                  >
                    <span
                      style={{
                        width: "7px",
                        height: "7px",
                        borderRadius: "50%",
                        backgroundColor: dotColor,
                        boxShadow: isBusy ? "0 0 8px #38BDF8" : isSuccess ? "0 0 6px #10B981" : "none",
                        flexShrink: 0,
                      }}
                    />
                    <span
                      style={{
                        fontSize: "0.72rem",
                        color: isBusy ? "#38BDF8" : isSuccess ? "#F0F6FC" : "#8B949E",
                        fontFamily: "var(--mono-font)",
                        whiteSpace: "nowrap",
                        overflow: "hidden",
                        textOverflow: "ellipsis",
                      }}
                    >
                      {agent.name}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
