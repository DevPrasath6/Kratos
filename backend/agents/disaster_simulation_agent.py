import math
from typing import Any, Dict, List, Tuple
from agents.base import BaseAgent
from agents.graph_store import graph_store
from agents.road_graph_agent import RoadGraphAgent


# Disaster impact lookup table: (block_threshold_severity, speed_mult_low, speed_mult_high)
DISASTER_LOOKUP: Dict[str, Dict[str, Any]] = {
    "flood": {"block_min_severity": 4, "speed_mult_low": 0.3, "speed_mult_high": 0.0},
    "landslide": {"block_min_severity": 3, "speed_mult_low": 0.2, "speed_mult_high": 0.0},
    "earthquake": {"block_min_severity": 4, "speed_mult_low": 0.4, "speed_mult_high": 0.0},
    "wildfire": {"block_min_severity": 4, "speed_mult_low": 0.5, "speed_mult_high": 0.1},
    "cyclone": {"block_min_severity": 5, "speed_mult_low": 0.5, "speed_mult_high": 0.2},
}


class DisasterSimulationAgent(BaseAgent):
    name: str = "disaster_simulation"

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Input:
        - graph_id: str (default: "sample_graph_default")
        - disaster_type: "flood" | "earthquake" | "cyclone" | "landslide" | "wildfire"
        - severity: 1 to 5 (default 3)
        - center: [x, y] (optional, defaults to graph center)
        - radius: float (optional, defaults to 120.0)
        """
        graph_id = input_data.get("graph_id", "sample_graph_default")
        G = graph_store.get_graph(graph_id)

        if G is None:
            # Auto-generate sample graph if not present
            road_agent = RoadGraphAgent()
            G, graph_id = road_agent.sample_graph()

        disaster_type = input_data.get("disaster_type", "flood").lower()
        raw_sev = input_data.get("severity")
        severity = int(raw_sev) if raw_sev is not None else 3
        severity = max(1, min(5, severity))

        # Calculate bounding box / default center if not provided
        center = input_data.get("center")
        if not center:
            xs = [d["pos"][0] for _, d in G.nodes(data=True) if "pos" in d]
            ys = [d["pos"][1] for _, d in G.nodes(data=True) if "pos" in d]
            center = [(min(xs) + max(xs)) / 2.0 if xs else 100.0, (min(ys) + max(ys)) / 2.0 if ys else 100.0]

        radius = float(input_data.get("radius", 120.0))

        rules = DISASTER_LOOKUP.get(disaster_type, DISASTER_LOOKUP["flood"])
        should_block = severity >= rules["block_min_severity"]
        speed_mult = rules["speed_mult_high"] if should_block else rules["speed_mult_low"]

        blocked_edges: List[List[int]] = []
        degraded_edges: List[Dict[str, Any]] = []

        for u, v, data in G.edges(data=True):
            pos_u = G.nodes[u].get("pos", [0, 0])
            pos_v = G.nodes[v].get("pos", [0, 0])
            edge_center_x = (pos_u[0] + pos_v[0]) / 2.0
            edge_center_y = (pos_u[1] + pos_v[1]) / 2.0

            dist = math.hypot(edge_center_x - center[0], edge_center_y - center[1])

            if dist <= radius:
                if should_block:
                    data["blocked"] = True
                    data["speed_multiplier"] = 0.0
                    blocked_edges.append([u, v])
                else:
                    data["blocked"] = False
                    data["speed_multiplier"] = speed_mult
                    degraded_edges.append({"edge": [u, v], "speed_multiplier": speed_mult})
            else:
                # Reset edges outside radius
                data["blocked"] = False
                data["speed_multiplier"] = 1.0

        output = dict(input_data)
        output.update({
            "graph_id": graph_id,
            "disaster_type": disaster_type,
            "severity": severity,
            "center": center,
            "radius": radius,
            "blocked_edges": blocked_edges,
            "degraded_edges": degraded_edges,
            "affected_edge_count": len(blocked_edges) + len(degraded_edges),
        })
        return output
