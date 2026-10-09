#!/usr/bin/env python3
"""Reproducible graph-based network topology and routing simulator."""

from collections import deque
import random
import statistics


class NetworkSimulator:
    def __init__(self, nodes=50, links=120, seed=42):
        if nodes < 2:
            raise ValueError("nodes must be at least 2")
        if links < nodes - 1 or links > nodes * (nodes - 1) // 2:
            raise ValueError("links must fit a simple connected graph")
        self.nodes, self.links, self.seed = nodes, links, seed
        self.random = random.Random(seed)
        self.edges = set()
        # Build a connected backbone first, then add reproducible random links.
        for node in range(1, nodes):
            parent = self.random.randrange(node)
            self.edges.add(tuple(sorted((node, parent))))
        while len(self.edges) < links:
            a, b = self.random.sample(range(nodes), 2)
            self.edges.add(tuple(sorted((a, b))))

    def graph(self):
        graph = {i: [] for i in range(self.nodes)}
        for a, b in self.edges:
            graph[a].append(b)
            graph[b].append(a)
        for neighbours in graph.values():
            neighbours.sort()
        return graph

    def shortest_hop_path(self, source, target):
        if not 0 <= source < self.nodes or not 0 <= target < self.nodes:
            raise ValueError("source and target must be valid node IDs")
        graph = self.graph()
        queue = deque([source])
        parent = {source: None}
        while queue:
            node = queue.popleft()
            if node == target:
                break
            for nxt in graph[node]:
                if nxt not in parent:
                    parent[nxt] = node
                    queue.append(nxt)
        if target not in parent:
            return None
        path, node = [], target
        while node is not None:
            path.append(node)
            node = parent[node]
        return path[::-1]

    def degree_statistics(self):
        degrees = [len(v) for v in self.graph().values()]
        return {
            "min_degree": min(degrees),
            "max_degree": max(degrees),
            "average_degree": round(statistics.mean(degrees), 3),
        }

    def benchmark(self, trials=1000):
        if trials < 1:
            raise ValueError("trials must be positive")
        hops = []
        for _ in range(trials):
            source, target = self.random.sample(range(self.nodes), 2)
            path = self.shortest_hop_path(source, target)
            if path:
                hops.append(len(path) - 1)
        return {
            "nodes": self.nodes,
            "links": self.links,
            "trials": trials,
            "reachable": len(hops),
            "average_hops": round(statistics.mean(hops), 3),
            "max_hops": max(hops),
            **self.degree_statistics(),
        }


if __name__ == "__main__":
    simulator = NetworkSimulator()
    print(simulator.benchmark())
    print("0 -> 25:", simulator.shortest_hop_path(0, 25))
