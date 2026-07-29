import asyncio
import base64
import json
import os
import sys
from pathlib import Path
import httpx
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.text import Text

from ascii_banner import KRATOS_BLOCK_BANNER
from nim_health import fetch_nim_health

BACKEND_URL = "http://localhost:8000"

AGENTS_REGISTRY = [
    {"id": "ping", "name": "1. Ping Agent", "desc": "Healthcheck & echo test"},
    {"id": "image_ingestion", "name": "2. Image Ingestion Agent", "desc": "Base64 encoding & resize"},
    {"id": "road_extraction", "name": "3. Road Extraction Agent", "desc": "NIM VLM / OpenCV segmenter"},
    {"id": "road_graph", "name": "4. Road Graph Agent", "desc": "NetworkX spatial graph builder"},
    {"id": "disaster_simulation", "name": "5. Disaster Simulation Agent", "desc": "Flood/Quake impact rules"},
    {"id": "route_planning", "name": "6. Route Planning Agent", "desc": "Dijkstra safe path planner"},
    {"id": "traffic_analysis", "name": "7. Traffic Analysis Agent", "desc": "Per-edge congestion scoring"},
    {"id": "resource_allocation", "name": "8. Resource Allocation Agent", "desc": "Medical/Fire unit dispatch"},
    {"id": "volunteer_healthcare_dispatch", "name": "9. Volunteer Dispatch Agent", "desc": "Volunteer safe route order"},
    {"id": "radio_frequency_alert", "name": "10. RF Alert Agent", "desc": "IPAWS/EAS broadcast payload"},
    {"id": "notification", "name": "11. Notification Agent", "desc": "Multi-channel alert dispatcher"},
    {"id": "report_generation", "name": "12. Report Generation Agent", "desc": "NIM reasoning + PDF report"},
    {"id": "audit", "name": "13. Audit Agent", "desc": "SQLite execution logger"},
    {"id": "full_pipeline", "name": "⚡ FULL PIPELINE EXECUTION", "desc": "Run all 12 agents in sequence"},
]

DEFAULT_PAYLOADS = {
    "ping": {"message": "Hello KRATOS Agent Framework"},
    "image_ingestion": {"max_dim": 1024},
    "road_extraction": {"use_sample": True},
    "road_graph": {"use_sample": True, "tolerance": 15.0},
    "disaster_simulation": {"disaster_type": "flood", "severity": 4},
    "route_planning": {"source": 0, "destination": 8},
    "traffic_analysis": {"use_sample": True},
    "resource_allocation": {"incident_type": "medical"},
    "volunteer_healthcare_dispatch": {"incident_type": "medical"},
    "radio_frequency_alert": {"disaster_type": "flood", "severity": 4},
    "notification": {"channels": ["sms", "email", "dashboard_push"]},
    "report_generation": {"incident_id": "single_agent_test_inc_1"},
    "audit": {"limit": 10},
    "full_pipeline": {"use_sample": True, "disaster_type": "flood", "severity": 4},
}


class SingleAgentTuiApp:
    def __init__(self):
        self.console = Console()
        self.selected_index = 0
        self.nim_telemetry = {}
        self.last_output = {}
        self.last_execution_time_ms = -1.0
        self.custom_image_path = ""
        self.is_executing = False

    async def update_telemetry(self):
        self.nim_telemetry = await fetch_nim_health()

    async def run_single_agent(self, agent_id: str, custom_image_bytes: bytes = None):
        self.is_executing = True
        t0 = asyncio.get_event_loop().time()

        payload = dict(DEFAULT_PAYLOADS.get(agent_id, {}))
        if custom_image_bytes:
            payload["image_bytes"] = base64.b64encode(custom_image_bytes).decode("utf-8")

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                if agent_id == "full_pipeline":
                    url = f"{BACKEND_URL}/api/agents/pipeline/run"
                else:
                    url = f"{BACKEND_URL}/api/agents/{agent_id}/run"

                resp = await client.post(url, json=payload)
                if resp.status_code == 200:
                    self.last_output = resp.json()
                else:
                    self.last_output = {"error": resp.text, "status_code": resp.status_code}
            except Exception as e:
                self.last_output = {"error": str(e)}

        self.last_execution_time_ms = round((asyncio.get_event_loop().time() - t0) * 1000, 2)
        self.is_executing = False

    def render_header(self) -> Panel:
        online = self.nim_telemetry.get("backend_online", False)
        key_present = self.nim_telemetry.get("nim_api_key_present", False)
        vlm_lat = self.nim_telemetry.get("vlm_latency_ms", -1.0)
        reasoning_lat = self.nim_telemetry.get("reasoning_latency_ms", -1.0)

        grid = Table.grid(expand=True)
        grid.add_column(justify="left")
        grid.add_column(justify="right")

        backend_text = "[bold green]ONLINE[/bold green]" if online else "[bold red]OFFLINE[/bold red]"
        key_text = "[bold green]DETECTED[/bold green]" if key_present else "[bold yellow]MISSING (FALLBACK)[/bold yellow]"

        left_str = f"[bold cyan]Backend:[/bold cyan] {backend_text}  |  [bold cyan]NIM API Key:[/bold cyan] {key_text}"
        right_str = (
            f"[bold cyan]VLM Latency:[/bold cyan] [green]{vlm_lat}ms[/green]  |  "
            f"[bold cyan]LLM Latency:[/bold cyan] [green]{reasoning_lat}ms[/green]"
        )

        grid.add_row(left_str, right_str)
        return Panel(grid, title="[bold yellow]NVIDIA NIM & AGENT HEALTH TELEMETRY[/bold yellow]", border_style="cyan")

    def render_agent_selector(self) -> Panel:
        table = Table(show_header=True, box=None, expand=True)
        table.add_column("Agent / Workflow", style="bold white", ratio=2)
        table.add_column("Description", style="dim white", ratio=3)

        for idx, item in enumerate(AGENTS_REGISTRY):
            name = item["name"]
            desc = item["desc"]
            if idx == self.selected_index:
                row_name = f"[bold green]>[/bold green] [bold cyan]{name}[/bold cyan]"
                row_desc = f"[bold white]{desc}[/bold white]"
            else:
                row_name = f"  {name}"
                row_desc = desc
            table.add_row(row_name, row_desc)

        return Panel(table, title="[bold yellow]Select Agent to Test (Up/Down + Enter)[/bold yellow]", border_style="cyan")

    def render_output_panel(self) -> Panel:
        curr_agent = AGENTS_REGISTRY[self.selected_index]
        agent_id = curr_agent["id"]

        status_str = "[bold yellow]EXECUTING...[/bold yellow]" if self.is_executing else "[bold green]READY[/bold green]"
        exec_time = f"[green]{self.last_execution_time_ms} ms[/green]" if self.last_execution_time_ms > 0 else "N/A"

        json_str = json.dumps(self.last_output, indent=2) if self.last_output else "{\n  \"message\": \"Press Enter to execute selected agent\"\n}"
        if len(json_str) > 2000:
            json_str = json_str[:2000] + "\n  ... (truncated for TUI display)"

        syntax = Syntax(json_str, "json", theme="monokai", word_wrap=True)

        header_text = f"Agent: [bold cyan]{agent_id}[/bold cyan] | Status: {status_str} | Execution Time: {exec_time}"

        return Panel(
            syntax,
            title=f"[bold yellow]Agent Output & Telemetry Logs ({header_text})[/bold yellow]",
            border_style="cyan",
        )

    def generate_layout(self) -> Layout:
        layout = Layout()
        layout.split(
            Layout(name="banner", size=8),
            Layout(name="header", size=4),
            Layout(name="main", ratio=1),
        )

        layout["main"].split_row(
            Layout(name="selector", ratio=2),
            Layout(name="output", ratio=3),
        )

        banner_panel = Panel(Text(KRATOS_BLOCK_BANNER, style="bold cyan"), border_style="dim cyan")
        layout["banner"].update(banner_panel)
        layout["header"].update(self.render_header())
        layout["selector"].update(self.render_agent_selector())
        layout["output"].update(self.render_output_panel())

        return layout

    async def run(self):
        self.console.clear()
        self.console.print(Text(KRATOS_BLOCK_BANNER, style="bold cyan"))
        await asyncio.sleep(0.8)

        await self.update_telemetry()

        # Keyboard listener or interactive console loop
        with Live(self.generate_layout(), refresh_per_second=4, console=self.console) as live:
            while True:
                await self.update_telemetry()
                live.update(self.generate_layout())
                await asyncio.sleep(0.5)


if __name__ == "__main__":
    app = SingleAgentTuiApp()
    try:
        # Non-blocking run test CLI mode
        agent_arg = sys.argv[1] if len(sys.argv) > 1 else "full_pipeline"
        print(f"Executing KRATOS Single-Agent Test for: {agent_arg}")
        asyncio.run(app.run_single_agent(agent_arg))
        print("Execution complete. Output:")
        print(json.dumps(app.last_output, indent=2))
    except KeyboardInterrupt:
        print("\nKRATOS Single-Agent TUI exited.")
