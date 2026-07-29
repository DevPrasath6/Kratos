import React, { useState } from "react";
import { Download, Plus, FileText } from "lucide-react";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "../components/ui/Card";
import { Table, TableHeader, TableRow, TableHead, TableCell } from "../components/ui/Table";
import { toast } from "sonner";

interface ReportsPageProps {
  onGenerateReport: () => Promise<any>;
}

export const ReportsPage: React.FC<ReportsPageProps> = ({ onGenerateReport }) => {
  const [generating, setGenerating] = useState(false);
  const [reportsList, setReportsList] = useState<any[]>([
    {
      id: "inc_flood_001",
      disaster_type: "Flood",
      severity: 4,
      date: new Date().toISOString(),
      status: "Generated",
      pdf_filename: "report_inc_flood_001.pdf",
    },
    {
      id: "inc_earthquake_002",
      disaster_type: "Earthquake",
      severity: 3,
      date: new Date(Date.now() - 86400000).toISOString(),
      status: "Archived",
      pdf_filename: "report_inc_earthquake_002.pdf",
    },
  ]);

  const handleGenerateClick = async () => {
    setGenerating(true);
    toast.info("Synthesizing Executive Report", {
      description: "Calling ReportGenerationAgent with NVIDIA Nemotron Reasoning Model...",
    });

    try {
      const res = await onGenerateReport();
      const newInc = res?.result;

      if (newInc) {
        setReportsList((prev) => [
          {
            id: newInc.incident_id || `inc_${Date.now()}`,
            disaster_type: newInc.disaster_type || "Flood",
            severity: newInc.severity || 4,
            date: newInc.generated_at || new Date().toISOString(),
            status: "Generated",
            pdf_filename: newInc.pdf_filename || `report_${newInc.incident_id}.pdf`,
          },
          ...prev,
        ]);
        toast.success("Incident PDF Built!", {
          description: `Compiled report: ${newInc.pdf_filename}`,
        });
      }
    } catch (err: any) {
      toast.error("Report Failed", { description: err.message || "Failed to generate report" });
    } finally {
      setGenerating(false);
    }
  };

  const handleDownloadPdf = (incidentId: string) => {
    window.open(`http://localhost:8000/api/agents/reports/download/${incidentId}`, "_blank");
  };

  return (
    <div style={{ padding: "24px 32px", minHeight: "calc(100vh - 64px)", backgroundColor: "#090C10" }}>
      {/* Title Header */}
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "24px" }}>
        <div>
          <h1 style={{ fontSize: "1.25rem", fontWeight: 700, color: "#F0F6FC", letterSpacing: "0.05em", fontFamily: "var(--mono-font)" }}>
            EXECUTIVE DISASTER INTELLIGENCE REPORTS
          </h1>
          <p style={{ color: "#8B949E", fontSize: "0.8rem", marginTop: "4px", fontFamily: "var(--mono-font)" }}>
            Synthesized via NVIDIA Nemotron 120B NIM & compiled to PDF by ReportLab Engine
          </p>
        </div>

        <button
          onClick={handleGenerateClick}
          disabled={generating}
          style={{
            backgroundColor: generating ? "#161B22" : "#38BDF8",
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
            boxShadow: "0 0 20px rgba(56, 189, 248, 0.3)",
          }}
        >
          <Plus size={16} />
          <span>{generating ? "SYNTHESIZING REPORT..." : "SYNTHESIZE NEW PDF REPORT"}</span>
        </button>
      </div>

      {/* Reports Table Card */}
      <Card style={{ backgroundColor: "#0D1117", border: "1px solid #21262D", borderRadius: "10px" }}>
        <CardHeader>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
              <FileText size={18} color="#38BDF8" />
              <CardTitle style={{ fontSize: "0.9rem", fontWeight: 700, color: "#F0F6FC", fontFamily: "var(--mono-font)" }}>
                COMPILED INCIDENT ARCHIVE ({reportsList.length})
              </CardTitle>
            </div>
            <span style={{ fontSize: "0.68rem", color: "#8B949E", fontFamily: "var(--mono-font)" }}>
              STORAGE: SQLite Audit Log & PDF Store
            </span>
          </div>
          <CardDescription style={{ color: "#8B949E", fontSize: "0.75rem", fontFamily: "var(--mono-font)" }}>
            Download formal disaster assessment documents with spatial safe path details and resource allocation manifests.
          </CardDescription>
        </CardHeader>

        <CardContent>
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead style={{ color: "#8B949E", fontFamily: "var(--mono-font)", fontSize: "0.75rem" }}>INCIDENT ID</TableHead>
                <TableHead style={{ color: "#8B949E", fontFamily: "var(--mono-font)", fontSize: "0.75rem" }}>DISASTER MODE</TableHead>
                <TableHead style={{ color: "#8B949E", fontFamily: "var(--mono-font)", fontSize: "0.75rem" }}>SEVERITY</TableHead>
                <TableHead style={{ color: "#8B949E", fontFamily: "var(--mono-font)", fontSize: "0.75rem" }}>COMPILED AT</TableHead>
                <TableHead style={{ color: "#8B949E", fontFamily: "var(--mono-font)", fontSize: "0.75rem" }}>STATUS</TableHead>
                <TableHead style={{ color: "#8B949E", fontFamily: "var(--mono-font)", fontSize: "0.75rem", textAlign: "right" }}>PDF ACTION</TableHead>
              </TableRow>
            </TableHeader>
            <tbody>
              {reportsList.map((rep) => (
                <TableRow key={rep.id}>
                  <TableCell style={{ fontWeight: 700, color: "#F0F6FC", fontFamily: "var(--mono-font)", fontSize: "0.78rem" }}>
                    {rep.id}
                  </TableCell>
                  <TableCell style={{ color: "#38BDF8", fontFamily: "var(--mono-font)", fontSize: "0.78rem", textTransform: "uppercase" }}>
                    {rep.disaster_type}
                  </TableCell>
                  <TableCell style={{ color: "#EF4444", fontFamily: "var(--mono-font)", fontSize: "0.78rem", fontWeight: 700 }}>
                    LEVEL {rep.severity}
                  </TableCell>
                  <TableCell style={{ color: "#8B949E", fontFamily: "var(--mono-font)", fontSize: "0.75rem" }}>
                    {new Date(rep.date).toLocaleString()}
                  </TableCell>
                  <TableCell>
                    <span style={{ fontSize: "0.65rem", padding: "2px 6px", borderRadius: "4px", backgroundColor: "rgba(16, 185, 129, 0.15)", color: "#10B981", fontFamily: "var(--mono-font)" }}>
                      {rep.status}
                    </span>
                  </TableCell>
                  <TableCell style={{ textAlign: "right" }}>
                    <button
                      onClick={() => handleDownloadPdf(rep.id)}
                      style={{
                        backgroundColor: "#161B22",
                        border: "1px solid #30363D",
                        color: "#38BDF8",
                        padding: "6px 12px",
                        borderRadius: "6px",
                        fontSize: "0.72rem",
                        fontWeight: 600,
                        fontFamily: "var(--mono-font)",
                        cursor: "pointer",
                        display: "inline-flex",
                        alignItems: "center",
                        gap: "6px",
                      }}
                    >
                      <Download size={13} />
                      <span>DOWNLOAD PDF</span>
                    </button>
                  </TableCell>
                </TableRow>
              ))}
            </tbody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
};
