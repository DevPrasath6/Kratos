import os
import random

AGENT_WORKLOADS = {
    "fire_propagation": """{
            "status": "completed",
            "burn_radius_km": round(random.uniform(2.5, 12.0), 2),
            "containment_percentage": random.randint(10, 85),
            "wind_factor_multiplier": round(random.uniform(1.1, 2.5), 2)
        }""",
    "wind_trajectory": """{
            "status": "completed",
            "primary_vector": {"direction": random.choice(["NE", "NW", "SE", "SW"]), "speed_mph": random.randint(15, 65)},
            "hazard_spread_eta_mins": random.randint(30, 120)
        }""",
    "evacuation_center": """{
            "status": "completed",
            "active_staging_areas": random.randint(3, 15),
            "total_displaced_processed": random.randint(500, 5000),
            "capacity_remaining_pct": random.randint(5, 45)
        }""",
    "food_supply": """{
            "status": "completed",
            "mre_pallets_dispatched": random.randint(10, 100),
            "water_gallons_routed": random.randint(1000, 25000),
            "critical_shortages": random.choice([True, False])
        }""",
    "water_purification": """{
            "status": "completed",
            "mobile_units_active": random.randint(2, 8),
            "gallons_purified_per_hour": random.randint(500, 5000),
            "contaminants_neutralized": ["E. coli", "Lead", "Silt"]
        }""",
    "mobile_clinic": """{
            "status": "completed",
            "clinics_deployed": random.randint(1, 5),
            "triage_queue_size": random.randint(20, 150),
            "critical_beds_available": random.randint(0, 15)
        }""",
    "emergency_surgery": """{
            "status": "completed",
            "trauma_surgeons_routed": random.randint(2, 10),
            "surgeries_pending": random.randint(5, 30),
            "medical_supplies_status": random.choice(["Critical", "Adequate", "Low"])
        }""",
    "blood_bank": """{
            "status": "completed",
            "o_negative_units": random.randint(10, 200),
            "drone_drops_requested": random.randint(1, 5),
            "supply_level": random.choice(["Critical", "Stable"])
        }""",
    "search_rescue_dogs": """{
            "status": "completed",
            "k9_units_deployed": random.randint(5, 25),
            "scent_trails_identified": random.randint(2, 12),
            "structures_cleared": random.randint(10, 50)
        }""",
    "acoustic_detection": """{
            "status": "completed",
            "anomalies_detected": random.randint(1, 8),
            "confidence_scores": [round(random.uniform(0.7, 0.99), 2) for _ in range(3)],
            "triangulated_coordinates": {"lat": 34.05, "lng": -118.25}
        }""",
    "thermal_imaging": """{
            "status": "completed",
            "heat_signatures_found": random.randint(3, 15),
            "drone_sweeps_completed": random.randint(1, 6),
            "max_temp_celsius": random.randint(35, 120)
        }""",
    "seismic_activity": """{
            "status": "completed",
            "richter_scale": round(random.uniform(3.5, 7.8), 1),
            "epicenter": {"lat": 36.1, "lng": -115.2},
            "aftershock_probability_pct": random.randint(20, 95)
        }""",
    "tsunami_warning": """{
            "status": "completed",
            "wave_height_meters": round(random.uniform(1.5, 8.0), 1),
            "eta_coastline_mins": random.randint(15, 180),
            "evacuation_zones": ["Zone A", "Zone B"]
        }""",
    "radiation_monitor": """{
            "status": "completed",
            "sieverts_per_hour": round(random.uniform(0.01, 5.0), 2),
            "plume_radius_km": round(random.uniform(1.0, 15.0), 1),
            "reactor_status": random.choice(["Stable", "Compromised"])
        }""",
    "biohazard_detection": """{
            "status": "completed",
            "pathogens_detected": random.choice([[], ["Unknown Strain A"], ["Chemical Agent B"]]),
            "quarantine_zones_active": random.randint(1, 4),
            "hazard_level": random.choice(["Low", "Moderate", "High", "Critical"])
        }""",
    "chemical_spill": """{
            "status": "completed",
            "toxic_plume_sq_km": round(random.uniform(0.5, 5.5), 1),
            "dispersion_rate": "Fast",
            "recommended_ppe": "Level A"
        }""",
    "air_quality": """{
            "status": "completed",
            "aqi_score": random.randint(50, 450),
            "pm25_level": random.randint(12, 250),
            "safe_routing_enabled": True
        }""",
    "traffic_signal_override": """{
            "status": "completed",
            "intersections_overridden": random.randint(10, 150),
            "eta_reduction_mins": random.randint(5, 25),
            "gridlock_avoided": True
        }""",
    "bridge_inspection": """{
            "status": "completed",
            "bridges_assessed": random.randint(1, 8),
            "critical_failures_detected": random.randint(0, 2),
            "drone_battery_avg": random.randint(15, 85)
        }""",
    "dam_integrity": """{
            "status": "completed",
            "hydrostatic_pressure_psi": random.randint(1500, 4500),
            "micro_fractures_detected": random.randint(0, 12),
            "breach_risk": random.choice(["Low", "Moderate", "High"])
        }""",
    "helipad_logistics": """{
            "status": "completed",
            "landing_zones_cleared": random.randint(2, 10),
            "choppers_en_route": random.randint(1, 5),
            "weather_clearance": random.choice([True, False])
        }""",
    "maritime_rescue": """{
            "status": "completed",
            "vessels_deployed": random.randint(3, 12),
            "civilians_recovered": random.randint(0, 45),
            "sea_state": random.choice(["Calm", "Rough", "Severe"])
        }""",
    "submarine_drone": """{
            "status": "completed",
            "rovs_active": random.randint(1, 4),
            "submerged_infrastructure_scanned": random.randint(1, 5),
            "anomalies": random.randint(0, 3)
        }""",
    "volunteer_coordination": """{
            "status": "completed",
            "volunteers_registered": random.randint(50, 500),
            "supply_chains_formed": random.randint(2, 10),
            "training_completed_pct": random.randint(40, 100)
        }""",
    "donation_routing": """{
            "status": "completed",
            "pallets_received": random.randint(10, 200),
            "shelters_supplied": random.randint(1, 8),
            "logistics_bottleneck": random.choice(["None", "Trucks", "Roads"])
        }""",
    "crowd_psychology": """{
            "status": "completed",
            "panic_index": round(random.uniform(0.1, 0.9), 2),
            "bottlenecks_predicted": random.randint(1, 5),
            "sentiment": random.choice(["Anxious", "Calm", "Panicked"])
        }""",
    "panic_mitigation": """{
            "status": "completed",
            "push_notifications_sent": random.randint(1000, 50000),
            "geo_fences_active": random.randint(2, 8),
            "calming_effect_est": "Moderate"
        }""",
    "language_translation": """{
            "status": "completed",
            "languages_translated": random.randint(10, 50),
            "processing_time_ms": random.randint(15, 60),
            "accuracy_score": "99.9%"
        }""",
    "sign_language": """{
            "status": "completed",
            "asl_videos_generated": random.randint(1, 5),
            "render_time_ms": random.randint(100, 400),
            "broadcast_synced": True
        }""",
    "pet_rescue": """{
            "status": "completed",
            "animals_recovered": random.randint(5, 50),
            "temporary_shelters_full": random.choice([True, False]),
            "veterinary_needs": "Moderate"
        }""",
    "livestock_evacuation": """{
            "status": "completed",
            "herds_relocated": random.randint(1, 10),
            "heavy_transports_active": random.randint(2, 15),
            "routes_secured": True
        }""",
    "emergency_generator": """{
            "status": "completed",
            "generators_dispatched": random.randint(2, 20),
            "fuel_levels_pct": random.randint(20, 95),
            "hospitals_powered": random.randint(1, 5)
        }""",
    "solar_microgrid": """{
            "status": "completed",
            "batteries_tapped": random.randint(50, 500),
            "mw_rerouted": round(random.uniform(1.5, 12.0), 1),
            "grid_stability": random.choice(["Stable", "Fluctuating"])
        }""",
    "satellite_internet": """{
            "status": "completed",
            "terminals_deployed": random.randint(5, 25),
            "bandwidth_mbps": random.randint(50, 300),
            "dead_zones_covered": random.randint(2, 10)
        }""",
    "mesh_network": """{
            "status": "completed",
            "nodes_connected": random.randint(100, 5000),
            "network_resilience_pct": random.randint(60, 99),
            "data_transferred_gb": round(random.uniform(5.0, 50.0), 1)
        }"""
}

backend_dir = "c:/Users/91934/Music/KRATOS-v1-main/KRATOS-v1-main/backend/agents"

print("Updating workloads...")
for agent_id, workload_str in AGENT_WORKLOADS.items():
    file_path = os.path.join(backend_dir, f"{agent_id}_agent.py")
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            content = f.read()
        
        # We know the exact string to replace
        class_name = "".join([word.capitalize() for word in agent_id.split("_")]) + "Agent"
        target_str = f"""{{
            "status": "completed",
            "message": "Processed successfully by {class_name}"
        }}"""
        
        if target_str in content:
            # We need to prepend 'import random' if not present
            if "import random" not in content:
                content = "import random\\n" + content
            
            content = content.replace(target_str, workload_str)
            with open(file_path, "w") as f:
                f.write(content)
            print(f"Updated {agent_id}_agent.py")
        else:
            print(f"Could not find target string in {agent_id}_agent.py")
    else:
        print(f"File not found: {file_path}")

print("Done injecting simulated workloads!")
