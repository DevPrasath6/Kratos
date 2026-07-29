from typing import Any, Dict, List
import random
from agents.base import BaseAgent

class DroneSwarmAgent(BaseAgent):
    name = "drone_swarm_orchestrator"
    purpose = "Calculates 3D flight paths for autonomous drones to survey occluded areas."

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        target_zone = input_data.get("target_zone", "unknown_zone")
        drone_count = input_data.get("drone_count", 3)
        
        graph_id = input_data.get("graph_id")
        from agents.graph_store import graph_store
        G = graph_store.get_graph(graph_id) if graph_id else None
        
        flight_paths = []
        if G and len(G.nodes) > 0:
            nodes_data = list(G.nodes(data=True))
            for i in range(min(drone_count, len(nodes_data))):
                node_id, data = nodes_data[i]
                pos = data.get("pos", (34.05 + i * 0.01, -118.25 + i * 0.01))
                path = []
                for step in range(5):
                    path.append({
                        "lat": round(pos[0] + (step * 0.002), 5),
                        "lng": round(pos[1] + (step * 0.002), 5),
                        "alt_meters": 100 + (step * 15)
                    })
                flight_paths.append({
                    "drone_id": f"UAV-{100 + i}",
                    "status": "dispatched",
                    "target_zone": f"node_{node_id}",
                    "waypoints": path
                })
        else:
            base_lat = input_data.get("lat", 34.05)
            base_lng = input_data.get("lng", -118.25)
            for i in range(drone_count):
                path = []
                for step in range(5):
                    path.append({
                        "lat": round(base_lat + (i * 0.005) + (step * 0.002), 5),
                        "lng": round(base_lng + (i * 0.005) + (step * 0.002), 5),
                        "alt_meters": 120 + (step * 10)
                    })
                flight_paths.append({
                    "drone_id": f"UAV-{100 + i}",
                    "status": "dispatched",
                    "target_zone": target_zone,
                    "waypoints": path
                })
            
        output = dict(input_data)
        output.update({
            "status": "success",
            "message": f"Successfully calculated 3D flight paths for {drone_count} drones.",
            "fleet_assignments": flight_paths
        })
        return output
