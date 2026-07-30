import React, { useState } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { Shield, LayoutDashboard, Users, Activity, FileText, Cpu, Terminal, Search } from "lucide-react";
import { Command } from "./ui/Command";
import { VisuallyHidden } from "./ui/VisuallyHidden";
import { toast } from "sonner";

interface NavbarProps {
  wsConnected: boolean;
  onRunPipeline: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({ wsConnected, onRunPipeline }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [cmdOpen, setCmdOpen] = useState(false);
  const [launchingTerminal, setLaunchingTerminal] = useState(false);

  const navTabs = [
    { id: "/dashboard", label: "COMMAND CENTER", icon: <LayoutDashboard size={15} /> },
    { id: "/agents", label: "AGENT FLEET", icon: <Users size={15} />, badge: "30" },
    { id: "/telemetry", label: "TELEMETRY", icon: <Activity size={15} /> },
    { id: "/reports", label: "REPORTS", icon: <FileText size={15} /> },
    { id: "/nemotron", label: "NEMOTRON AI", icon: <Cpu size={15} /> },
  ];

  const currentTab = navTabs.find((t) => location.pathname.startsWith(t.id))?.id || "/dashboard";

  const handleOpenTerminal = async () => {
    setLaunchingTerminal(true);
    toast.info("Launching System Terminal", {
      description: "Triggering POST /api/system/open-terminal for native KRATOS TUI...",
    });

    try {
      const resp = await fetch("http://localhost:8000/api/agents/system/open-terminal", { method: "POST" });
      if (resp.ok) {
        toast.success("Native Terminal Opened!", {
          description: "KRATOS TUI app initialized in local system terminal window.",
        });
      } else {
        const err = await resp.json();
        toast.error("Failed to Open Terminal", { description: err.detail || "Terminal launch error" });
      }
    } catch (err: any) {
      toast.error("Terminal Launch Failed", { description: err.message || "Failed to reach backend API" });
    } finally {
      setLaunchingTerminal(false);
    }
  };

  const commandItems = [
    {
      id: "cmd_pipeline",
      title: "Run Full 22-Agent Response Pipeline",
      category: "Actions",
      icon: <Activity size={18} />,
      action: () => onRunPipeline(),
    },
    {
      id: "cmd_dashboard",
      title: "Go to Command Center",
      category: "Navigation",
      icon: <LayoutDashboard size={18} />,
      action: () => navigate("/dashboard"),
    },
    {
      id: "cmd_agents",
      title: "Manage Agent Fleet (22 Agents)",
      category: "Navigation",
      icon: <Users size={18} />,
      action: () => navigate("/agents"),
    },
    {
      id: "cmd_telemetry",
      title: "Open Telemetry Mission Control",
      category: "Navigation",
      icon: <Activity size={18} />,
      action: () => navigate("/telemetry"),
    },
    {
      id: "cmd_reports",
      title: "Open Intelligence Reports",
      category: "Navigation",
      icon: <FileText size={18} />,
      action: () => navigate("/reports"),
    },
    {
      id: "cmd_nemotron",
      title: "Open NeMoTron AI Workspace",
      category: "Navigation",
      icon: <Cpu size={18} />,
      action: () => navigate("/nemotron"),
    },
    {
      id: "cmd_tui",
      title: "Launch Native System TUI Terminal",
      category: "System",
      icon: <Terminal size={18} />,
      action: () => handleOpenTerminal(),
    },
  ];

  return (
    <>
      <header
        style={{
          backgroundColor: "#0D1117",
          borderBottom: "1px solid #21262D",
          padding: "10px 24px",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          position: "sticky",
          top: 0,
          zIndex: 50,
        }}
      >
        {/* Left Brand Identifier */}
        <div
          style={{ display: "flex", alignItems: "center", gap: "12px", cursor: "pointer" }}
          onClick={() => navigate("/dashboard")}
        >
          <div
            style={{
              backgroundColor: "#161B22",
              border: "1px solid #30363D",
              width: "34px",
              height: "34px",
              borderRadius: "6px",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <Shield size={18} color="#38BDF8" />
          </div>
          <div>
            <h1
              style={{
                fontSize: "0.95rem",
                fontWeight: 700,
                color: "#F0F6FC",
                margin: 0,
                letterSpacing: "0.08em",
                fontFamily: "var(--mono-font)",
              }}
            >
              KRATOS <span style={{ fontSize: "0.65rem", color: "#38BDF8" }}>OPS-ROOM</span>
            </h1>
            <span style={{ fontSize: "0.62rem", color: "#8B949E", fontWeight: 500, fontFamily: "var(--mono-font)" }}>
              DISASTER RESPONSE COMMAND CENTER
            </span>
          </div>
        </div>

        {/* Mission Control Navigation Pills */}
        <nav style={{ display: "flex", alignItems: "center", gap: "6px" }}>
          {navTabs.map((tab) => {
            const isActive = currentTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => navigate(tab.id)}
                style={{
                  backgroundColor: isActive ? "#161B22" : "transparent",
                  border: `1px solid ${isActive ? "#30363D" : "transparent"}`,
                  color: isActive ? "#38BDF8" : "#8B949E",
                  padding: "6px 14px",
                  borderRadius: "6px",
                  fontSize: "0.75rem",
                  fontWeight: 600,
                  fontFamily: "var(--mono-font)",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  gap: "8px",
                  transition: "all 0.2s ease",
                }}
              >
                {tab.icon}
                <span>{tab.label}</span>
                {tab.badge && (
                  <span
                    style={{
                      fontSize: "0.65rem",
                      padding: "1px 5px",
                      borderRadius: "4px",
                      backgroundColor: isActive ? "rgba(56, 189, 248, 0.15)" : "#21262D",
                      color: isActive ? "#38BDF8" : "#F0F6FC",
                    }}
                  >
                    {tab.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>

        {/* Right Status Indicators & Quick Actions */}
        <div style={{ display: "flex", alignItems: "center", gap: "10px" }}>
          {/* NVIDIA NIM Indicator */}
          <span
            style={{
              fontSize: "0.68rem",
              fontWeight: 600,
              fontFamily: "var(--mono-font)",
              padding: "4px 8px",
              borderRadius: "4px",
              backgroundColor: "#161B22",
              color: "#38BDF8",
              border: "1px solid #21262D",
            }}
          >
            NIM LLM/VLM
          </span>

          {/* WebSocket Status */}
          <span
            style={{
              fontSize: "0.68rem",
              fontWeight: 600,
              fontFamily: "var(--mono-font)",
              padding: "4px 8px",
              borderRadius: "4px",
              backgroundColor: "#161B22",
              color: wsConnected ? "#10B981" : "#EF4444",
              border: "1px solid #21262D",
              display: "flex",
              alignItems: "center",
              gap: "6px",
            }}
          >
            <span
              style={{
                width: "6px",
                height: "6px",
                borderRadius: "50%",
                backgroundColor: wsConnected ? "#10B981" : "#EF4444",
              }}
            />
            {wsConnected ? "ONLINE" : "DISCONNECTED"}
          </span>

          {/* Native Terminal Launcher */}
          <button
            onClick={handleOpenTerminal}
            disabled={launchingTerminal}
            style={{
              backgroundColor: "#161B22",
              border: "1px solid #30363D",
              color: "#F0F6FC",
              padding: "6px 12px",
              borderRadius: "6px",
              fontSize: "0.75rem",
              fontWeight: 600,
              fontFamily: "var(--mono-font)",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "6px",
            }}
          >
            <Terminal size={14} color="#38BDF8" />
            <span>TUI</span>
          </button>

          {/* Cmd+K Quick Search Trigger */}
          <button
            onClick={() => setCmdOpen(true)}
            style={{
              backgroundColor: "#161B22",
              border: "1px solid #21262D",
              color: "#8B949E",
              padding: "6px 10px",
              borderRadius: "6px",
              fontSize: "0.75rem",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "6px",
            }}
          >
            <Search size={14} />
            <kbd
              style={{
                backgroundColor: "#21262D",
                padding: "1px 5px",
                borderRadius: "3px",
                fontSize: "0.65rem",
                color: "#F0F6FC",
                fontFamily: "var(--mono-font)",
              }}
            >
              ⌘K
            </kbd>
            <VisuallyHidden>Command Palette</VisuallyHidden>
          </button>
        </div>
      </header>

      <Command isOpen={cmdOpen} onClose={() => setCmdOpen(false)} items={commandItems} />
    </>
  );
};
