from typing import Any, Dict, List
from agents.base import BaseAgent
from agents.graph_store import graph_store

class SupplyLogisticsAgent(BaseAgent):
    name = "supply_logistics"
    purpose = "Calculates weight/cargo distributions and helicopter drop coordinates for isolated regions."

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        graph_id = input_data.get("graph_id", "sample_graph_default")
        population_headcount = input_data.get("isolated_population", 250)
        G = graph_store.get_graph(graph_id)

        # Calculate required supplies
        water_liters = population_headcount * 3.0  # 3L per person / day
        ration_kits = population_headcount * 1.0   # 1 pack per person / day
        first_aid_kits = int(population_headcount / 20) + 1

        total_weight_kg = (water_liters * 1.0) + (ration_kits * 0.8) + (first_aid_kits * 2.5)

        # Select isolated drop nodes
        drop_zones: List[Dict[str, Any]] = []
        if G and len(G.nodes) > 0:
            blocked_nodes = [n for n, data in G.nodes(data=True) if data.get("blocked", False)]
            target_nodes = blocked_nodes if blocked_nodes else list(G.nodes())[:2]
            
            for n in target_nodes[:2]:
                pos = G.nodes[n].get("pos", [37.77, -122.41])
                drop_zones.append({
                    "drop_node_id": n,
                    "coordinates": {"lat": pos[0], "lng": pos[1]},
                    "allocated_weight_kg": round(total_weight_kg / max(1, len(target_nodes[:2])), 1),
                    "priority": "HIGH_URGENCY"
                })
        else:
            drop_zones.append({
                "drop_node_id": 4,
                "coordinates": {"lat": 37.7849, "lng": -122.4094},
                "allocated_weight_kg": round(total_weight_kg, 1),
                "priority": "HIGH_URGENCY"
            })

        output = dict(input_data)
        output.update({
            "status": "success",
            "isolated_population": population_headcount,
            "logistics_manifest": {
                "water_liters": water_liters,
                "ration_kits": ration_kits,
                "first_aid_kits": first_aid_kits,
                "total_payload_weight_kg": round(total_weight_kg, 1),
                "recommended_aircraft": "CH-47_Chinook" if total_weight_kg > 1000 else "UH-60_Blackhawk"
            },
            "air_drop_zones": drop_zones
        })
        return output
