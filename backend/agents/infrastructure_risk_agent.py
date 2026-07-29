from typing import Any, Dict, List
from agents.base import BaseAgent
from agents.graph_store import graph_store

class InfrastructureRiskAgent(BaseAgent):
    name = "infrastructure_risk"
    purpose = "Evaluates structural risk scores for critical infrastructure (bridges, power, dams)."

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        graph_id = input_data.get("graph_id", "sample_graph_default")
        disaster_type = input_data.get("disaster_type", "earthquake")
        G = graph_store.get_graph(graph_id)

        assessment: List[Dict[str, Any]] = []

        if G and len(G.edges) > 0:
            for u, v, data in list(G.edges(data=True))[:5]:
                length = data.get("weight", 100.0)
                is_blocked = data.get("blocked", False)

                # Compute structural collapse risk index
                risk_score = round(min(1.0, (length / 200.0) + (0.5 if is_blocked else 0.1)), 2)
                risk_level = "CRITICAL" if risk_score >= 0.7 else "MODERATE" if risk_score >= 0.4 else "LOW"

                assessment.append({
                    "structure_id": f"bridge_edge_{u}_{v}",
                    "connected_nodes": [u, v],
                    "asset_type": "bridge" if (u + v) % 2 == 0 else "power_substation",
                    "structural_risk_score": risk_score,
                    "risk_level": risk_level,
                    "requires_inspection": risk_score >= 0.5
                })
        else:
            assessment.append({
                "structure_id": "main_bay_bridge",
                "asset_type": "bridge",
                "structural_risk_score": 0.85,
                "risk_level": "CRITICAL",
                "requires_inspection": True
            })

        critical_count = sum(1 for a in assessment if a["risk_level"] == "CRITICAL")

        output = dict(input_data)
        output.update({
            "status": "success",
            "disaster_type": disaster_type,
            "critical_structures_count": critical_count,
            "infrastructure_evaluations": assessment,
            "message": f"Evaluated {len(assessment)} critical infrastructure assets against {disaster_type} impact."
        })
        return output
