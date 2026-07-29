import asyncio
import httpx
import os
import sys
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Button, Label, Input, RichLog
from textual.containers import Grid, Horizontal, Vertical

from ascii_banner import KRATOS_ASCII_BANNER, KRATOS_BLOCK_BANNER

BACKEND_URL = "http://localhost:8000"

ALL_AGENTS = [
    "image_ingestion",
    "road_extraction",
    "road_graph",
    "disaster_simulation",
    "route_planning",
    "traffic_analysis",
    "resource_allocation",
    "volunteer_dispatch",
    "radio_frequency_alert",
    "report_generation",
    "notification",
    "drone_swarm_orchestrator",
    "weather_monitor",
    "social_media_distress",
    "satellite_tasking",
    "telecom_mesh",
    "shelter_capacity",
    "infrastructure_risk",
    "damage_verification",
    "supply_logistics",
    "audit",
    "ping",
]


class BannerWidget(Static):
    def render(self) -> str:
        return f"[bold cyan]{KRATOS_ASCII_BANNER}[/bold cyan]"


class AgentButton(Button):
    def __init__(self, agent_name: str, **kwargs):
        self.agent_name = agent_name
        formatted_name = agent_name.replace("_", " ").title()
        super().__init__(f"○ {formatted_name}", id=f"btn_{agent_name}", **kwargs)

    def update_status(self, status: str):
        formatted_name = self.agent_name.replace("_", " ").title()
        if status == "success":
            self.label = f"[bold green]✓ {formatted_name}[/bold green]"
            self.variant = "success"
        elif status == "failed":
            self.label = f"[bold red]✗ {formatted_name}[/bold red]"
            self.variant = "error"
        elif status == "running":
            self.label = f"[bold yellow]… {formatted_name}[/bold yellow]"
            self.variant = "warning"
        else:
            self.label = f"○ {formatted_name}"
            self.variant = "default"


class KratosTextualApp(App):
    CSS = """
    Screen {
        background: #020617;
        color: #f8fafc;
    }

    #banner_box {
        height: auto;
        border: solid #0e7490;
        margin-bottom: 1;
        content-align: center middle;
    }

    #info_bar {
        height: 3;
        border: solid #0e7490;
        background: #0f172a;
        padding: 0 1;
        align: center middle;
    }

    #trigger_btn {
        margin: 1 0;
        width: 100%;
    }

    #agent_grid {
        grid-size: 2;
        grid-gutter: 1;
        height: auto;
        border: solid #0e7490;
        padding: 1;
    }

    .panel_box {
        border: solid #0e7490;
        background: #0f172a;
        padding: 1;
        margin-top: 1;
    }

    #command_input {
        border: solid #0284c7;
        background: #0f172a;
        color: #38bdf8;
        margin-top: 1;
    }

    #console_log {
        height: 10;
        border: solid #0e7490;
        background: #020617;
        margin-top: 1;
    }
    """

    TITLE = "KRATOS Control Center TUI"

    def compose(self) -> ComposeResult:
        yield Header()
        yield BannerWidget(id="banner_box")
        yield Horizontal(
            Label("[bold cyan]Disaster:[/bold cyan] Flood  |  [bold cyan]Status:[/bold cyan] ", id="status_label"),
            id="info_bar"
        )
        yield Button("⚡ Execute Full Agent Pipeline", id="trigger_btn", variant="primary")
        
        yield Label("[bold yellow]Agent Network Status (Click to trigger isolated agent test):[/bold yellow]")
        yield Grid(*[AgentButton(agent) for agent in ALL_AGENTS], id="agent_grid")

        yield Vertical(
            Label("[bold yellow]Active Units:[/bold yellow] Ambulances: [green]12[/green] | Police: [green]8[/green] | Fire: [green]4[/green] | Volunteers: [green]15[/green]"),
            classes="panel_box"
        )
        yield Vertical(
            Label("[bold green]Safe Route →[/bold green] ETA 7 min · 4.3 km (Route: [0, 3, 6, 7, 8])"),
            classes="panel_box"
        )
        yield Label("[bold cyan]Command Shell (Type -help or -doctor):[/bold cyan]")
        yield Input(placeholder="Type command here (e.g. -help, -doctor, -status, -run pipeline)...", id="command_input")
        yield RichLog(id="console_log", highlight=True, markup=True)
        yield Footer()

    async def on_mount(self) -> None:
        log = self.query_one("#console_log", RichLog)
        log.write("[bold green]KRATOS Control Shell Initialized.[/bold green] Type [cyan]-help[/cyan] for available commands or [cyan]-doctor[/cyan] for agent diagnostic health check.")
        self.set_interval(1.0, self.fetch_status)

    async def fetch_status(self) -> None:
        async with httpx.AsyncClient(timeout=2.0) as client:
            try:
                resp = await client.get(f"{BACKEND_URL}/api/agents/status")
                if resp.status_code == 200:
                    statuses = resp.json()
                    self.query_one("#status_label", Label).update("[bold cyan]Disaster:[/bold cyan] Flood  |  [bold cyan]Status:[/bold cyan] [bold green]● CONNECTED[/bold green]")
                    for agent in ALL_AGENTS:
                        st = statuses.get(agent, {}).get("last_run_status")
                        btn = self.query_one(f"#btn_{agent}", AgentButton)
                        btn.update_status(st)
                else:
                    self.query_one("#status_label", Label).update("[bold cyan]Disaster:[/bold cyan] Flood  |  [bold cyan]Status:[/bold cyan] [bold red]○ DISCONNECTED[/bold red]")
            except Exception:
                self.query_one("#status_label", Label).update("[bold cyan]Disaster:[/bold cyan] Flood  |  [bold cyan]Status:[/bold cyan] [bold red]○ DISCONNECTED[/bold red]")

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        cmd = event.value.strip().lower()
        log = self.query_one("#console_log", RichLog)
        input_widget = self.query_one("#command_input", Input)
        input_widget.value = ""

        if not cmd:
            return

        log.write(f"[dim]>[/dim] [cyan]{cmd}[/cyan]")

        if cmd in ["-help", "help", "-h"]:
            log.write("[bold yellow]Available Commands:[/bold yellow]")
            log.write("  [cyan]-help[/cyan]            Show this help manual")
            log.write("  [cyan]-doctor[/cyan]          Run system diagnostics, detect failing agents, and auto-restart them")
            log.write("  [cyan]-status[/cyan]          Display live status of all 22 KRATOS agents")
            log.write("  [cyan]-nim[/cyan]             Check NVIDIA NIM VLM/LLM endpoint latency and status")
            log.write("  [cyan]-run pipeline[/cyan]    Execute full 22-agent disaster simulation pipeline")
            log.write("  [cyan]-clear[/cyan]           Clear terminal log screen")

        elif cmd in ["-doctor", "doctor", "-doc"]:
            log.write("[bold yellow]🏥 Running KRATOS System Doctor Diagnostics...[/bold yellow]")
            async with httpx.AsyncClient(timeout=5.0) as client:
                try:
                    resp = await client.get(f"{BACKEND_URL}/api/agents/status")
                    if resp.status_code == 200:
                        statuses = resp.json()
                        failed_agents = []
                        for agent, info in statuses.items():
                            if info.get("last_run_status") == "failed":
                                failed_agents.append((agent, info.get("last_error", "Unknown error")))

                        if not failed_agents:
                            log.write("[bold green]✓ All 22 agents healthy! No failing agents detected.[/bold green]")
                        else:
                            log.write(f"[bold red]Found {len(failed_agents)} failing agent(s):[/bold red]")
                            for ag, err in failed_agents:
                                log.write(f"  ❌ [bold red]{ag}[/bold red]: {err}")
                                log.write(f"  ↳ [yellow]Attempting auto-recovery restart for '{ag}'...[/yellow]")
                                restart_resp = await client.post(f"{BACKEND_URL}/api/agents/{ag}/run", json={"use_sample": True})
                                if restart_resp.status_code == 200:
                                    log.write(f"  ✓ [green]Agent '{ag}' successfully restarted.[/green]")
                                else:
                                    log.write(f"  ❌ [red]Restart failed for '{ag}': {restart_resp.text}[/red]")
                    else:
                        log.write(f"[bold red]Doctor unable to connect to backend (HTTP {resp.status_code}). Ensure backend server is running.[/bold red]")
                except Exception as e:
                    log.write(f"[bold red]Doctor Connection Error:[/bold red] {e}. Make sure backend server is running on port 8000.")

        elif cmd in ["-status", "status"]:
            async with httpx.AsyncClient(timeout=2.0) as client:
                try:
                    resp = await client.get(f"{BACKEND_URL}/api/agents/status")
                    if resp.status_code == 200:
                        log.write(f"[bold green]Agent Status Matrix:[/bold green]\n{resp.json()}")
                    else:
                        log.write("[bold red]Failed to fetch status.[/bold red]")
                except Exception as e:
                    log.write(f"[bold red]Error:[/bold red] {e}")

        elif cmd in ["-nim", "nim"]:
            async with httpx.AsyncClient(timeout=3.0) as client:
                try:
                    resp = await client.get(f"{BACKEND_URL}/api/agents/nim/health")
                    if resp.status_code == 200:
                        data = resp.json()
                        log.write(f"[bold green]NVIDIA NIM Health:[/bold green]\n{data}")
                    else:
                        log.write("[bold red]NIM status endpoint unavailable.[/bold red]")
                except Exception as e:
                    log.write(f"[bold red]Error checking NIM:[/bold red] {e}")

        elif cmd in ["-run pipeline", "run pipeline", "-pipeline"]:
            log.write("[yellow]Executing full agent pipeline via shell command...[/yellow]")
            async with httpx.AsyncClient(timeout=10.0) as client:
                try:
                    resp = await client.post(
                        f"{BACKEND_URL}/api/agents/pipeline/run",
                        json={"use_sample": True, "disaster_type": "flood", "severity": 4}
                    )
                    if resp.status_code == 200:
                        log.write("[bold green]Pipeline execution completed successfully![/bold green]")
                    else:
                        log.write(f"[bold red]Pipeline failed: {resp.text}[/bold red]")
                except Exception as e:
                    log.write(f"[bold red]Error:[/bold red] {e}")

        elif cmd in ["-clear", "clear"]:
            log.clear()

        else:
            log.write(f"[bold red]Unknown command '[yellow]{cmd}[/yellow]'. Type [cyan]-help[/cyan] for available commands.[/bold red]")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        log = self.query_one("#console_log", RichLog)
        if event.button.id == "trigger_btn":
            log.write("[yellow]Executing full agent pipeline via UI button...[/yellow]")
            async with httpx.AsyncClient(timeout=10.0) as client:
                try:
                    resp = await client.post(
                        f"{BACKEND_URL}/api/agents/pipeline/run",
                        json={"use_sample": True, "disaster_type": "flood", "severity": 4}
                    )
                    if resp.status_code == 200:
                        log.write("[bold green]✓ Pipeline completed.[/bold green]")
                    await self.fetch_status()
                except Exception as e:
                    log.write(f"[bold red]Pipeline error: {e}[/bold red]")
        elif isinstance(event.button, AgentButton):
            agent_name = event.button.agent_name
            log.write(f"[yellow]Triggering isolated agent '[cyan]{agent_name}[/cyan]'...[/yellow]")
            async with httpx.AsyncClient(timeout=10.0) as client:
                try:
                    resp = await client.post(
                        f"{BACKEND_URL}/api/agents/{agent_name}/run",
                        json={"use_sample": True}
                    )
                    if resp.status_code == 200:
                        log.write(f"[bold green]✓ Agent '{agent_name}' finished.[/bold green]")
                    await self.fetch_status()
                except Exception as e:
                    log.write(f"[bold red]Agent error: {e}[/bold red]")


if __name__ == "__main__":
    app = KratosTextualApp()
    app.run()
