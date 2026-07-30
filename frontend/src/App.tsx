import React, { useEffect, useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Toaster } from "sonner";
import { Navbar } from "./components/Navbar";
import { DashboardPage } from "./pages/DashboardPage";
import { AgentsPage } from "./pages/AgentsPage";
import { TelemetryPage } from "./pages/TelemetryPage";
import { ReportsPage } from "./pages/ReportsPage";
import { NemotronPage } from "./pages/NemotronPage";
import { NemotronChatWidget } from "./components/NemotronChatWidget";

const BACKEND_URL = "http://localhost:8000";

export const App: React.FC = () => {
  const [statuses, setStatuses] = useState<Record<string, any>>({});
  const [logs, setLogs] = useState<any[]>([]);
  const [wsConnected, setWsConnected] = useState(false);

  const fetchStatus = async () => {
    try {
      const resp = await fetch(`${BACKEND_URL}/api/agents/status`);
      if (resp.ok) {
        const data = await resp.json();
        setStatuses(data);
        setWsConnected(true);
      }
    } catch {
      setWsConnected(false);
    }
  };

  const fetchLogs = async () => {
    try {
      const resp = await fetch(`${BACKEND_URL}/api/agents/logs?limit=50`);
      if (resp.ok) {
        const data = await resp.json();
        setLogs(data.logs || []);
      }
    } catch {
      // quiet fail
    }
  };

  useEffect(() => {
    fetchStatus();
    fetchLogs();

    let ws: WebSocket | null = null;
    try {
      ws = new WebSocket("ws://localhost:8000/ws/agents");
      ws.onopen = () => setWsConnected(true);
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === "status_snapshot") {
            setStatuses(data.agents);
          } else if (data.agent) {
            setStatuses((prev) => ({
              ...prev,
              [data.agent]: {
                ...prev[data.agent],
                name: data.agent,
                status: data.status,
                last_run_timestamp: data.timestamp,
                last_duration_ms: data.duration_ms || prev[data.agent]?.last_duration_ms,
              },
            }));
            fetchLogs();
          }
        } catch {
          // ignore
        }
      };
      ws.onclose = () => setWsConnected(false);
      ws.onerror = () => setWsConnected(false);
    } catch {
      setWsConnected(false);
    }

    return () => {
      if (ws) ws.close();
    };
  }, []);

  const handleRunPipeline = async (payload: any = {}) => {
    const finalPayload = {
      use_sample: payload.image_b64 ? false : true,
      disaster_type: payload.disaster_type || "flood",
      severity: payload.severity || 4,
      start_node: 0,
      target_node: 8,
      ...payload,
    };
    const resp = await fetch(`${BACKEND_URL}/api/agents/pipeline/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(finalPayload),
    });
    if (!resp.ok) {
      const err = await resp.json();
      throw new Error(err.detail || "Pipeline failed");
    }
    const data = await resp.json();
    await fetchStatus();
    await fetchLogs();
    return data;
  };

  const handleUploadImage = async (file: File) => {
    const formData = new FormData();
    formData.append("file", file);
    const resp = await fetch(`${BACKEND_URL}/api/agents/upload`, {
      method: "POST",
      body: formData,
    });
    if (!resp.ok) {
      const err = await resp.json();
      throw new Error(err.detail || "Upload failed");
    }
    return await resp.json();
  };

  const handleSegmentImage = async (imageB64: string) => {
    const resp = await fetch(`${BACKEND_URL}/api/agents/segment`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image_b64: imageB64 }),
    });
    if (!resp.ok) {
      const err = await resp.json();
      throw new Error(err.detail || "Segmentation failed");
    }
    return await resp.json();
  };

  const handleRunAgentStandalone = async (name: string, payload: any) => {
    const resp = await fetch(`${BACKEND_URL}/api/agents/${name}/run`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    if (!resp.ok) {
      const err = await resp.json();
      throw new Error(err.detail || `Agent ${name} run failed`);
    }
    const data = await resp.json();
    await fetchStatus();
    await fetchLogs();
    return data;
  };

  const handleGenerateReport = async () => {
    const resp = await fetch(`${BACKEND_URL}/api/agents/report`);
    if (!resp.ok) {
      const err = await resp.json();
      throw new Error(err.detail || "Report generation failed");
    }
    const data = await resp.json();
    await fetchStatus();
    await fetchLogs();
    return data;
  };

  return (
    <BrowserRouter>
      <div style={{ backgroundColor: "#050608", minHeight: "100vh", color: "#FFFFFF" }}>
        <Navbar wsConnected={wsConnected} onRunPipeline={handleRunPipeline} />
        <Toaster theme="dark" position="bottom-right" richColors />

        <main>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route
              path="/dashboard"
              element={
                <DashboardPage
                  agentStatus={statuses}
                  onRunPipeline={handleRunPipeline}
                  onUploadImage={handleUploadImage}
                  onSegmentImage={handleSegmentImage}
                />
              }
            />
            <Route
              path="/agents"
              element={
                <AgentsPage
                  agentsStatus={statuses}
                  logs={logs}
                  onRunAgentStandalone={handleRunAgentStandalone}
                />
              }
            />
            <Route path="/telemetry" element={<TelemetryPage />} />
            <Route
              path="/reports"
              element={<ReportsPage onGenerateReport={handleGenerateReport} />}
            />
            <Route path="/nemotron" element={<NemotronPage />} />
          </Routes>
        </main>
        <NemotronChatWidget />
      </div>
    </BrowserRouter>
  );
};

export default App;
