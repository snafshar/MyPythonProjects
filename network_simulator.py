#!/usr/bin/env python3
"""Reproducible graph-based network topology and routing simulator."""

from collections import deque
import random
import statistics


class NetworkSimulator:
    def __init__(self, nodes=50, links=120, seed=42):
        self.nodes = nodes
        self.links = links
        self.random = random.Random(seed)
        self.edges = set()
        while len(self.edges) < links:
            a, b = self.random.sample(range(nodes), 2)
            self.edges.add(tuple(sorted((a, b))))

    def graph(self):
        graph = {i: [] for i in range(self.nodes)}
        for a, b in self.edges:
            graph[a].append(b)
            graph[b].append(a)
        return graph

    def shortest_hop_path(self, source, target):
        graph = self.graph()
        queue = deque([(source, [source])])
        seen = {source}
        while queue:
            node, path = queue.popleft()
            if node == target:
                return path
            for nxt in graph[node]:
                if nxt not in seen:
                    seen.add(nxt)
                    queue.append((nxt, path + [nxt]))
        return None

    def benchmark(self, trials=1000):
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
            "average_hops": round(statistics.mean(hops), 3) if hops else None,
            "max_hops": max(hops) if hops else None,
        }


if __name__ == "__main__":
    print(NetworkSimulator().benchmark())
