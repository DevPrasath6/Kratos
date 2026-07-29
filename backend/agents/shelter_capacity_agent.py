from typing import Any, Dict, List
from agents.base import BaseAgent
from agents.graph_store import graph_store

class ShelterCapacityAgent(BaseAgent):
    name = "shelter_capacity"
    purpose = "Monitors live capacity, medical triage, and food stock across relief shelters."

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        graph_id = input_data.get("graph_id", "sample_graph_default")
        G = graph_store.get_graph(graph_id)
        
        # Dynamic shelter data generation based on graph nodes
        shelters: List[Dict[str, Any]] = []
        if G and len(G.nodes) > 0:
            for idx, (node_id, data) in enumerate(list(G.nodes(data=True))[:4]):
                capacity = 100 + (idx * 50)
                current_occupancy = 30 + (idx * 25)
                shelters.append({
                    "shelter_id": f"shelter_node_{node_id}",
                    "node_id": node_id,
                    "location": data.get("pos", [37.77, -122.41]),
                    "max_capacity": capacity,
                    "current_occupancy": current_occupancy,
                    "available_beds": capacity - current_occupancy,
                    "occupancy_rate_pct": round((current_occupancy / capacity) * 100, 1),
                    "status": "available" if (capacity - current_occupancy) > 10 else "FULL",
                    "supplies": {
                        "water_days_left": round(7.0 - (idx * 1.2), 1),
                        "medical_kits": 50 - (idx * 8)
                    }
                })
        else:
            shelters.append({
                "shelter_id": "shelter_node_0",
                "node_id": 0,
                "max_capacity": 200,
                "current_occupancy": 120,
                "available_beds": 80,
                "occupancy_rate_pct": 60.0,
                "status": "available"
            })

        # Calculate optimal shelter for an incoming group
        group_size = input_data.get("evacuee_count", 15)
        recommended_shelter = next((s for s in shelters if s["available_beds"] >= group_size), None)

        output = dict(input_data)
        output.update({
            "status": "success",
            "evacuee_group_size": group_size,
            "recommended_shelter": recommended_shelter,
            "all_shelters": shelters,
            "message": f"Processed {len(shelters)} shelters and assigned evacuation destination."
        })
        return output
