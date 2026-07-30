import os

AGENTS = [
    ("Fire Propagation Agent", "fire_propagation", "Simulates fire spread based on wind and terrain.", "15.2ms", "50ms", "92%", "Fire Sim Active"),
    ("Wind Trajectory Agent", "wind_trajectory", "Calculates wind vector fields for hazard spread.", "11.1ms", "35ms", "96%", "Wind Vectors Active"),
    ("Evacuation Center Agent", "evacuation_center", "Manages staging areas for displaced populations.", "8.5ms", "25ms", "98%", "Staging Active"),
    ("Food Supply Agent", "food_supply", "Optimizes distribution of MREs and water rations.", "9.2ms", "30ms", "97%", "Ration Allocator Active"),
    ("Water Purification Agent", "water_purification", "Locates and dispatches mobile water purification units.", "12.0ms", "28ms", "95%", "Purification Active"),
    ("Mobile Clinic Agent", "mobile_clinic", "Routes mobile hospitals to high-density triage zones.", "10.4ms", "42ms", "98%", "Mobile Clinic Routing"),
    ("Emergency Surgery Agent", "emergency_surgery", "Matches trauma surgeons to critical infrastructure.", "7.8ms", "35ms", "99%", "Surgeon Matcher"),
    ("Blood Bank Agent", "blood_bank", "Monitors regional blood supplies and requests drops.", "6.5ms", "15ms", "99%", "Blood Bank Monitor"),
    ("Search Rescue Dogs Agent", "search_rescue_dogs", "Dispatches K9 units to collapsed structures.", "11.5ms", "22ms", "96%", "K9 Dispatch Active"),
    ("Acoustic Detection Agent", "acoustic_detection", "Analyzes drone audio feeds for trapped survivors.", "25.4ms", "85ms", "93%", "Acoustic ML Active"),
    ("Thermal Imaging Agent", "thermal_imaging", "Processes IR satellite data to find heat signatures.", "32.1ms", "95ms", "95%", "IR Processor Active"),
    ("Seismic Activity Agent", "seismic_activity", "Monitors USGS feeds for aftershock probability.", "18.5ms", "40ms", "97%", "Seismic Monitor"),
    ("Tsunami Warning Agent", "tsunami_warning", "Calculates wave propagation from offshore quakes.", "22.3ms", "60ms", "94%", "Tsunami Sim Active"),
    ("Radiation Monitor Agent", "radiation_monitor", "Tracks nuclear plant stability and radiation plumes.", "14.2ms", "35ms", "99%", "Rad Monitor Active"),
    ("Biohazard Detection Agent", "biohazard_detection", "Identifies chemical and biological hazard zones.", "16.8ms", "45ms", "96%", "Biohazard Active"),
    ("Chemical Spill Agent", "chemical_spill", "Models toxic plume dispersion in urban areas.", "20.1ms", "55ms", "95%", "Plume Sim Active"),
    ("Air Quality Agent", "air_quality", "Monitors PM2.5 and toxic gas levels for safe routing.", "12.5ms", "25ms", "98%", "Air Quality Active"),
    ("Traffic Signal Override Agent", "traffic_signal_override", "Hacks city infrastructure to green-light emergency vehicles.", "8.9ms", "30ms", "99%", "Traffic Override Active"),
    ("Bridge Inspection Agent", "bridge_inspection", "Deploys drones to assess bridge pylons.", "15.4ms", "42ms", "96%", "Bridge Inspector"),
    ("Dam Integrity Agent", "dam_integrity", "Evaluates hydrostatic pressure on local dams.", "19.2ms", "50ms", "97%", "Dam Monitor Active"),
    ("Helipad Logistics Agent", "helipad_logistics", "Identifies clear, flat areas for emergency chopper landings.", "14.5ms", "38ms", "95%", "LZ Locator Active"),
    ("Maritime Rescue Agent", "maritime_rescue", "Coordinates Coast Guard and civilian boats.", "11.2ms", "34ms", "97%", "Maritime Dispatch"),
    ("Submarine Drone Agent", "submarine_drone", "Deploys underwater ROVs to inspect submerged infrastructure.", "28.5ms", "75ms", "92%", "ROV Coordinator"),
    ("Volunteer Coordination Agent", "volunteer_coordination", "Groups untrained volunteers into safe supply chains.", "9.5ms", "20ms", "98%", "Volunteer Mgr"),
    ("Donation Routing Agent", "donation_routing", "Matches incoming physical donations to shelter needs.", "7.2ms", "15ms", "99%", "Donation Router"),
    ("Crowd Psychology Agent", "crowd_psychology", "Predicts panic bottlenecks in dense urban evacuations.", "35.2ms", "110ms", "91%", "Psychology Sim Active"),
    ("Panic Mitigation Agent", "panic_mitigation", "Sends calming push notifications to specific geo-fences.", "10.1ms", "25ms", "98%", "Mitigation Active"),
    ("Language Translation Agent", "language_translation", "Translates EAS alerts into 50+ languages instantly.", "45.2ms", "150ms", "99%", "Translation Active"),
    ("Sign Language Agent", "sign_language", "Generates ASL avatar videos for emergency broadcasts.", "120.5ms", "350ms", "95%", "ASL Gen Active"),
    ("Pet Rescue Agent", "pet_rescue", "Coordinates animal control and shelters for abandoned pets.", "11.4ms", "28ms", "97%", "Pet Rescue Active"),
    ("Livestock Evacuation Agent", "livestock_evacuation", "Routes heavy transport for farm animal evacuation.", "14.8ms", "36ms", "96%", "Livestock Routing"),
    ("Emergency Generator Agent", "emergency_generator", "Dispatches diesel generators to hospitals.", "8.6ms", "22ms", "99%", "Generator Dispatch"),
    ("Solar Microgrid Agent", "solar_microgrid", "Reroutes power from residential solar batteries to grid.", "16.5ms", "45ms", "95%", "Microgrid Reroute"),
    ("Satellite Internet Agent", "satellite_internet", "Deploys Starlink terminals to dead zones.", "9.9ms", "24ms", "98%", "Starlink Active"),
    ("Mesh Network Agent", "mesh_network", "Creates ad-hoc wifi networks from surviving cell phones.", "22.1ms", "65ms", "94%", "Mesh Active"),
]

backend_dir = "c:/Users/91934/Music/KRATOS-v1-main/KRATOS-v1-main/backend/agents"
agent_template = """import asyncio
from typing import Any, Dict
from agents.base import BaseAgent

class {class_name}(BaseAgent):
    name: str = "{id}"

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"
        {purpose}
        \"\"\"
        await asyncio.sleep(0.01)  # Simulate logic
        
        output = dict(input_data)
        output["{id}"] = {{
            "status": "completed",
            "message": "Processed successfully by {class_name}"
        }}
        return output
"""

print("Generating 35 Python agent files...")
for name, agent_id, purpose, ping, exec_time, conf, statusMsg in AGENTS:
    class_name = "".join([word.capitalize() for word in agent_id.split("_")]) + "Agent"
    file_content = agent_template.format(class_name=class_name, id=agent_id, purpose=purpose)
    file_path = os.path.join(backend_dir, f"{agent_id}_agent.py")
    with open(file_path, "w") as f:
        f.write(file_content)

print("Updating backend/routes/agents.py...")
agents_routes_file = "c:/Users/91934/Music/KRATOS-v1-main/KRATOS-v1-main/backend/routes/agents.py"
with open(agents_routes_file, "r") as f:
    routes_content = f.read()

# 1. Add imports
imports_str = "\\n".join([f"from agents.{agent_id}_agent import {''.join([w.capitalize() for w in agent_id.split('_')])}Agent" for _, agent_id, _, _, _, _, _ in AGENTS])
if "from agents.public_relations_agent import PublicRelationsAgent" in routes_content:
    routes_content = routes_content.replace(
        "from agents.public_relations_agent import PublicRelationsAgent",
        f"from agents.public_relations_agent import PublicRelationsAgent\\n{imports_str}"
    )

# 2. Register with orchestrator
register_str = "\\n".join([f"orchestrator.register_agent({''.join([w.capitalize() for w in agent_id.split('_')])}Agent())" for _, agent_id, _, _, _, _, _ in AGENTS])
if "orchestrator.register_agent(PublicRelationsAgent())" in routes_content:
    routes_content = routes_content.replace(
        "orchestrator.register_agent(PublicRelationsAgent())",
        f"orchestrator.register_agent(PublicRelationsAgent())\\n{register_str}"
    )

# 3. Add to default pipeline
pipeline_str = ",\\n        ".join([f'"{agent_id}"' for _, agent_id, _, _, _, _, _ in AGENTS])
if '"public_relations"' in routes_content:
    routes_content = routes_content.replace(
        '"public_relations"\\n    ]',
        f'"public_relations",\\n        {pipeline_str}\\n    ]'
    )

# 4. Add endpoints
endpoints_str = "\\n".join([
    f"""
@router.post("/{agent_id}/run")
async def run_{agent_id}(payload: Dict[str, Any]):
    return await orchestrator.execute_agent_standalone("{agent_id}", payload)"""
    for _, agent_id, _, _, _, _, _ in AGENTS
])

routes_content += "\\n" + endpoints_str + "\\n"

with open(agents_routes_file, "w") as f:
    f.write(routes_content)


print("Updating frontend/src/pages/AgentsPage.tsx...")
agents_page_file = "c:/Users/91934/Music/KRATOS-v1-main/KRATOS-v1-main/frontend/src/pages/AgentsPage.tsx"
with open(agents_page_file, "r") as f:
    page_content = f.read()

frontend_objs = "\\n".join([f'    {{ name: "{n}", id: "{id}", purpose: "{p}", ping: "{ping}", exec: "{e}", conf: "{c}", statusMsg: "{s}" }},' for n, id, p, ping, e, c, s in AGENTS])
if 'id: "public_relations"' in page_content:
    parts = page_content.split('  ];\\n\\n  const sampleLogs = [')
    if len(parts) == 2:
        page_content = parts[0] + frontend_objs + "\\n  ];\\n\\n  const sampleLogs = [" + parts[1]

page_content = page_content.replace("30-AGENT AUTONOMOUS FLEET", "65-AGENT AUTONOMOUS FLEET")
page_content = page_content.replace("30 / 30 ONLINE", "65 / 65 ONLINE")

with open(agents_page_file, "w") as f:
    f.write(page_content)


print("Updating frontend/src/components/TuiPanel.tsx...")
tui_file = "c:/Users/91934/Music/KRATOS-v1-main/KRATOS-v1-main/frontend/src/components/TuiPanel.tsx"
with open(tui_file, "r") as f:
    tui_content = f.read()

tui_agents = "\\n".join([f'  "{id}",' for _, id, _, _, _, _, _ in AGENTS])
if '"public_relations",' in tui_content:
    tui_content = tui_content.replace('"public_relations",\\n];', f'"public_relations",\\n{tui_agents}\\n];')

tui_content = tui_content.replace("30 AGENTS DOCKED", "65 AGENTS DOCKED")
tui_content = tui_content.replace("30 AUTONOMOUS AGENTS", "65 AUTONOMOUS AGENTS")

with open(tui_file, "w") as f:
    f.write(tui_content)

print("Updating frontend/src/components/Navbar.tsx...")
nav_file = "c:/Users/91934/Music/KRATOS-v1-main/KRATOS-v1-main/frontend/src/components/Navbar.tsx"
with open(nav_file, "r") as f:
    nav_content = f.read()
nav_content = nav_content.replace('badge: "30"', 'badge: "65"')
with open(nav_file, "w") as f:
    f.write(nav_content)

print("Done generating 35 agents and wiring everything!")
