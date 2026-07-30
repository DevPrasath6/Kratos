import math
import uuid
import networkx as nx
from typing import Any, Dict, List, Tuple
from agents.base import BaseAgent
from agents.graph_store import graph_store


class RoadGraphAgent(BaseAgent):
    name: str = "road_graph"

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Input options:
        - { "use_sample": True }
        - { "segments": [[x1, y1, x2, y2], ...], "tolerance": 15.0 }

        Output:
        GeoJSON-like dict representation of the graph + graph_id.
        """
        use_sample = input_data.get("use_sample", False)
        segments = input_data.get("segments")

        if use_sample:
            graph, graph_id = self.sample_graph()
            return self.serialize_graph(graph, graph_id, input_data)

        if not segments:
            graph, graph_id = self.sample_graph()
            return self.serialize_graph(graph, graph_id, input_data)

        tolerance = float(input_data.get("tolerance", 15.0))
        graph, graph_id = self.build_graph_from_segments(segments, tolerance)
        return self.serialize_graph(graph, graph_id, input_data)

    def build_graph_from_segments(self, segments: List[List[int]], tolerance: float) -> Tuple[nx.Graph, str]:
        G = nx.Graph()
        node_coords: List[Tuple[float, float]] = []

        def get_or_create_node_id(pt: Tuple[float, float]) -> int:
            for idx, existing in enumerate(node_coords):
                dist = math.hypot(pt[0] - existing[0], pt[1] - existing[1])
                if dist <= tolerance:
                    return idx
            idx = len(node_coords)
            node_coords.append(pt)
            
            geo_base_lat, geo_base_lng = 37.7749, -122.4194
            geo_lat = round(geo_base_lat - (pt[1] / 10000.0), 6)
            geo_lng = round(geo_base_lng + (pt[0] / 10000.0), 6)
            
            G.add_node(idx, pos=list(pt), geo_pos=[geo_lat, geo_lng])
            return idx

        for seg in segments:
            if len(seg) < 4:
                continue
            p1 = (float(seg[0]), float(seg[1]))
            p2 = (float(seg[2]), float(seg[3]))

            u = get_or_create_node_id(p1)
            v = get_or_create_node_id(p2)

            if u != v:
                length = math.hypot(p2[0] - p1[0], p2[1] - p1[1])
                G.add_edge(
                    u,
                    v,
                    weight=round(length, 2),
                    blocked=False,
                    speed_multiplier=1.0,
                )

        graph_id = f"graph_{uuid.uuid4().hex[:8]}"
        graph_store.save_graph(graph_id, G)
        return G, graph_id

    def sample_graph(self) -> Tuple[nx.Graph, str]:
        """Returns a sample graph with 9 nodes (3x3 grid layout) with real geographic lat/lng metadata."""
        G = nx.Graph()
        # 3x3 grid coordinates + geographic lat/lng mapping
        coords = {
            0: [0, 0], 1: [100, 0], 2: [200, 0],
            3: [0, 100], 4: [100, 100], 5: [200, 100],
            6: [0, 200], 7: [100, 200], 8: [200, 200],
        }
        geo_base_lat, geo_base_lng = 37.7749, -122.4194

        for n, pos in coords.items():
            geo_lat = round(geo_base_lat + (pos[1] / 10000.0), 4)
            geo_lng = round(geo_base_lng + (pos[0] / 10000.0), 4)
            G.add_node(n, pos=pos, geo_pos=[geo_lat, geo_lng])

        edges = [
            (0, 1, 100.0), (1, 2, 100.0),
            (3, 4, 100.0), (4, 5, 100.0),
            (6, 7, 100.0), (7, 8, 100.0),
            (0, 3, 100.0), (3, 6, 100.0),
            (1, 4, 100.0), (4, 7, 100.0),
            (2, 5, 100.0), (5, 8, 100.0),
            (1, 3, 141.4), (4, 8, 141.4),  # Diagonals for interest
        ]

        for u, v, w in edges:
            G.add_edge(u, v, weight=w, blocked=False, speed_multiplier=1.0)

        graph_id = "sample_graph_default"
        graph_store.save_graph(graph_id, G)
        return G, graph_id

    @staticmethod
    def serialize_graph(graph: nx.Graph, graph_id: str, input_data: Dict[str, Any] = None) -> Dict[str, Any]:
        nodes_list = []
        for n, data in graph.nodes(data=True):
            nodes_list.append({
                "id": n,
                "pos": data.get("pos", [0, 0]),
                "geo_pos": data.get("geo_pos", [37.7749, -122.4194]),
            })

        edges_list = []
        for u, v, data in graph.edges(data=True):
            edges_list.append({
                "source": u,
                "target": v,
                "weight": data.get("weight", 1.0),
                "blocked": data.get("blocked", False),
                "speed_multiplier": data.get("speed_multiplier", 1.0),
            })

        res = dict(input_data) if input_data else {}
        res.update({
            "graph_id": graph_id,
            "nodes": nodes_list,
            "edges": edges_list,
            "node_count": len(nodes_list),
            "edge_count": len(edges_list),
        })
        return res
