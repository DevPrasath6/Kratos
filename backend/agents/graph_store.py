import networkx as nx
from typing import Dict, Optional

class GraphStore:
    def __init__(self):
        self._graphs: Dict[str, nx.Graph] = {}

    def save_graph(self, graph_id: str, graph: nx.Graph) -> None:
        self._graphs[graph_id] = graph

    def get_graph(self, graph_id: str) -> Optional[nx.Graph]:
        return self._graphs.get(graph_id)

    def list_graph_ids(self) -> list[str]:
        return list(self._graphs.keys())

graph_store = GraphStore()
