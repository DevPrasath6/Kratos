# KRATOS Multi-Agent System Detailed Documentation

This directory contains the detailed documentation for all the autonomous agents that make up the KRATOS disaster response pipeline.

## [Ping](./agents/ping.md)
**Agent ID:** `ping`

**Source File:** `backend/agents/ping_agent.py`

Automated disaster response agent component.

## [Image Ingestion](./agents/image_ingestion.md)
**Agent ID:** `image_ingestion`

**Source File:** `backend/agents/image_ingestion_agent.py`

Automated disaster response agent component.

## [Road Extraction](./agents/road_extraction.md)
**Agent ID:** `road_extraction`

**Source File:** `backend/agents/road_extraction_agent.py`

Automated disaster response agent component.

## [Road Graph](./agents/road_graph.md)
**Agent ID:** `road_graph`

**Source File:** `backend/agents/road_graph_agent.py`

Automated disaster response agent component.

## [Disaster Simulation](./agents/disaster_simulation.md)
**Agent ID:** `disaster_simulation`

**Source File:** `backend/agents/disaster_simulation_agent.py`

Automated disaster response agent component.

## [Route Planning](./agents/route_planning.md)
**Agent ID:** `route_planning`

**Source File:** `backend/agents/route_planning_agent.py`

Automated disaster response agent component.

## [Traffic Analysis](./agents/traffic_analysis.md)
**Agent ID:** `traffic_analysis`

**Source File:** `backend/agents/traffic_analysis_agent.py`

Automated disaster response agent component.

## [Resource Allocation](./agents/resource_allocation.md)
**Agent ID:** `resource_allocation`

**Source File:** `backend/agents/resource_allocation_agent.py`

Automated disaster response agent component.

## [Volunteer Healthcare Dispatch](./agents/volunteer_healthcare_dispatch.md)
**Agent ID:** `volunteer_healthcare_dispatch`

**Source File:** `backend/agents/volunteer_dispatch_agent.py`

Automated disaster response agent component.

## [Radio Frequency Alert](./agents/radio_frequency_alert.md)
**Agent ID:** `radio_frequency_alert`

**Source File:** `backend/agents/rf_alert_agent.py`

Automated disaster response agent component.

## [Notification](./agents/notification.md)
**Agent ID:** `notification`

**Source File:** `backend/agents/notification_agent.py`

Automated disaster response agent component.

## [Audit](./agents/audit.md)
**Agent ID:** `audit`

**Source File:** `backend/agents/audit_agent.py`

Automated disaster response agent component.

## [Report Generation](./agents/report_generation.md)
**Agent ID:** `report_generation`

**Source File:** `backend/agents/report_generation_agent.py`

Automated disaster response agent component.

## [Drone Swarm Orchestrator](./agents/drone_swarm_orchestrator.md)
**Agent ID:** `drone_swarm_orchestrator`

**Source File:** `backend/agents/drone_swarm_agent.py`

Calculates 3D flight paths for autonomous drones to survey occluded areas.

## [Predictive Micro Climate](./agents/predictive_micro_climate.md)
**Agent ID:** `predictive_micro_climate`

**Source File:** `backend/agents/predictive_climate_agent.py`

Predicts disaster spread over 12 hours using live meteorology.

## [Social Media Distress](./agents/social_media_distress.md)
**Agent ID:** `social_media_distress`

**Source File:** `backend/agents/social_media_distress_agent.py`

Monitors social media feeds and extracts precise coordinates of trapped individuals.

## [Autonomous Satellite Tasking](./agents/autonomous_satellite_tasking.md)
**Agent ID:** `autonomous_satellite_tasking`

**Source File:** `backend/agents/satellite_tasking_agent.py`

Automatically pings commercial satellite networks to take fresh images.

## [Telecom Mesh](./agents/telecom_mesh.md)
**Agent ID:** `telecom_mesh`

**Source File:** `backend/agents/telecom_mesh_agent.py`

Calculates optimal line-of-sight deployments for temporary cell towers (COWs).

## [Shelter Capacity](./agents/shelter_capacity.md)
**Agent ID:** `shelter_capacity`

**Source File:** `backend/agents/shelter_capacity_agent.py`

Monitors live capacity, medical triage, and food stock across relief shelters.

## [Infrastructure Risk](./agents/infrastructure_risk.md)
**Agent ID:** `infrastructure_risk`

**Source File:** `backend/agents/infrastructure_risk_agent.py`

Evaluates structural risk scores for critical infrastructure (bridges, power, dams).

## [Damage Verification](./agents/damage_verification.md)
**Agent ID:** `damage_verification`

**Source File:** `backend/agents/damage_verification_agent.py`

Analyzes citizen-uploaded photos using NVIDIA Nemotron Vision model to verify road/bridge damage.

## [Supply Logistics](./agents/supply_logistics.md)
**Agent ID:** `supply_logistics`

**Source File:** `backend/agents/supply_logistics_agent.py`

Calculates weight/cargo distributions and helicopter drop coordinates for isolated regions.
