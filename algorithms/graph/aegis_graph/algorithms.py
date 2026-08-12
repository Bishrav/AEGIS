from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field


@dataclass
class Graph:
    adjacency: dict[str, dict[str, float]] = field(default_factory=dict)

    def add_edge(self, source: str, target: str, weight: float = 1.0) -> None:
        self.adjacency.setdefault(source, {})[target] = weight
        self.adjacency.setdefault(target, {})


def bfs_impact(graph: Graph, start: str, max_depth: int | None = None) -> list[str]:
    visited = {start}
    queue = deque([(start, 0)])
    result: list[str] = []
    while queue:
        node, depth = queue.popleft()
        result.append(node)
        if max_depth is not None and depth >= max_depth:
            continue
        for neighbor in graph.adjacency.get(node, {}):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, depth + 1))
    return result


def shortest_path(graph: Graph, start: str, target: str) -> tuple[float, list[str]]:
    distances = {node: float("inf") for node in graph.adjacency}
    previous: dict[str, str | None] = {node: None for node in graph.adjacency}
    distances[start] = 0.0
    unvisited = set(graph.adjacency)
    while unvisited:
        current = min(unvisited, key=lambda node: distances[node])
        unvisited.remove(current)
        if current == target or distances[current] == float("inf"):
            break
        for neighbor, weight in graph.adjacency[current].items():
            candidate = distances[current] + weight
            if candidate < distances[neighbor]:
                distances[neighbor] = candidate
                previous[neighbor] = current
    if distances.get(target, float("inf")) == float("inf"):
        return float("inf"), []
    path = []
    node: str | None = target
    while node is not None:
        path.append(node)
        node = previous[node]
    return distances[target], list(reversed(path))

