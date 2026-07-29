from typing import Any, Dict, List
from agents.base import BaseAgent
from agents.graph_store import graph_store
from agents.road_graph_agent import RoadGraphAgent
from agents.route_planning_agent import RoutePlanningAgent


DEFAULT_UNITS: List[Dict[str, Any]] = [
    {"id": "amb_01", "name": "Ambulance 1", "type": "medical", "location_node": 0, "status": "busy"},
    {"id": "amb_02", "name": "Ambulance 2", "type": "medical", "location_node": 2, "status": "available"},
    {"id": "fire_01", "name": "Fire Truck 1", "type": "fire", "location_node": 6, "status": "available"},
    {"id": "pol_01", "name": "Police Cruiser 1", "type": "police", "location_node": 1, "status": "available"},
]

PRIORITY_TYPE_MAP: Dict[str, List[str]] = {
    "medical": ["medical", "fire", "police"],
    "casualty": ["medical", "fire", "police"],
    "fire": ["fire", "medical", "police"],
    "security": ["police", "fire", "medical"],
    "general": ["medical", "fire", "police"],
}


class ResourceAllocationAgent(BaseAgent):
    name: str = "resource_allocation"

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Input:
        - graph_id: str
        - incident_node: int (default 8)
        - incident_type: "medical" | "casualty" | "fire" | "security" | "general" (default "medical")
        - units: list of unit dicts (optional)
        """
        graph_id = input_data.get("graph_id", "sample_graph_default")
        G = graph_store.get_graph(graph_id)

        if G is None:
            road_agent = RoadGraphAgent()
            G, graph_id = road_agent.sample_graph()

        incident_node = int(input_data.get("incident_node", 8))
        incident_type = input_data.get("incident_type", "medical").lower()
        units = input_data.get("units", DEFAULT_UNITS)

        router = RoutePlanningAgent()
        priority_order = PRIORITY_TYPE_MAP.get(incident_type, PRIORITY_TYPE_MAP["general"])

        # Filter available units
        available_units = [u for u in units if u.get("status") == "available"]

        if not available_units:
            res = dict(input_data)
            res.update({
                "graph_id": graph_id,
                "incident_node": incident_node,
                "incident_type": incident_type,
                "assigned_unit": None,
                "allocation_status": "no_units_available",
            })
            return res

        candidates = []
        for unit in available_units:
            loc = unit.get("location_node", 0)
            route_res = await router.run({
                "graph_id": graph_id,
                "source": loc,
                "destination": incident_node,
            })

            if route_res.get("route_found") and route_res.get("safe_distance") != -1.0:
                unit_type = unit.get("type", "general")
                priority_rank = priority_order.index(unit_type) if unit_type in priority_order else 99
                dist = route_res["safe_distance"]
                eta = route_res["safe_eta"]

                candidates.append({
                    "unit": unit,
                    "priority_rank": priority_rank,
                    "safe_distance": dist,
                    "safe_eta": eta,
                    "safe_path": route_res["safe_path"],
                    "avoided_blocked_edges": route_res["avoided_blocked_edges"],
                })

        if not candidates:
            res = dict(input_data)
            res.update({
                "graph_id": graph_id,
                "incident_node": incident_node,
                "incident_type": incident_type,
                "assigned_unit": None,
                "allocation_status": "no_safe_route_to_incident",
            })
            return res

        # Sort candidates primarily by type priority rank, secondarily by safe distance
        candidates.sort(key=lambda c: (c["priority_rank"], c["safe_distance"]))
        best = candidates[0]

        output = dict(input_data)  # Preserve pipeline chain
        output.update({
            "graph_id": graph_id,
            "incident_node": incident_node,
            "incident_type": incident_type,
            "assigned_unit": best["unit"],
            "safe_distance": best["safe_distance"],
            "safe_eta": best["safe_eta"],
            "safe_path": best["safe_path"],
            "avoided_blocked_edges": best["avoided_blocked_edges"],
            "allocation_status": "assigned",
        })
        return output
