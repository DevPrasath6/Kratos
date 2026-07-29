import networkx as nx
from typing import Any, Dict, List, Tuple
from agents.base import BaseAgent
from agents.graph_store import graph_store
from agents.road_graph_agent import RoadGraphAgent


class RoutePlanningAgent(BaseAgent):
    name: str = "route_planning"

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Input:
        - graph_id: str
        - source: int (node id, default 0)
        - destination: int (node id, default 8)
        - base_speed: float (speed unit per distance unit, default 1.0)
        """
        # Pipeline compatibility: if input_data is coming from disaster_sim output, pass through context
        graph_id = input_data.get("graph_id", "sample_graph_default")
        G = graph_store.get_graph(graph_id)

        if G is None:
            road_agent = RoadGraphAgent()
            G, graph_id = road_agent.sample_graph()

        nodes = list(G.nodes())
        if not nodes:
            raise ValueError(f"Graph '{graph_id}' has no nodes.")

        raw_source = input_data.get("source")
        try:
            source = int(raw_source) if raw_source is not None else nodes[0]
        except (ValueError, TypeError):
            source = nodes[0]

        raw_dest = input_data.get("destination")
        try:
            destination = int(raw_dest) if raw_dest is not None else (nodes[-1] if len(nodes) > 1 else nodes[0])
        except (ValueError, TypeError):
            destination = nodes[-1] if len(nodes) > 1 else nodes[0]

        if source not in G:
            source = nodes[0]
        if destination not in G:
            destination = nodes[-1]

        base_speed = float(input_data.get("base_speed", 1.0))

        # 1. Compute unconstrained shortest path (ignoring blocked status)
        shortest_path, shortest_dist = self._compute_dijkstra(G, source, destination, ignore_blocked=True)

        # 2. Compute safe path (excluding blocked edges and weighting by speed_multiplier)
        safe_path, safe_dist, safe_eta, avoided_blocked_edges = self._compute_safe_path(
            G, source, destination, base_speed
        )

        output = dict(input_data)  # Preserve pipeline chain data
        output.update({
            "graph_id": graph_id,
            "source": source,
            "destination": destination,
            "shortest_path": shortest_path,
            "shortest_distance": round(shortest_dist, 2),
            "safe_path": safe_path,
            "safe_distance": round(safe_dist, 2),
            "safe_eta": round(safe_eta, 2),
            "avoided_blocked_edges": avoided_blocked_edges,
            "route_found": len(safe_path) > 0,
        })
        return output

    def _compute_dijkstra(
        self, G: nx.Graph, source: int, target: int, ignore_blocked: bool = False
    ) -> Tuple[List[int], float]:
        try:
            if ignore_blocked:
                path = nx.shortest_path(G, source=source, target=target, weight="weight")
                dist = nx.shortest_path_length(G, source=source, target=target, weight="weight")
                return path, round(float(dist), 2)
            else:
                # Create a view filtering out blocked edges
                def filter_edge(u, v):
                    return not G[u][v].get("blocked", False)
                sub_G = nx.subgraph_view(G, filter_edge=filter_edge)
                path = nx.shortest_path(sub_G, source=source, target=target, weight="weight")
                dist = nx.shortest_path_length(sub_G, source=source, target=target, weight="weight")
                return path, round(float(dist), 2)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return [], -1.0

    def _compute_safe_path(
        self, G: nx.Graph, source: int, target: int, base_speed: float
    ) -> Tuple[List[int], float, float, List[List[int]]]:
        # Filter out blocked edges
        blocked_edges = []
        valid_G = nx.Graph()

        for n, d in G.nodes(data=True):
            valid_G.add_node(n, **d)

        for u, v, d in G.edges(data=True):
            if d.get("blocked", False):
                blocked_edges.append([u, v])
            else:
                # Adjusted edge weight for ETA based on speed_multiplier
                mult = max(0.1, float(d.get("speed_multiplier", 1.0)))
                travel_time = d.get("weight", 1.0) / (base_speed * mult)
                valid_G.add_edge(u, v, weight=d.get("weight", 1.0), travel_time=travel_time)

        try:
            path = nx.shortest_path(valid_G, source=source, target=target, weight="travel_time")
            path_dist = 0.0
            path_eta = 0.0
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                edge_data = valid_G[u][v]
                path_dist += edge_data.get("weight", 1.0)
                path_eta += edge_data.get("travel_time", 1.0)

            # Identify which blocked edges were avoided by comparing against all graph blocked edges
            avoided = [edge for edge in blocked_edges]

            return path, path_dist, path_eta, avoided
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            return [], -1.0, -1.0, blocked_edges
