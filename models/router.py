from __future__ import annotations

from math import sqrt
from typing import Any

import networkx as nx


class TrafficRouter:
    def __init__(self) -> None:
        self.graph = nx.Graph()
        self._build_graph()

    def _build_graph(self) -> None:
        nodes = {
            "A": (12.9716, 77.5946),
            "B": (12.9750, 77.6000),
            "C": (12.9700, 77.6100),
            "D": (12.9650, 77.6020),
            "E": (12.9680, 77.5920),
        }
        for node_id, coord in nodes.items():
            self.graph.add_node(node_id, coord=coord)

        edges = [("A", "B"), ("B", "C"), ("A", "E"), ("E", "D"), ("D", "C"), ("A", "D")]
        for u, v in edges:
            self.graph.add_edge(u, v, distance=self._distance(nodes[u], nodes[v]))

    @property
    def edge_ids(self) -> list[str]:
        return [self._edge_id(u, v) for u, v in self.graph.edges]

    def _edge_id(self, u: str, v: str) -> str:
        return f"{min(u, v)}-{max(u, v)}"

    def _distance(self, a: tuple[float, float], b: tuple[float, float]) -> float:
        return sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    def _nearest_node(self, coord: list[float]) -> str:
        lat, lon = float(coord[0]), float(coord[1])
        return min(
            self.graph.nodes,
            key=lambda node: self._distance((lat, lon), self.graph.nodes[node]["coord"]),
        )

    def _weighted_graph(self, edge_predictions: dict[str, dict[str, Any]]) -> nx.Graph:
        weighted = self.graph.copy()
        penalty = {"Low": 1.0, "Moderate": 1.5, "Severe": 2.2}

        for u, v, data in weighted.edges(data=True):
            edge_id = self._edge_id(u, v)
            level = edge_predictions.get(edge_id, {}).get("congestion_level", "Low")
            data["weight"] = data["distance"] * penalty.get(level, 1.0)
        return weighted

    def recommend_route(
        self,
        start: list[float],
        end: list[float],
        edge_predictions: dict[str, dict[str, Any]],
        algorithm: str = "dijkstra",
    ) -> dict[str, Any]:
        weighted = self._weighted_graph(edge_predictions)
        source = self._nearest_node(start)
        target = self._nearest_node(end)

        if algorithm.lower() == "astar":
            path_nodes = nx.astar_path(
                weighted,
                source,
                target,
                heuristic=lambda n1, n2: self._distance(weighted.nodes[n1]["coord"], weighted.nodes[n2]["coord"]),
                weight="weight",
            )
        else:
            path_nodes = nx.shortest_path(weighted, source=source, target=target, weight="weight")

        coordinates = [weighted.nodes[node]["coord"] for node in path_nodes]
        total_weight = nx.path_weight(weighted, path_nodes, weight="weight")

        return {
            "algorithm": algorithm,
            "path_nodes": path_nodes,
            "path_coordinates": coordinates,
            "estimated_weight": round(total_weight, 6),
        }
