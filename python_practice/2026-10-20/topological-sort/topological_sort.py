"""Topological sorting for directed graphs using Kahn's algorithm."""


def topological_sort(graph):
    """Return a deterministic topological order or raise ValueError on cycles.

    graph maps each vertex to an iterable of outgoing neighbors. Neighbors
    that are not explicit keys are still treated as vertices.
    """
    adjacency = {vertex: set(neighbors) for vertex, neighbors in graph.items()}
    vertices = set(adjacency)
    for neighbors in adjacency.values():
        vertices.update(neighbors)
    for vertex in vertices:
        adjacency.setdefault(vertex, set())

    indegree = {vertex: 0 for vertex in vertices}
    for neighbors in adjacency.values():
        for neighbor in neighbors:
            indegree[neighbor] += 1

    ready = sorted((v for v in vertices if indegree[v] == 0), key=repr)
    order = []
    while ready:
        vertex = ready.pop(0)
        order.append(vertex)
        for neighbor in sorted(adjacency[vertex], key=repr):
            indegree[neighbor] -= 1
            if indegree[neighbor] == 0:
                ready.append(neighbor)
                ready.sort(key=repr)

    if len(order) != len(vertices):
        raise ValueError("graph contains a directed cycle")
    return order
