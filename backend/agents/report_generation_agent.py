from datetime import datetime, timezone
from pathlib import Path
import uuid
from typing import Any, Dict
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from agents.base import BaseAgent
from agents.nim_client import reasoning_client, NIM_API_KEY

REPORTS_DIR = Path(__file__).parent.parent / "static" / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)


class ReportGenerationAgent(BaseAgent):
    name: str = "report_generation"

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates executive summary using NIM reasoning LLM (or string fallback) and PDF report,
        incorporating all dynamic agent telemetry found in input_data.
        """
        prompt = input_data.get("prompt")
        if prompt:
            reply = self._handle_chat(prompt)
            output = dict(input_data)
            output["llm_response"] = reply
            return output

        incident_id = input_data.get("incident_id")
        if not incident_id:
            incident_id = f"inc_{uuid.uuid4().hex[:8]}"
        
        disaster_type = input_data.get("disaster_type", "Flood").capitalize()
        severity = input_data.get("severity", 4)
        blocked_edges = input_data.get("avoided_blocked_edges", input_data.get("blocked_edges", []))
        safe_path = input_data.get("safe_path", [])
        safe_eta = input_data.get("safe_eta", "N/A")
        
        assigned_unit = input_data.get("assigned_unit", {})
        assigned_unit_name = assigned_unit.get("name", "Emergency Medical Team 1") if isinstance(assigned_unit, dict) else str(assigned_unit)

        # Extract extended agent data
        ignore_keys = {
            "graph_id", "incident_id", "disaster_type", "severity", "center", 
            "radius", "blocked_edges", "degraded_edges", "affected_edge_count", 
            "safe_path", "safe_eta", "assigned_unit", "avoided_blocked_edges"
        }
        extended_data = {}
        for k, v in input_data.items():
            if k not in ignore_keys and isinstance(v, (dict, list)) and v:
                extended_data[k] = v

        # Generate summary using NIM reasoning_client
        executive_summary = self._generate_summary(
            disaster_type=disaster_type,
            severity=severity,
            blocked_count=len(blocked_edges),
            safe_path=safe_path,
            unit_name=assigned_unit_name,
            extended_data=extended_data,
        )

        # Generate PDF report file
        pdf_path = REPORTS_DIR / f"report_{incident_id}.pdf"
        self._build_pdf_report(
            filepath=pdf_path,
            incident_id=incident_id,
            disaster_type=disaster_type,
            severity=severity,
            executive_summary=executive_summary,
            safe_path=safe_path,
            safe_eta=safe_eta,
            blocked_edges=blocked_edges,
            assigned_unit=assigned_unit_name,
            extended_data=extended_data,
        )

        output = dict(input_data)  # Preserve pipeline chain
        output.update({
            "incident_id": incident_id,
            "report_summary": executive_summary,
            "pdf_filename": pdf_path.name,
            "download_url": f"/api/agents/reports/download/{incident_id}",
            "generated_at": datetime.now(timezone.utc).isoformat(),
        })
        return output

    def _handle_chat(self, prompt: str) -> str:
        if NIM_API_KEY and reasoning_client:
            try:
                res = ""
                for chunk in reasoning_client.stream([{"role": "user", "content": prompt}]):
                    if chunk.content:
                        res += chunk.content
                if res.strip():
                    return res.strip()
            except Exception:
                pass
        
        return f"Received command: '{prompt}'. Integrating into disaster pipeline telemetry."

    def _generate_summary(
        self, disaster_type: str, severity: int, blocked_count: int, safe_path: list, unit_name: str, extended_data: dict
    ) -> str:
        if NIM_API_KEY and reasoning_client:
            try:
                # Add summary of extended data for the LLM context
                extended_context = "\\n".join([f"{k}: {str(v)[:150]}" for k, v in extended_data.items()])
                
                prompt = (
                    f"Synthesize a comprehensive executive incident summary paragraph for disaster emergency responders. "
                    f"Details: Disaster={disaster_type}, Severity={severity}/5, Blocked Roads Count={blocked_count}, "
                    f"Computed Safe Route={safe_path}, Primary Dispatched Unit={unit_name}. "
                    f"Additional Pipeline Telemetry: {extended_context}. "
                    f"Keep it factual, highly detailed but concise, under 5 sentences."
                )
                res = ""
                for chunk in reasoning_client.stream([{"role": "user", "content": prompt}]):
                    if chunk.content:
                        res += chunk.content
                if res.strip():
                    return res.strip()
            except Exception:
                pass

        return (
            f"EXECUTIVE SUMMARY: {disaster_type.upper()} incident report (Severity {severity}/5). "
            f"A total of {blocked_count} road segment(s) were impacted. "
            f"Safe evacuation route identified: {safe_path}. "
            f"Primary response unit '{unit_name}' successfully dispatched via safe path. "
            f"Additional telemetry recorded from {len(extended_data)} agent modules."
        )

    def _build_pdf_report(
        self,
        filepath: Path,
        incident_id: str,
        disaster_type: str,
        severity: int,
        executive_summary: str,
        safe_path: list,
        safe_eta: Any,
        blocked_edges: list,
        assigned_unit: str,
        extended_data: dict,
    ) -> None:
        doc = SimpleDocTemplate(str(filepath), pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        title_style = ParagraphStyle(
            "TitleStyle",
            parent=styles["Heading1"],
            fontSize=20,
            leading=24,
            textColor=colors.HexColor("#1e293b"),
        )
        story.append(Paragraph(f"KRATOS Incident Report: {incident_id}", title_style))
        story.append(Spacer(1, 12))

        meta_data = [
            ["Disaster Type:", disaster_type, "Severity:", f"{severity} / 5"],
            ["Assigned Unit:", assigned_unit, "Estimated ETA:", f"{safe_eta} min"],
            ["Blocked Edges:", str(len(blocked_edges)), "Safe Route:", str(safe_path)],
        ]
        t = Table(meta_data, colWidths=[110, 150, 110, 150])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f1f5f9")),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor("#334155")),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(t)
        story.append(Spacer(1, 16))

        story.append(Paragraph("Executive Summary", styles["Heading2"]))
        story.append(Spacer(1, 6))
        story.append(Paragraph(executive_summary, styles["Normal"]))
        story.append(Spacer(1, 16))

        # Add dynamic extended data sections
        if extended_data:
            story.append(Paragraph("Extended Agent Telemetry", styles["Heading2"]))
            story.append(Spacer(1, 6))
            
            for agent_name, data in extended_data.items():
                story.append(Paragraph(agent_name.replace("_", " ").title(), styles["Heading3"]))
                
                if isinstance(data, dict):
                    table_data = []
                    for k, v in data.items():
                        # Truncate very long string values for table
                        val_str = str(v)
                        if len(val_str) > 80:
                            val_str = val_str[:77] + "..."
                        table_data.append([k.replace("_", " ").capitalize(), val_str])
                        
                    if table_data:
                        sub_table = Table(table_data, colWidths=[150, 300])
                        sub_table.setStyle(TableStyle([
                            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor("#334155")),
                            ('FONTSIZE', (0, 0), (-1, -1), 8),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
                        ]))
                        story.append(sub_table)
                        story.append(Spacer(1, 8))
                elif isinstance(data, list) and data:
                    story.append(Paragraph(f"List contains {len(data)} items.", styles["Normal"]))
                    story.append(Spacer(1, 8))

        story.append(Spacer(1, 16))
        story.append(Paragraph(f"Generated at: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}", styles["Italic"]))

        doc.build(story)
