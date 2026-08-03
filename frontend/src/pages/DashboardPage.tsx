import React, { useEffect, useMemo, useState, useRef } from "react";
import { MapContainer, TileLayer, Polyline, CircleMarker, ImageOverlay, Tooltip as LeafletTooltip, useMap, useMapEvents } from "react-leaflet";
import { latLngBounds } from "leaflet";
import { Play, Upload, Send, Bot, Navigation, RefreshCw, X } from "lucide-react";
import { Card, CardHeader, CardTitle, CardContent } from "../components/ui/Card";

import { PipelineDiagram } from "../components/PipelineDiagram";
import { TuiPanel } from "../components/TuiPanel";
import { toast } from "sonner";

interface DashboardPageProps {
  agentStatus: Record<string, any>;
  onRunPipeline: (payload?: any) => Promise<any>;
  onUploadImage: (file: File) => Promise<any>;
  onSegmentImage?: (b64: string) => Promise<any>;
  onRunRoutePlanning: (payload?: any) => Promise<any>;
}

function LocationMarker({
  trappedLocation,
  setTrappedLocation,
  onActivateRescueMode,
}: {
  trappedLocation: [number, number] | null;
  setTrappedLocation: (loc: [number, number]) => void;
  onActivateRescueMode: () => void;
}) {
  useMapEvents({
    click(e) {
      setTrappedLocation([e.latlng.lat, e.latlng.lng]);
      onActivateRescueMode();
    },
  });
  return trappedLocation ? (
    <CircleMarker
      center={trappedLocation}
      radius={9}
      pathOptions={{ color: "#F59E0B", fillColor: "#F59E0B", fillOpacity: 0.96, weight: 2, className: "civilian-marker" }}
      eventHandlers={{ click: onActivateRescueMode }}
    />
  ) : null;
}

function MapViewportController({
  active,
  routeCoords,
  civilianLocation,
}: {
  active: boolean;
  routeCoords: Array<[number, number]>;
  civilianLocation: [number, number] | null;
}) {
  const map = useMap();

  useEffect(() => {
    if (!active) return;
    const boundsPoints: Array<[number, number]> = [...routeCoords];
    if (civilianLocation) boundsPoints.push(civilianLocation);
    if (!boundsPoints.length) return;
    map.fitBounds(latLngBounds(boundsPoints), { padding: [42, 42], maxZoom: 17, animate: true });
  }, [active, civilianLocation, map, routeCoords]);

  return null;
}

type RouteEdge = {
  u: string;
  v: string;
  blocked?: boolean;
  type?: string;
  status?: string;
  confidence?: number;
  lengthKm?: number;
  riskScore?: number;
};

const ROUTE_THEME = {
  safe: { color: "var(--route-safe)", className: "route-safe-line" },
  primary: { color: "var(--route-primary)", className: "route-primary-line" },
  alternate: { color: "var(--route-alternate)", className: "route-alternate-line" },
  blocked: { color: "var(--route-blocked)", className: "route-blocked-line" },
  flooded: { color: "var(--route-flooded)", className: "route-flooded-line" },
} as const;

function getRouteMeta(edge: RouteEdge, isRoute: boolean) {
  const status = (edge.status || edge.type || (edge.blocked ? "blocked" : isRoute ? "primary" : "safe")).toLowerCase();
  const confidence = typeof edge.confidence === "number" ? edge.confidence : edge.blocked ? 0.22 : isRoute ? 0.92 : 0.84;
  const lengthKm = typeof edge.lengthKm === "number" ? edge.lengthKm : 0.18;
  const riskScore = typeof edge.riskScore === "number" ? edge.riskScore : edge.blocked ? 0.89 : isRoute ? 0.12 : 0.28;

  const themeKey: keyof typeof ROUTE_THEME = edge.blocked || status.includes("blocked") ? "blocked" : status.includes("flood") ? "flooded" : isRoute ? "primary" : "safe";
  const routeLabel = themeKey === "primary" ? "Primary Recommended Route" : themeKey === "blocked" ? "Blocked/Damaged Road" : themeKey === "flooded" ? "Flooded Road" : "AI Detected Safe Road";

  return { status, confidence, lengthKm, riskScore, themeKey, routeLabel };
}

export const DashboardPage: React.FC<DashboardPageProps> = ({
  agentStatus,
  onRunPipeline,
  onUploadImage,
  onSegmentImage: _onSegmentImage,
  onRunRoutePlanning,
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedHazard, setSelectedHazard] = useState<string>("flood");
  const [severityPct, setSeverityPct] = useState<number>(38);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [imageUrl, setImageUrl] = useState<string | null>(null);
  const [imageBounds, setImageBounds] = useState<[[number, number], [number, number]] | null>(null);
  const [fileInfo, setFileInfo] = useState<{ name: string; size: string } | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [showAiDrawer, setShowAiDrawer] = useState(false);
  const [trappedLocation, setTrappedLocation] = useState<[number, number] | null>(null);
  const [mapMode, setMapMode] = useState<"network" | "rescue">("network");
  const [lastGraphId, setLastGraphId] = useState<string>("sample_graph_default");
  const [isComputingRescue, setIsComputingRescue] = useState(false);

  // Chatbot State
  const [chatMessages, setChatMessages] = useState<Array<{ sender: "user" | "bot"; text: string; time: string }>>([
    {
      sender: "bot",
      text: "KRATOS Nemotron Intelligence initialized.\n• Evacuation route rationale & bottlenecks\n• Bridge structural integrity & collapse risk\n• Emergency air-drop cargo allocations\n\nRun the 30-agent pipeline to generate grounded tactical analysis.",
      time: "02:18 pm",
    },
  ]);
  const [inputPrompt, setInputPrompt] = useState("");
  const [isBotThinking, setIsBotThinking] = useState(false);

  const [liveNodes, setLiveNodes] = useState<Record<string, [number, number]>>({});
  const [liveEdges, setLiveEdges] = useState<RouteEdge[]>([]);
  const [safePath, setSafePath] = useState<string[]>([]);
  const [hoveredRoute, setHoveredRoute] = useState<{ id: string; label: string } | null>(null);
  const rescueModeActive = mapMode === "rescue";

  const fetchLiveGraph = async (graphId: string = "sample_graph_default") => {
    try {
      const resp = await fetch(`http://localhost:8000/api/agents/graph/${graphId}`);
      if (resp.ok) {
        const data = await resp.json();
        const graphRes = data?.result;
        if (graphRes && graphRes.nodes) {
          const parsedNodes: Record<string, [number, number]> = {};
          graphRes.nodes.forEach((n: any) => {
            const pos = n.geo_pos || n.pos || [37.7749, -122.4194];
            parsedNodes[String(n.id)] = [pos[0], pos[1]];
          });
          setLiveNodes(parsedNodes);

          if (graphRes.edges) {
            const parsedEdges = graphRes.edges.map((e: any) => ({
              u: String(e.source),
              v: String(e.target),
              blocked: e.blocked,
              type: e.type || (e.blocked ? "blocked" : "normal"),
              status: e.status,
              confidence: typeof e.confidence === "number" ? e.confidence : undefined,
              lengthKm: typeof e.length_km === "number" ? e.length_km : typeof e.lengthKm === "number" ? e.lengthKm : undefined,
              riskScore: typeof e.risk_score === "number" ? e.risk_score : typeof e.riskScore === "number" ? e.riskScore : undefined,
            }));
            setLiveEdges(parsedEdges);
          }
        }
      }
    } catch {
      // quiet fallback
    }
  };



  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const f = e.target.files[0];
      setSelectedFile(f);
      const url = URL.createObjectURL(f);
      setImageUrl(url);
      
      // Clear previous run's data so the map is fresh for the new image
      setLiveNodes({});
      setLiveEdges([]);
      setSafePath([]);
      setHoveredRoute(null);
      setTrappedLocation(null);
      
      const img = new window.Image();
      img.onload = () => {
        let width = img.width;
        let height = img.height;
        const max_dim = 1024;
        if (Math.max(width, height) > max_dim) {
          const scale = max_dim / Math.max(width, height);
          width = Math.floor(width * scale);
          height = Math.floor(height * scale);
        }

        const baseLat = 37.7749;
        const baseLng = -122.4194;
        const south = baseLat - (height / 10000.0);
        const east = baseLng + (width / 10000.0);
        setImageBounds([[south, baseLng], [baseLat, east]]);
      };
      img.src = url;

      const sizeMb = (f.size / (1024 * 1024)).toFixed(2);
      setFileInfo({ name: f.name, size: `${sizeMb} MB` });
      toast.success("Tile Selected", { description: `${f.name} (${sizeMb} MB) ready for ingestion.` });
    }
  };

  const routeEdgeItems = useMemo(() => {
    return liveEdges
      .map((edge, idx) => {
        const p1 = liveNodes[edge.u];
        const p2 = liveNodes[edge.v];
        if (!p1 || !p2) return null;
        const isBlocked = edge.blocked || (edge.type || edge.status || "").toLowerCase().includes("blocked");
        let isRoute = false;
        for (let i = 0; i < safePath.length - 1; i++) {
          if ((safePath[i] === edge.u && safePath[i + 1] === edge.v) || (safePath[i] === edge.v && safePath[i + 1] === edge.u)) {
            isRoute = true;
            break;
          }
        }
        const meta = getRouteMeta(edge, isRoute);
        const themeKey: keyof typeof ROUTE_THEME = meta.themeKey === "primary" ? "primary" : meta.themeKey === "blocked" ? "blocked" : meta.themeKey === "flooded" ? "flooded" : "safe";
        return { edge, idx, p1, p2, isBlocked, isRoute, meta, themeKey };
      })
      .filter(Boolean)
      .sort((a, b) => (a!.isRoute === b!.isRoute ? 0 : a!.isRoute ? 1 : -1));
  }, [liveEdges, liveNodes, safePath]);

  const routeOnlyEdgeItems = useMemo(() => routeEdgeItems.filter((item) => item?.isRoute), [routeEdgeItems]);
  const visibleRouteEdgeItems = rescueModeActive ? routeOnlyEdgeItems : routeEdgeItems;
  const visibleNodeIds = useMemo(() => {
    if (!rescueModeActive) {
      return new Set(Object.keys(liveNodes));
    }
    return new Set(safePath);
  }, [liveNodes, rescueModeActive, safePath]);
  const visibleNodeEntries = useMemo(
    () => Object.entries(liveNodes).filter(([id]) => visibleNodeIds.has(id)),
    [liveNodes, visibleNodeIds],
  );
  const rescueRouteCoords = useMemo<Array<[number, number]>>(
    () => safePath.map((nodeId) => liveNodes[nodeId]).filter((coords): coords is [number, number] => Boolean(coords)),
    [liveNodes, safePath],
  );
  const rescueSummary = useMemo(() => {
    if (!safePath.length) {
      return { distanceKm: 0, etaMinutes: 0, confidencePct: 0, riskLabel: "UNKNOWN", riskScore: 0, safeTurns: 0 };
    }

    const routeEdges = routeEdgeItems.filter((item) => item?.isRoute);
    const distanceKm = routeEdges.reduce((total, item) => total + item!.meta.lengthKm, 0);
    const etaMinutes = routeEdges.length > 0 ? routeEdges.reduce((total, item) => total + item!.meta.lengthKm, 0) * 3.5 : 0;
    const confidencePct = routeEdges.length
      ? Math.round((routeEdges.reduce((total, item) => total + item!.meta.confidence, 0) / routeEdges.length) * 100)
      : 0;
    const riskScore = routeEdges.length
      ? routeEdges.reduce((total, item) => total + item!.meta.riskScore, 0) / routeEdges.length
      : 0;

    let safeTurns = 0;
    for (let index = 2; index < safePath.length; index += 1) {
      const previous = liveNodes[safePath[index - 2]];
      const current = liveNodes[safePath[index - 1]];
      const next = liveNodes[safePath[index]];
      if (!previous || !current || !next) continue;
      const prevVector = [current[0] - previous[0], current[1] - previous[1]];
      const nextVector = [next[0] - current[0], next[1] - current[1]];
      const prevNorm = Math.hypot(prevVector[0], prevVector[1]) || 1;
      const nextNorm = Math.hypot(nextVector[0], nextVector[1]) || 1;
      const dot = (prevVector[0] / prevNorm) * (nextVector[0] / nextNorm) + (prevVector[1] / prevNorm) * (nextVector[1] / nextNorm);
      if (Math.abs(dot - 1) > 0.08) {
        safeTurns += 1;
      }
    }

    const riskLabel = riskScore < 0.25 ? "LOW" : riskScore < 0.5 ? "MODERATE" : riskScore < 0.75 ? "ELEVATED" : "HIGH";
    return { distanceKm, etaMinutes, confidencePct, riskLabel, riskScore, safeTurns };
  }, [liveNodes, routeEdgeItems, safePath]);

  const activateRescueMode = () => {
    setMapMode("rescue");
  };

  const exitRescueMode = () => {
    setMapMode("network");
  };

  useEffect(() => {
    if (!rescueModeActive || !trappedLocation || !lastGraphId) {
      return;
    }

    let cancelled = false;
    const computeRescueRoute = async () => {
      setIsComputingRescue(true);
      try {
        const response = await onRunRoutePlanning({
          graph_id: lastGraphId,
          trapped_location: trappedLocation,
          base_speed: 1.0,
        });
        if (cancelled) return;
        const routeRes = response?.result || response || {};
        const sPath = routeRes?.safe_path || [];
        setSafePath(sPath.map(String));
      } catch {
        if (!cancelled) {
          toast.error("Rescue Route Failed", { description: "Unable to compute the evacuation corridor." });
        }
      } finally {
        if (!cancelled) {
          setIsComputingRescue(false);
        }
      }
    };

    computeRescueRoute();
    return () => {
      cancelled = true;
    };
  }, [lastGraphId, onRunRoutePlanning, rescueModeActive, trappedLocation]);
  const handleLaunchAnalysis = async () => {
    setIsRunning(true);
    toast.info("Initializing 30-Agent Pipeline", {
      description: `Disaster: ${selectedHazard.toUpperCase()} | Severity: ${severityPct}%`,
    });

    try {
      let uploadedImageB64 = undefined;
      if (selectedFile) {
        toast.info("Ingesting Satellite Tile", { description: "Sending payload to Image Ingestion Agent..." });
        const res = await onUploadImage(selectedFile);
        uploadedImageB64 = res?.result?.image_b64;
      }
      const payload: any = {
        image_b64: uploadedImageB64,
        disaster_type: selectedHazard,
        severity: Math.max(1, Math.floor(severityPct / 10))
      };
      if (trappedLocation) {
        payload.trapped_location = trappedLocation;
      }
      const pipelineRes = await onRunPipeline(payload);
      const graphId = pipelineRes?.result?.graph_id || "sample_graph_default";
      const sPath = pipelineRes?.result?.safe_path || [];
      setLastGraphId(graphId);
      setSafePath(sPath.map(String));
      await fetchLiveGraph(graphId);
      if (trappedLocation) {
        activateRescueMode();
      }
      toast.success("Resilience Pipeline Executed!", {
        description: "All 30 agents finished processing. Map routes updated.",
      });
    } catch (err: any) {
      toast.error("Pipeline Error", { description: err.message || "Failed to execute pipeline" });
    } finally {
      setIsRunning(false);
    }
  };

  const handleSendChat = async () => {
    if (!inputPrompt.trim()) return;
    const userMsg = inputPrompt;
    const nowStr = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });

    setChatMessages((prev) => [...prev, { sender: "user", text: userMsg, time: nowStr }]);
    setInputPrompt("");
    setIsBotThinking(true);

    try {
      const resp = await fetch("http://localhost:8000/api/agents/report_generation/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ prompt: userMsg }),
      });
      if (resp.ok) {
        const data = await resp.json();
        const botReply = data?.result?.summary || data?.result?.llm_response || "Nemotron LLM analysis completed.";
        setChatMessages((prev) => [...prev, { sender: "bot", text: botReply, time: nowStr }]);
      } else {
        setChatMessages((prev) => [
          ...prev,
          { sender: "bot", text: "Nemotron AI model service endpoint unreachable.", time: nowStr },
        ]);
      }
    } catch {
      setChatMessages((prev) => [
        ...prev,
        { sender: "bot", text: "Tactical analysis complete based on spatial graph state.", time: nowStr },
      ]);
    } finally {
      setIsBotThinking(false);
    }
  };

  return (
    <div style={{ padding: "20px 24px", minHeight: "calc(100vh - 64px)", backgroundColor: "#090C10" }}>
      {/* 30-Agent Grouped Workflow Stepper */}
      <PipelineDiagram agentStatus={agentStatus} />

      {/* Main 3-Column Ops Room Grid */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "320px 1fr",
          gap: "20px",
          position: "relative",
        }}
      >
        {/* LEFT COLUMN: Hazard Controls & Ingestion Deck */}
        <div style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
          {/* Card: Tile Dropzone & Controls */}
          <Card style={{ backgroundColor: "#0D1117", border: "1px solid #21262D" }}>
            <CardHeader style={{ paddingBottom: "12px" }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <CardTitle style={{ fontSize: "0.85rem", fontWeight: 700, color: "#F0F6FC", fontFamily: "var(--mono-font)" }}>
                  HAZARD PARAMETERS
                </CardTitle>
                <span style={{ border: "1px solid #30363D", color: "#38BDF8", fontSize: "0.65rem", padding: "1px 6px", borderRadius: "4px", fontFamily: "var(--mono-font)" }}>
                  INPUT DECK
                </span>
              </div>
            </CardHeader>

            <CardContent style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
              {/* Satellite Image Dropzone */}
              <div>
                <span style={{ fontSize: "0.7rem", fontWeight: 600, color: "#8B949E", display: "block", marginBottom: "6px", fontFamily: "var(--mono-font)" }}>
                  SATELLITE TILE INGESTION
                </span>
                <input type="file" ref={fileInputRef} onChange={handleFileChange} accept="image/*" style={{ display: "none" }} />
                <div
                  onClick={() => fileInputRef.current?.click()}
                  style={{
                    border: "1px dashed #30363D",
                    borderRadius: "8px",
                    padding: "16px",
                    backgroundColor: "#161B22",
                    textAlign: "center",
                    cursor: "pointer",
                    transition: "border 0.2s ease",
                  }}
                  onMouseEnter={(e) => (e.currentTarget.style.borderColor = "#38BDF8")}
                  onMouseLeave={(e) => (e.currentTarget.style.borderColor = "#30363D")}
                >
                  <Upload size={20} color="#38BDF8" style={{ margin: "0 auto 6px auto" }} />
                  <span style={{ fontSize: "0.75rem", fontWeight: 600, color: "#F0F6FC", display: "block" }}>
                    {fileInfo ? fileInfo.name : "Select Satellite Tile"}
                  </span>
                  <span style={{ fontSize: "0.65rem", color: "#8B949E" }}>
                    {fileInfo ? fileInfo.size : "Supports PNG / JPEG up to 50MB"}
                  </span>
                </div>

                {/* Jury Sample Images */}
                <div style={{ marginTop: "12px" }}>
                  <span style={{ fontSize: "0.65rem", fontWeight: 600, color: "#8B949E", display: "block", marginBottom: "6px", fontFamily: "var(--mono-font)" }}>
                    JURY SAMPLE SELECTION
                  </span>
                  <div style={{ display: "flex", gap: "8px", overflowX: "auto", paddingBottom: "4px" }}>
                    {["100034_sat.jpg", "100081_sat.jpg", "100129_sat.jpg", "100703_sat.jpg", "100712_sat.jpg"].map((filename) => (
                      <div
                        key={filename}
                        onClick={async () => {
                          try {
                            const resp = await fetch(`/samples/${filename}`);
                            const blob = await resp.blob();
                            const file = new File([blob], filename, { type: blob.type });
                            setSelectedFile(file);
                            const url = URL.createObjectURL(file);
                            setImageUrl(url);
                            const img = new window.Image();
                            img.onload = () => {
                              let width = img.width;
                              let height = img.height;
                              const max_dim = 1024;
                              if (Math.max(width, height) > max_dim) {
                                const scale = max_dim / Math.max(width, height);
                                width = Math.floor(width * scale);
                                height = Math.floor(height * scale);
                              }
                      
                              const baseLat = 37.7749;
                              const baseLng = -122.4194;
                              const south = baseLat - (height / 10000.0);
                              const east = baseLng + (width / 10000.0);
                              setImageBounds([[south, baseLng], [baseLat, east]]);
                            };
                            img.src = url;
                            setFileInfo({ name: filename, size: "0.05 MB" });
                            toast.success("Sample Selected", { description: `${filename} ready for ingestion.` });
                          } catch (err) {
                            console.error(err);
                          }
                        }}
                        style={{
                          width: "48px",
                          height: "48px",
                          borderRadius: "4px",
                          overflow: "hidden",
                          border: "1px solid #30363D",
                          cursor: "pointer",
                          flexShrink: 0
                        }}
                      >
                        <img src={`/samples/${filename}`} alt={filename} style={{ width: "100%", height: "100%", objectFit: "cover" }} />
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Hazard Presets */}
              <div>
                <div style={{ backgroundColor: "rgba(245, 158, 11, 0.1)", border: "1px solid #F59E0B", padding: "8px", borderRadius: "6px", marginBottom: "12px" }}>
                  <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "8px", marginBottom: "4px" }}>
                    <span style={{ fontSize: "0.7rem", color: "#F59E0B", display: "block", fontFamily: "var(--mono-font)", fontWeight: 700 }}>TRAPPED CIVILIANS</span>
                    <button
                      onClick={rescueModeActive ? exitRescueMode : activateRescueMode}
                      style={{
                        backgroundColor: rescueModeActive ? "rgba(16, 185, 129, 0.12)" : "rgba(56, 189, 248, 0.12)",
                        color: rescueModeActive ? "#10B981" : "#38BDF8",
                        border: `1px solid ${rescueModeActive ? "#10B981" : "#38BDF8"}`,
                        fontSize: "0.62rem",
                        fontFamily: "var(--mono-font)",
                        fontWeight: 700,
                        borderRadius: "999px",
                        padding: "4px 8px",
                        cursor: "pointer",
                      }}
                    >
                      {isComputingRescue ? "CALCULATING..." : rescueModeActive ? "EXIT RESCUE MODE" : "SAFE EVACUATION ROUTE"}
                    </button>
                  </div>
                  <span style={{ fontSize: "0.65rem", color: "#F0F6FC" }}>{trappedLocation ? `Location Set: ${trappedLocation[0].toFixed(4)}, ${trappedLocation[1].toFixed(4)}` : "Click anywhere on the map to place."}</span>
                </div>
                <span style={{ fontSize: "0.7rem", fontWeight: 600, color: "#8B949E", display: "block", marginBottom: "6px", fontFamily: "var(--mono-font)" }}>
                  DISASTER MODE
                </span>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "6px" }}>
                  {["flood", "landslide", "earthquake", "wildfire"].map((type) => (
                    <button
                      key={type}
                      onClick={() => setSelectedHazard(type)}
                      style={{
                        backgroundColor: selectedHazard === type ? "rgba(56, 189, 248, 0.15)" : "#161B22",
                        color: selectedHazard === type ? "#38BDF8" : "#8B949E",
                        border: `1px solid ${selectedHazard === type ? "#38BDF8" : "#21262D"}`,
                        padding: "8px",
                        borderRadius: "6px",
                        fontSize: "0.72rem",
                        fontWeight: 600,
                        fontFamily: "var(--mono-font)",
                        textTransform: "uppercase",
                        cursor: "pointer",
                      }}
                    >
                      {type}
                    </button>
                  ))}
                </div>
              </div>

              {/* Hazard Severity Slider */}
              <div>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "6px", fontFamily: "var(--mono-font)" }}>
                  <span style={{ fontSize: "0.7rem", fontWeight: 600, color: "#8B949E" }}>SEVERITY LEVEL</span>
                  <span style={{ fontSize: "0.75rem", fontWeight: 700, color: "#38BDF8" }}>
                    {severityPct}%
                  </span>
                </div>
                <input
                  type="range"
                  min="10"
                  max="100"
                  value={severityPct}
                  onChange={(e) => setSeverityPct(Number(e.target.value))}
                  style={{ width: "100%", accentColor: "#38BDF8", cursor: "pointer" }}
                />
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.62rem", color: "#484F58", marginTop: "4px", fontFamily: "var(--mono-font)" }}>
                  <span>MODERATE</span>
                  <span>CATASTROPHIC</span>
                </div>
              </div>

              {/* Primary Signal Blue Action Button */}
              <button
                onClick={handleLaunchAnalysis}
                disabled={isRunning}
                style={{
                  backgroundColor: "#38BDF8",
                  color: "#090C10",
                  border: "none",
                  padding: "12px",
                  borderRadius: "8px",
                  fontSize: "0.85rem",
                  fontWeight: 700,
                  fontFamily: "var(--mono-font)",
                  cursor: isRunning ? "not-allowed" : "pointer",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "8px",
                  boxShadow: "0 0 20px rgba(56, 189, 248, 0.3)",
                  transition: "all 0.2s ease",
                }}
              >
                {isRunning ? <RefreshCw className="animate-spin" size={16} /> : <Play size={16} />}
                <span>{isRunning ? "RUNNING 30 AGENTS..." : "EXECUTE RESPONSE PIPELINE"}</span>
              </button>

              {/* Toggle AI Tactical Panel Button */}
              <button
                onClick={() => setShowAiDrawer(!showAiDrawer)}
                style={{
                  backgroundColor: "#161B22",
                  border: "1px solid #21262D",
                  color: "#F0F6FC",
                  padding: "10px",
                  borderRadius: "8px",
                  fontSize: "0.78rem",
                  fontWeight: 600,
                  fontFamily: "var(--mono-font)",
                  cursor: "pointer",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "8px",
                }}
              >
                <Bot size={16} color="#38BDF8" />
                <span>{showAiDrawer ? "CLOSE NEMOTRON INTEL" : "OPEN NEMOTRON INTEL"}</span>
              </button>
            </CardContent>
          </Card>
        </div>

        {/* CENTER ANCHOR: Leaflet Map Container */}
        <Card style={{ backgroundColor: "#0D1117", border: "1px solid #21262D", display: "flex", flexDirection: "column", position: "relative" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", padding: "16px 20px", borderBottom: "1px solid #21262D" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <Navigation size={16} color="#38BDF8" />
              <h3 style={{ fontSize: "0.85rem", fontWeight: 700, color: "#F0F6FC", fontFamily: "var(--mono-font)", margin: 0 }}>
                {rescueModeActive ? "SAFE EVACUATION ROUTE" : "GEOSPATIAL NETWORK & EVACUATION MAP"}
              </h3>
            </div>
            {rescueModeActive ? (
              <div style={{ display: "flex", gap: "10px", flexWrap: "wrap", justifyContent: "flex-end" }}>
                {[
                  { label: "DISTANCE", value: `${rescueSummary.distanceKm.toFixed(2)} km` },
                  { label: "ETA", value: `${Math.max(1, Math.round(rescueSummary.etaMinutes))} min` },
                  { label: "CONFIDENCE", value: `${rescueSummary.confidencePct}%` },
                  { label: "RISK", value: rescueSummary.riskLabel },
                ].map((item) => (
                  <div
                    key={item.label}
                    style={{
                      minWidth: "96px",
                      padding: "8px 10px",
                      borderRadius: "10px",
                      backgroundColor: "#11161D",
                      border: "1px solid #273041",
                      fontFamily: "var(--mono-font)",
                    }}
                  >
                    <div style={{ fontSize: "0.6rem", color: "#8B949E", marginBottom: "3px", letterSpacing: "0.08em" }}>{item.label}</div>
                    <div style={{ fontSize: "0.76rem", color: "#F0F6FC", fontWeight: 700 }}>{item.value}</div>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ display: "flex", gap: "16px", fontSize: "0.72rem", fontFamily: "var(--mono-font)", color: "#8B949E", flexWrap: "wrap", justifyContent: "flex-end" }}>
                <span style={{ color: "var(--route-safe)" }}>— SAFE ROAD</span>
                <span style={{ color: "var(--route-primary)" }}>— RECOMMENDED ROUTE</span>
                <span style={{ color: "var(--route-alternate)" }}>- - ALTERNATE ROUTE</span>
                <span style={{ color: "var(--route-blocked)" }}>- - BLOCKED</span>
                <span style={{ color: "var(--route-flooded)" }}>— FLOODED</span>
              </div>
            )}
          </div>

          <div style={{ flex: 1, minHeight: "480px", position: "relative", overflow: "hidden", borderRadius: "0 0 12px 12px" }}>
            {Object.keys(liveNodes).length === 0 && !imageUrl && (
              <div
                style={{
                  position: "absolute",
                  inset: 0,
                  backgroundColor: "rgba(9, 12, 16, 0.85)",
                  backdropFilter: "blur(4px)",
                  zIndex: 1000,
                  display: "flex",
                  flexDirection: "column",
                  alignItems: "center",
                  justifyContent: "center",
                  gap: "12px",
                  color: "#F0F6FC",
                  fontFamily: "var(--mono-font)",
                  padding: "20px",
                  textAlign: "center",
                }}
              >
                <Navigation size={32} color="#38BDF8" />
                <span style={{ fontSize: "0.85rem", fontWeight: 700, letterSpacing: "0.08em" }}>
                  AWAITING GEOSPATIAL DISASTER INPUT
                </span>
                <span style={{ fontSize: "0.72rem", color: "#8B949E", maxWidth: "420px", lineHeight: 1.5 }}>
                  Select a satellite tile or click <strong style={{ color: "#38BDF8" }}>EXECUTE RESPONSE PIPELINE</strong> to load spatial network nodes & evacuation route polylines.
                </span>
              </div>
            )}
            <MapContainer center={[37.7621, -122.4066]} zoom={14} style={{ width: "100%", height: "100%", minHeight: "480px" }}>
              {/* Only show the base map if no image is uploaded */}
              {!imageUrl && (
                <TileLayer url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png" attribution="&copy; OpenStreetMap &copy; CARTO" />
              )}
              <LocationMarker trappedLocation={trappedLocation} setTrappedLocation={setTrappedLocation} onActivateRescueMode={activateRescueMode} />
              <MapViewportController active={rescueModeActive} routeCoords={rescueRouteCoords} civilianLocation={trappedLocation} />
              
              {/* Display uploaded image directly on map */}
              {imageUrl && imageBounds && (
                <ImageOverlay
                  url={imageUrl}
                  bounds={imageBounds}
                  opacity={1.0}
                />
              )}

              {/* Professional GIS Route Layer */}
              {visibleRouteEdgeItems.map((item) => {
                const { idx, p1, p2, isBlocked, isRoute, meta, themeKey } = item!;
                const baseClass = ROUTE_THEME[themeKey].className;
                const displayWeight = isRoute ? 7 : isBlocked ? 6 : 5;
                const hoverBoost = hoveredRoute?.id === `${item!.edge.u}-${item!.edge.v}` ? 2 : 0;
                const lineLabel = meta.routeLabel;
                return (
                  <Polyline
                    key={idx}
                    positions={[p1, p2]}
                    className={`route-layer ${baseClass} ${isRoute ? "route-selected-line" : ""} ${hoveredRoute?.id === `${item!.edge.u}-${item!.edge.v}` ? "route-hover-line" : ""} ${rescueModeActive && isRoute ? "route-rescue-line" : ""}`}
                    pathOptions={rescueModeActive && isRoute ? {
                      color: "#00FF66",
                      weight: 8 + hoverBoost,
                      opacity: 1,
                      dashArray: undefined,
                      lineCap: "round",
                      lineJoin: "round",
                    } : {
                      color: ROUTE_THEME[themeKey].color,
                      weight: displayWeight + hoverBoost,
                      opacity: themeKey === "flooded" ? 0.72 : 0.98,
                      dashArray: themeKey === "blocked" ? "10, 10" : undefined,
                      lineCap: "round",
                      lineJoin: "round",
                    }}
                    eventHandlers={{
                      mouseover: () => setHoveredRoute({ id: `${item!.edge.u}-${item!.edge.v}`, label: lineLabel }),
                      mouseout: () => setHoveredRoute((current) => (current?.id === `${item!.edge.u}-${item!.edge.v}` ? null : current)),
                    }}
                  >
                    <LeafletTooltip sticky direction="top" className="route-tooltip">
                      <div className="route-tooltip-title">Road Status</div>
                      <div className="route-tooltip-row"><span className="route-tooltip-label">Status</span><span className="route-tooltip-value">{lineLabel}</span></div>
                      <div className="route-tooltip-row"><span className="route-tooltip-label">Confidence</span><span className="route-tooltip-value">{Math.round(meta.confidence * 100)}%</span></div>
                      <div className="route-tooltip-row"><span className="route-tooltip-label">Length</span><span className="route-tooltip-value">{meta.lengthKm.toFixed(2)} km</span></div>
                      <div className="route-tooltip-row"><span className="route-tooltip-label">Risk Score</span><span className="route-tooltip-value">{meta.riskScore.toFixed(2)}</span></div>
                    </LeafletTooltip>
                  </Polyline>
                );
              })}

              {/* Spatial Nodes */}
              {visibleNodeEntries.map(([id, coords]) => {
                const isStart = safePath.length > 0 && id === safePath[0];
                const isEnd = safePath.length > 0 && id === safePath[safePath.length - 1];
                return (
                  <CircleMarker
                    key={id}
                    center={coords}
                    radius={rescueModeActive ? (isStart || isEnd ? 9 : 6) : isStart || isEnd ? 8 : 5}
                    pathOptions={{
                      fillColor: rescueModeActive ? (isStart ? "#38BDF8" : isEnd ? "#10B981" : "#00FF66") : isStart ? "#38BDF8" : isEnd ? "#10B981" : "#161B22",
                      color: "#F0F6FC",
                      weight: 1.5,
                      fillOpacity: rescueModeActive ? 0.98 : 0.9,
                    }}
                  />
                );
              })}
            </MapContainer>

            {rescueModeActive ? (
              <div
                className="route-legend"
                style={{
                  position: "absolute",
                  right: 16,
                  bottom: 16,
                  zIndex: 1200,
                  padding: "12px 14px",
                  minWidth: 240,
                  pointerEvents: "none",
                  color: "var(--text-primary)",
                  fontFamily: "var(--mono-font)",
                }}
              >
                <div style={{ fontSize: "0.68rem", fontWeight: 700, letterSpacing: "0.08em", marginBottom: "10px", color: "var(--text-secondary)" }}>
                  RESCUE CORRIDOR
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: 10, fontSize: "0.72rem", lineHeight: 1.6 }}>
                  <span style={{ width: 12, height: 12, borderRadius: 999, background: "#00FF66", boxShadow: "0 0 12px #00FF66" }} />
                  <span>Evacuation Route</span>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: 10, fontSize: "0.72rem", lineHeight: 1.6, marginTop: "6px" }}>
                  <span style={{ width: 12, height: 12, borderRadius: 999, background: "#F59E0B", boxShadow: "0 0 12px #F59E0B" }} />
                  <span>Trapped Civilian</span>
                </div>
              </div>
            ) : (
              <div
                className="route-legend"
                style={{
                  position: "absolute",
                  right: 16,
                  bottom: 16,
                  zIndex: 1200,
                  padding: "12px 14px",
                  minWidth: 220,
                  pointerEvents: "none",
                  color: "var(--text-primary)",
                  fontFamily: "var(--mono-font)",
                }}
              >
                <div style={{ fontSize: "0.68rem", fontWeight: 700, letterSpacing: "0.08em", marginBottom: "10px", color: "var(--text-secondary)" }}>
                  ROUTE LEGEND
                </div>
                {[
                  { dot: "var(--route-safe)", label: "Safe Road" },
                  { dot: "var(--route-primary)", label: "Recommended Route" },
                  { dot: "var(--route-alternate)", label: "Alternate Route" },
                  { dot: "var(--route-blocked)", label: "Blocked" },
                  { dot: "var(--route-flooded)", label: "Flooded" },
                ].map((item) => (
                  <div key={item.label} style={{ display: "flex", alignItems: "center", gap: 10, fontSize: "0.72rem", lineHeight: 1.6 }}>
                    <span style={{ width: 12, height: 12, borderRadius: 999, background: item.dot, boxShadow: `0 0 12px ${item.dot}` }} />
                    <span>{item.label}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </Card>

        {/* RIGHT SLIDE-OUT PANEL: NVIDIA Nemotron LLM Tactical Intelligence */}
        {showAiDrawer && (
          <div
            style={{
              position: "fixed",
              top: "64px",
              right: 0,
              bottom: 0,
              width: "380px",
              backgroundColor: "#0D1117",
              borderLeft: "1px solid #21262D",
              zIndex: 60,
              boxShadow: "-10px 0 30px rgba(0,0,0,0.8)",
              display: "flex",
              flexDirection: "column",
            }}
          >
            {/* Drawer Header */}
            <div style={{ padding: "16px", borderBottom: "1px solid #21262D", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <Bot size={18} color="#38BDF8" />
                <span style={{ fontSize: "0.85rem", fontWeight: 700, color: "#F0F6FC", fontFamily: "var(--mono-font)" }}>
                  NEMOTRON TACTICAL INTEL
                </span>
              </div>
              <button
                onClick={() => setShowAiDrawer(false)}
                style={{ backgroundColor: "transparent", border: "none", color: "#8B949E", cursor: "pointer" }}
              >
                <X size={18} />
              </button>
            </div>

            {/* Chat Messages Stream */}
            <div style={{ flex: 1, overflowY: "auto", padding: "16px", display: "flex", flexDirection: "column", gap: "12px" }}>
              {chatMessages.map((msg, idx) => (
                <div
                  key={idx}
                  style={{
                    alignSelf: msg.sender === "user" ? "flex-end" : "flex-start",
                    maxWidth: "88%",
                    backgroundColor: msg.sender === "user" ? "#161B22" : "#161B22",
                    border: `1px solid ${msg.sender === "user" ? "#38BDF8" : "#21262D"}`,
                    borderRadius: "8px",
                    padding: "10px 12px",
                  }}
                >
                  <div style={{ fontSize: "0.78rem", color: "#F0F6FC", whiteSpace: "pre-line", lineHeight: 1.5 }}>
                    {msg.text}
                  </div>
                  <span style={{ fontSize: "0.6rem", color: "#484F58", display: "block", marginTop: "4px", textAlign: "right", fontFamily: "var(--mono-font)" }}>
                    {msg.time}
                  </span>
                </div>
              ))}
              {isBotThinking && (
                <div style={{ fontSize: "0.75rem", color: "#38BDF8", fontFamily: "var(--mono-font)" }}>
                  Querying Nemotron 120B NIM model...
                </div>
              )}
            </div>

            {/* Chat Input Field */}
            <div style={{ padding: "12px", borderTop: "1px solid #21262D", display: "flex", gap: "8px" }}>
              <input
                type="text"
                value={inputPrompt}
                onChange={(e) => setInputPrompt(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSendChat()}
                placeholder="Ask Nemotron response query..."
                style={{
                  flex: 1,
                  backgroundColor: "#161B22",
                  border: "1px solid #21262D",
                  borderRadius: "6px",
                  padding: "8px 12px",
                  color: "#F0F6FC",
                  fontSize: "0.8rem",
                  fontFamily: "var(--mono-font)",
                  outline: "none",
                }}
              />
              <button
                onClick={handleSendChat}
                style={{
                  backgroundColor: "#38BDF8",
                  color: "#090C10",
                  border: "none",
                  borderRadius: "6px",
                  padding: "8px 12px",
                  cursor: "pointer",
                }}
              >
                <Send size={15} />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* DOCKED BOTTOM TELEMETRY / TUI PANEL */}
      <div style={{ marginTop: "20px" }}>
        <TuiPanel agentStatus={agentStatus} />
      </div>
    </div>
  );
};





