from typing import Any, Dict
from agents.base import BaseAgent
from agents.graph_store import graph_store
import networkx as nx

class TelecomMeshAgent(BaseAgent):
    name = "telecom_mesh"
    purpose = "Calculates optimal line-of-sight deployments for temporary cell towers (COWs)."

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        graph_id = input_data.get("graph_id", "default_graph")
        G = graph_store.get_graph(graph_id)

        if not G or len(G.nodes) == 0:
            from agents.road_graph_agent import RoadGraphAgent
            graph_res = await RoadGraphAgent().run({"use_sample": True})
            graph_id = graph_res.get("graph_id", "sample_graph_default")
            G = graph_store.get_graph(graph_id)

        if not G or len(G.nodes) == 0:
            return {
                "status": "error",
                "message": f"Graph '{graph_id}' not found or empty."
            }

        # We want to find the most "central" nodes that are NOT blocked by the disaster
        safe_nodes = [n for n, attr in G.nodes(data=True) if not attr.get('blocked', False)]
        
        if not safe_nodes:
             return {
                "status": "error",
                "message": "No safe nodes available for COW deployment."
            }
             
        # Create a subgraph of only safe nodes to calculate centrality
        safe_subgraph = G.subgraph(safe_nodes)
        
        # Calculate degree centrality to find highly connected intersections
        centrality = nx.degree_centrality(safe_subgraph)
        
        # Sort nodes by centrality, highest first
        sorted_nodes = sorted(centrality.items(), key=lambda item: item[1], reverse=True)
        
        # Select top 3 deployment sites
        deployment_sites = []
        for i in range(min(3, len(sorted_nodes))):
            node_id = sorted_nodes[i][0]
            deployment_sites.append({
                "node": node_id,
                "centrality_score": round(sorted_nodes[i][1], 3),
                "recommended_hardware": "COW_TYPE_A" if i == 0 else "MESH_NODE",
                "estimated_coverage_radius_meters": 5000 if i == 0 else 1500
            })
            
        output = dict(input_data)
        output.update({
            "status": "success",
            "message": f"Calculated {len(deployment_sites)} optimal deployment sites.",
            "deployment_plan": deployment_sites
        })
        return output
