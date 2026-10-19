"""Graph algorithms using adjacency dictionaries."""


from heapq import heappop, heappush
from collections import deque


def bfs_shortest_path(graph, start, goal):
    """Return a shortest unweighted path as a node list, or None.

    graph maps each node to an iterable of neighboring nodes.
    """
    queue = deque([start])
    parent = {start: None}
    while queue:
        node = queue.popleft()
        if node == goal:
            path = []
            while node is not None:
                path.append(node)
                node = parent[node]
            return list(reversed(path))
        for neighbor in graph.get(node, ()):
            if neighbor not in parent:
                parent[neighbor] = node
                queue.append(neighbor)
    return None


def dijkstra(graph, start):
    """Return shortest non-negative distances from start.

    graph maps each node to (neighbor, weight) pairs. Unreachable nodes are
    absent from the returned dictionary. Negative edge weights raise ValueError.
    """
    distances = {start: 0}
    heap = [(0, start)]
    while heap:
        distance, node = heappop(heap)
        if distance != distances.get(node):
            continue
        for neighbor, weight in graph.get(node, ()):
            if weight < 0:
                raise ValueError("Dijkstra requires non-negative edge weights")
            candidate = distance + weight
            if candidate < distances.get(neighbor, float("inf")):
                distances[neighbor] = candidate
                heappush(heap, (candidate, neighbor))
    return distances
