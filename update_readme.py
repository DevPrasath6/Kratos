import re

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

readme_path = "c:/Users/91934/Music/KRATOS-v1-main/KRATOS-v1-main/README.md"
with open(readme_path, "r", encoding="utf-8") as f:
    readme = f.read()

# 1. Update text mentions
readme = readme.replace("30-Stage", "65-Stage")
readme = readme.replace("30 AUTONOMOUS DISASTER RESPONSE AGENTS", "65 AUTONOMOUS DISASTER RESPONSE AGENTS")
readme = readme.replace("30-Agent", "65-Agent")
readme = readme.replace("all 30 agents", "all 65 agents")

# 2. Rebuild the ASCII box
# The current box is rows 29-43. Let's extract the list of existing 30 agents.
import re

box_pattern = re.compile(r"│\   ┌──────────────────────────────────────────────────────────────────────────┐   │(.*?)│   └──────────────────────────────────────────────────────────────────────────┘   │", re.DOTALL)
match = box_pattern.search(readme)
if match:
    inner = match.group(1)
    
    # We want to create a new inner box content with 65 agents in 2 columns
    # First, let's extract the existing 30 names.
    existing = [
        "Image Ingestion Agent",
        "Road Extraction Agent",
        "Road Graph NetworkX Agent",
        "Disaster Simulation Agent",
        "Dynamic Route Planning Agent",
        "Traffic Congestion Agent",
        "Resource Allocation Agent",
        "Volunteer Dispatch Agent",
        "RF Broadcast Alert Agent",
        "PDF Report Generation Agent",
        "Multi-Channel Notification",
        "Drone Swarm Orchestrator Agent",
        "Predictive Micro-Climate Agent",
        "Social Media Distress NLP Agent",
        "Autonomous Satellite Tasking",
        "Telecom Mesh COW Agent",
        "Relief Shelter Capacity Agent",
        "Infrastructure Collapse Risk",
        "Multimodal Vision Damage Agent",
        "Supply Helicopter Cargo Agent",
        "Audit & SQLite Logging Agent",
        "Standalone Ping Diagnostic",
        "Evacuation Transport Agent",
        "Power Grid Restoration Agent",
        "Water Quality Agent",
        "Medical Triage Agent",
        "Debris Clearance Agent",
        "Wildlife Rescue Agent",
        "Structural Engineering Agent",
        "Public Relations Agent",
    ]
    
    for name, _, _, _, _, _, _ in AGENTS:
        existing.append(name)
    
    # We have 65 items. We want 2 columns. Column 1: 1-33. Column 2: 34-65.
    lines = []
    lines.append("│   │                 65 AUTONOMOUS DISASTER RESPONSE AGENTS                   │   │\\n")
    lines.append("│   ├──────────────────────────────────────────────────────────────────────────┤   │\\n")
    
    mid = 33
    for i in range(mid):
        idx1 = i + 1
        name1 = existing[i]
        str1 = f"{idx1:2d}. {name1}"
        
        idx2 = i + 1 + mid
        if idx2 <= 65:
            name2 = existing[idx2-1]
            str2 = f"{idx2:2d}. {name2}"
        else:
            str2 = ""
        
        # Pad to fit the box
        # Total width inside the box is 74 chars (between the │ characters)
        # We need "│  {str1:<33}  {str2:<35} │" 
        line = f"│   │ {str1:<35} {str2:<34} │   │\\n"
        lines.append(line)
        
    new_inner = "\\n".join([l.rstrip('\\n') for l in lines]) + "\\n"
    readme = readme[:match.start(1)] + "\\n" + new_inner + readme[match.end(1):]


# 3. Add to markdown table
table_end_pattern = r"\| \*\*30\*\* \| \*\*Public Relations\*\* \| Drafts automated public safety broadcasts based on incident data\. \| Nemotron LLM \|"
if table_end_pattern.replace('\\\\', '') in readme:
    new_rows = []
    start_idx = 31
    for name, agent_id, purpose, _, _, _, _ in AGENTS:
        name_clean = name.replace(" Agent", "")
        new_rows.append(f"| **{start_idx}** | **{name_clean}** | {purpose} | Domain Specific Engine |")
        start_idx += 1
    
    replacement = table_end_pattern.replace('\\\\', '') + "\\n" + "\\n".join(new_rows)
    readme = readme.replace(table_end_pattern.replace('\\\\', ''), replacement)

with open(readme_path, "w", encoding="utf-8") as f:
    f.write(readme)

print("README updated successfully.")
