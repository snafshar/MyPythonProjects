"""Breadth-first shortest-path reconstruction with validation and distance."""

from collections import deque


def shortest_path(graph, source, target):
    if source not in graph or target not in graph:
        return []
    queue = deque([source])
    parent = {source: None}
    while queue:
        node = queue.popleft()
        if node == target:
            break
        for neighbour in graph.get(node, []):
            if neighbour not in parent:
                parent[neighbour] = node
                queue.append(neighbour)
    if target not in parent:
        return []
    path, node = [], target
    while node is not None:
        path.append(node)
        node = parent[node]
    return path[::-1]


def shortest_distance(graph, source, target):
    path = shortest_path(graph, source, target)
    return len(path) - 1 if path else None


if __name__ == "__main__":
    graph = {"A": ["B", "D"], "B": ["A", "C"], "C": ["B"], "D": ["A"]}
    path = shortest_path(graph, "A", "C")
    print("Path:", " -> ".join(path))
    print("Hops:", shortest_distance(graph, "A", "C"))
