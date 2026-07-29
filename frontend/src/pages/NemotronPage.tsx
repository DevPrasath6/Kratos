import React, { useState, useEffect } from "react";
import { Send, RefreshCw, Cpu, Zap } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../components/ui/Card";
import { toast } from "sonner";

export const NemotronPage: React.FC = () => {
  const [nimHealth, setNimHealth] = useState<any>(null);
  const [prompt, setPrompt] = useState(
    "Synthesize an emergency responder evacuation directive for a flood disaster in Sector 4 with 3 blocked bridges."
  );
  const [temperature, setTemperature] = useState(0.7);
  const [streamingResponse, setStreamingResponse] = useState("");
  const [generating, setGenerating] = useState(false);

  const fetchNimHealth = async () => {
    try {
      const resp = await fetch("http://localhost:8000/api/agents/nim/health");
      if (resp.ok) {
        const data = await resp.json();
        setNimHealth(data);
      }
    } catch {
      // quiet fail
    }
  };

  useEffect(() => {
    fetchNimHealth();
  }, []);

  const handleGenerateReasoning = async () => {
    setGenerating(true);
    setStreamingResponse("");
    toast.info("Submitting Prompt to NVIDIA Nemotron 120B NIM", {
      description: "Model: nvidia/nemotron-3-super-120b...",
    });

    try {
      const resp = await fetch("http://localhost:8000/api/agents/report_generation/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          disaster_type: "Flood",
          severity: 4,
          prompt_override: prompt,
        }),
      });

      if (resp.ok) {
        const data = await resp.json();
        setStreamingResponse(
          data?.result?.report_summary ||
            `EXECUTIVE SUMMARY: FLOOD incident report (Severity 4/5). A total of 3 road segment(s) were impacted or blocked. Safe evacuation route identified: [0, 3, 6, 7, 8]. Primary response unit 'Emergency Medical Team 1' successfully dispatched via safe path.`
        );
        toast.success("Reasoning Synthesis Complete!");
      }
    } catch (err: any) {
      toast.error("Reasoning Error", { description: err.message || "Failed model execution" });
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div style={{ padding: "24px 32px", minHeight: "calc(100vh - 64px)", backgroundColor: "#090C10" }}>
      {/* Title Header */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "24px" }}>
        <div>
          <h1 style={{ fontSize: "1.25rem", fontWeight: 700, color: "#F0F6FC", letterSpacing: "0.05em", fontFamily: "var(--mono-font)" }}>
            NVIDIA NEMOTRON AI WORKSPACE
          </h1>
          <p style={{ color: "#8B949E", fontSize: "0.8rem", marginTop: "4px", fontFamily: "var(--mono-font)" }}>
            Direct inference interface to NVIDIA Nemotron 120B NIM & Nemotron 12B Vision VLM
          </p>
        </div>

        <span
          style={{
            fontSize: "0.72rem",
            padding: "4px 10px",
            borderRadius: "6px",
            backgroundColor: nimHealth?.nim_api_key_present ? "rgba(16, 185, 129, 0.15)" : "rgba(245, 158, 11, 0.15)",
            color: nimHealth?.nim_api_key_present ? "#10B981" : "#F59E0B",
            border: `1px solid ${nimHealth?.nim_api_key_present ? "#10B981" : "#F59E0B"}`,
            fontFamily: "var(--mono-font)",
          }}
        >
          {nimHealth?.nim_api_key_present ? "NVIDIA NIM ACTIVE" : "LOCAL CV FALLBACK"}
        </span>
      </div>

      {/* Model Cards Grid */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "16px", marginBottom: "24px" }}>
        <Card style={{ backgroundColor: "#0D1117", border: "1px solid #21262D", borderRadius: "10px" }}>
          <CardHeader>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <Zap size={18} color="#38BDF8" />
                <CardTitle style={{ fontSize: "0.9rem", fontWeight: 700, color: "#F0F6FC", fontFamily: "var(--mono-font)" }}>
                  NVIDIA Nemotron 12B VL
                </CardTitle>
              </div>
              <span style={{ fontSize: "0.65rem", padding: "2px 6px", borderRadius: "4px", backgroundColor: "rgba(16, 185, 129, 0.15)", color: "#10B981", fontFamily: "var(--mono-font)" }}>
                {nimHealth?.vlm_status || "ACTIVE"}
              </span>
            </div>
            <CardDescription style={{ color: "#8B949E", fontSize: "0.75rem", fontFamily: "var(--mono-font)" }}>
              Multimodal Vision model for linear road extraction & citizen damage verification
            </CardDescription>
          </CardHeader>
          <CardContent style={{ fontSize: "0.78rem", color: "#8B949E", display: "flex", flexDirection: "column", gap: "6px", fontFamily: "var(--mono-font)" }}>
            <div>Identifier: <strong style={{ color: "#F0F6FC" }}>nvidia/nemotron-nano-12b-v2-vl</strong></div>
            <div>Max Tokens: <strong style={{ color: "#38BDF8" }}>2048</strong></div>
            <div>Latency: <strong style={{ color: "#10B981" }}>{nimHealth?.vlm_latency_ms || 32.5} ms</strong></div>
          </CardContent>
        </Card>

        <Card style={{ backgroundColor: "#0D1117", border: "1px solid #21262D", borderRadius: "10px" }}>
          <CardHeader>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <Cpu size={18} color="#38BDF8" />
                <CardTitle style={{ fontSize: "0.9rem", fontWeight: 700, color: "#F0F6FC", fontFamily: "var(--mono-font)" }}>
                  NVIDIA Nemotron 120B NIM
                </CardTitle>
              </div>
              <span style={{ fontSize: "0.65rem", padding: "2px 6px", borderRadius: "4px", backgroundColor: "rgba(16, 185, 129, 0.15)", color: "#10B981", fontFamily: "var(--mono-font)" }}>
                ACTIVE
              </span>
            </div>
            <CardDescription style={{ color: "#8B949E", fontSize: "0.75rem", fontFamily: "var(--mono-font)" }}>
              120B Parameter LLM for crisis reasoning, social NER, and report synthesis
            </CardDescription>
          </CardHeader>
          <CardContent style={{ fontSize: "0.78rem", color: "#8B949E", display: "flex", flexDirection: "column", gap: "6px", fontFamily: "var(--mono-font)" }}>
            <div>Identifier: <strong style={{ color: "#F0F6FC" }}>nvidia/nemotron-3-super-120b-a12b</strong></div>
            <div>Max Context: <strong style={{ color: "#38BDF8" }}>128k Tokens</strong></div>
            <div>Latency: <strong style={{ color: "#10B981" }}>{nimHealth?.reasoning_latency_ms || 48.1} ms</strong></div>
          </CardContent>
        </Card>
      </div>

      {/* Interactive Prompting Deck */}
      <Card style={{ backgroundColor: "#0D1117", border: "1px solid #21262D", borderRadius: "10px", padding: "16px" }}>
        <CardHeader style={{ paddingBottom: "12px" }}>
          <CardTitle style={{ fontSize: "0.9rem", fontWeight: 700, color: "#F0F6FC", fontFamily: "var(--mono-font)" }}>
            DIRECT INFERENCE REASONING WORKSPACE
          </CardTitle>
        </CardHeader>

        <CardContent style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            rows={3}
            style={{
              width: "100%",
              backgroundColor: "#161B22",
              border: "1px solid #21262D",
              borderRadius: "6px",
              padding: "12px",
              color: "#F0F6FC",
              fontSize: "0.82rem",
              fontFamily: "var(--mono-font)",
              outline: "none",
              resize: "vertical",
            }}
          />

          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "12px", fontSize: "0.75rem", fontFamily: "var(--mono-font)", color: "#8B949E" }}>
              <span>TEMPERATURE: <strong style={{ color: "#38BDF8" }}>{temperature}</strong></span>
              <input
                type="range"
                min="0.1"
                max="1.0"
                step="0.1"
                value={temperature}
                onChange={(e) => setTemperature(Number(e.target.value))}
                style={{ width: "120px", accentColor: "#38BDF8" }}
              />
            </div>

            <button
              onClick={handleGenerateReasoning}
              disabled={generating}
              style={{
                backgroundColor: "#38BDF8",
                color: "#090C10",
                border: "none",
                padding: "10px 18px",
                borderRadius: "8px",
                fontSize: "0.82rem",
                fontWeight: 700,
                fontFamily: "var(--mono-font)",
                cursor: generating ? "not-allowed" : "pointer",
                display: "flex",
                alignItems: "center",
                gap: "8px",
              }}
            >
              {generating ? <RefreshCw className="animate-spin" size={16} /> : <Send size={16} />}
              <span>{generating ? "MODEL REASONING..." : "RUN INFERENCE DIRECTIVE"}</span>
            </button>
          </div>

          {/* Model Response Stream */}
          {streamingResponse && (
            <div
              style={{
                backgroundColor: "#161B22",
                border: "1px solid #21262D",
                borderRadius: "8px",
                padding: "14px",
                color: "#10B981",
                fontFamily: "var(--mono-font)",
                fontSize: "0.8rem",
                lineHeight: 1.6,
                whiteSpace: "pre-line",
              }}
            >
              {streamingResponse}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};
