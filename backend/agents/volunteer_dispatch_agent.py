from typing import Any, Dict, List
from agents.base import BaseAgent
from agents.graph_store import graph_store
from agents.road_graph_agent import RoadGraphAgent
from agents.route_planning_agent import RoutePlanningAgent


DEFAULT_VOLUNTEERS: List[Dict[str, Any]] = [
    {"id": "vol_01", "name": "Dr. Sarah Jenkins", "role": "Physician", "location_node": 3, "status": "available"},
    {"id": "vol_02", "name": "Nurse Mark Davis", "role": "ER Nurse", "location_node": 7, "status": "available"},
    {"id": "vol_03", "name": "Alex Carter", "role": "Paramedic Assistant", "location_node": 0, "status": "busy"},
]


class VolunteerHealthcareDispatchAgent(BaseAgent):
    name: str = "volunteer_healthcare_dispatch"

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Input:
        - graph_id: str
        - incident_node: int (default 8)
        - volunteers: list of volunteer dicts (optional)
        """
        graph_id = input_data.get("graph_id", "sample_graph_default")
        G = graph_store.get_graph(graph_id)

        if G is None:
            road_agent = RoadGraphAgent()
            G, graph_id = road_agent.sample_graph()

        incident_node = int(input_data.get("incident_node", 8))
        volunteers = input_data.get("volunteers", DEFAULT_VOLUNTEERS)

        router = RoutePlanningAgent()

        available_volunteers = [v for v in volunteers if v.get("status") == "available"]

        if not available_volunteers:
            return {
                "graph_id": graph_id,
                "incident_node": incident_node,
                "assigned_volunteer": None,
                "dispatch_status": "no_volunteers_available",
                "instructions": "No available volunteers/healthcare personnel to dispatch.",
            }

        candidates = []
        for vol in available_volunteers:
            loc = vol.get("location_node", 0)
            route_res = await router.run({
                "graph_id": graph_id,
                "source": loc,
                "destination": incident_node,
            })

            if route_res.get("route_found") and route_res.get("safe_distance") != -1.0:
                candidates.append({
                    "volunteer": vol,
                    "safe_distance": route_res["safe_distance"],
                    "safe_eta": route_res["safe_eta"],
                    "safe_path": route_res["safe_path"],
                    "avoided_blocked_edges": route_res["avoided_blocked_edges"],
                })

        if not candidates:
            res = dict(input_data)
            res.update({
                "graph_id": graph_id,
                "incident_node": incident_node,
                "assigned_volunteer": None,
                "dispatch_status": "no_safe_route",
                "instructions": "No safe route available for volunteer dispatch.",
            })
            return res

        # Sort by shortest safe distance
        candidates.sort(key=lambda c: c["safe_distance"])
        best = candidates[0]
        vol = best["volunteer"]

        blocked_count = len(best["avoided_blocked_edges"])
        avoid_str = (
            f"avoiding {blocked_count} blocked road segment(s)"
            if blocked_count > 0
            else "all clear routes"
        )
        instructions = (
            f"DISPATCH ORDER for {vol['name']} ({vol['role']}): "
            f"Proceed from Node {vol['location_node']} to Incident at Node {incident_node} "
            f"via Safe Route {best['safe_path']}, {avoid_str}. "
            f"Estimated ETA: {best['safe_eta']} min ({best['safe_distance']} km)."
        )

        output = dict(input_data)  # Preserve pipeline chain
        output.update({
            "graph_id": graph_id,
            "incident_node": incident_node,
            "assigned_volunteer": vol,
            "safe_distance": best["safe_distance"],
            "safe_eta": best["safe_eta"],
            "safe_path": best["safe_path"],
            "avoided_blocked_edges": best["avoided_blocked_edges"],
            "dispatch_status": "dispatched",
            "instructions": instructions,
        })
        return output
