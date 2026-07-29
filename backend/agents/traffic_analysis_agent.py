import random
from typing import Any, Dict, List
from agents.base import BaseAgent
from agents.graph_store import graph_store
from agents.road_graph_agent import RoadGraphAgent


class TrafficAnalysisAgent(BaseAgent):
    name: str = "traffic_analysis"

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Input:
        - graph_id: str
        - assigned_vehicles: dict/list (optional vehicle density updates)
        - seed: int (default 42)
        """
        graph_id = input_data.get("graph_id", "sample_graph_default")
        G = graph_store.get_graph(graph_id)

        if G is None:
            road_agent = RoadGraphAgent()
            G, graph_id = road_agent.sample_graph()

        seed = int(input_data.get("seed", 42))
        rng = random.Random(seed)

        assigned_vehicles = input_data.get("assigned_vehicles", {})

        traffic_map: List[Dict[str, Any]] = []
        total_congestion = 0.0

        for u, v, data in G.edges(data=True):
            edge_key = f"{min(u, v)}-{max(u, v)}"
            vehicle_count = 0
            if isinstance(assigned_vehicles, dict):
                vehicle_count = assigned_vehicles.get(edge_key, 0)
            elif isinstance(assigned_vehicles, list):
                vehicle_count = len(assigned_vehicles)

            # Compute congestion based on NetworkX node centrality and vehicle density
            u_deg = G.degree(u) if G.has_node(u) else 1
            v_deg = G.degree(v) if G.has_node(v) else 1
            node_centrality_factor = min(0.4, (u_deg + v_deg) * 0.05)
            length_factor = min(0.1, (data.get("length", 10) / 1000.0))
            density_penalty = min(0.5, vehicle_count * 0.1)
            congestion_score = round(min(1.0, 0.05 + node_centrality_factor + length_factor + density_penalty), 2)

            if data.get("blocked", False):
                congestion_score = 1.0
                level = "blocked"
            elif congestion_score >= 0.7:
                level = "heavy"
            elif congestion_score >= 0.4:
                level = "moderate"
            else:
                level = "low"

            traffic_map.append({
                "edge": [u, v],
                "congestion_score": congestion_score,
                "level": level,
                "vehicle_count": vehicle_count,
            })
            total_congestion += congestion_score

        avg_congestion = round(total_congestion / len(traffic_map), 2) if traffic_map else 0.0

        output = dict(input_data)  # Preserve pipeline chain
        output.update({
            "graph_id": graph_id,
            "traffic_map": traffic_map,
            "average_congestion": avg_congestion,
        })
        return output
