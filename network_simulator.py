#!/usr/bin/env python3
"""Reproducible graph-based network topology and routing simulator."""
from collections import deque
import random
import statistics

class NetworkSimulator:
    def __init__(self,nodes=50,links=120,seed=42):
        if nodes<2 or links<nodes-1 or links>nodes*(nodes-1)//2: raise ValueError("invalid graph size")
        self.nodes,self.links,self.seed=nodes,links,seed; self.random=random.Random(seed); self.edges=set()
        for node in range(1,nodes): self.edges.add(tuple(sorted((node,self.random.randrange(node)))))
        while len(self.edges)<links: self.edges.add(tuple(sorted(self.random.sample(range(nodes),2))))
    def graph(self):
        g={i:[] for i in range(self.nodes)}
        for a,b in self.edges: g[a].append(b); g[b].append(a)
        for n in g.values(): n.sort()
        return g
    def shortest_hop_path(self,source,target):
        if not 0<=source<self.nodes or not 0<=target<self.nodes: raise ValueError("invalid node")
        g=self.graph(); q=deque([source]); parent={source:None}
        while q:
            node=q.popleft()
            if node==target: break
            for nxt in g[node]:
                if nxt not in parent: parent[nxt]=node; q.append(nxt)
        if target not in parent: return None
        path=[]; node=target
        while node is not None: path.append(node); node=parent[node]
        return path[::-1]
    def degree_statistics(self):
        degrees=[len(v) for v in self.graph().values()]
        return {"min_degree":min(degrees),"max_degree":max(degrees),"average_degree":round(statistics.mean(degrees),3)}
    def benchmark(self,trials=1000):
        if trials<1: raise ValueError("trials must be positive")
        hops=[len(path)-1 for _ in range(trials) for path in [self.shortest_hop_path(*self.random.sample(range(self.nodes),2))] if path]
        return {"nodes":self.nodes,"links":self.links,"trials":trials,"reachable":len(hops),"average_hops":round(statistics.mean(hops),3),"max_hops":max(hops),**self.degree_statistics()}
    def route_summary(self,source=0):
        g=self.graph(); reachable={source}; q=deque([source])
        while q:
            node=q.popleft()
            for nxt in g[node]:
                if nxt not in reachable: reachable.add(nxt); q.append(nxt)
        return {"source":source,"reachable_nodes":len(reachable),"unreachable_nodes":self.nodes-len(reachable),"connectivity":len(reachable)==self.nodes}

if __name__=="__main__":
    simulator=NetworkSimulator()
    print(simulator.benchmark())
    print(simulator.route_summary())
    print("0 -> 25:",simulator.shortest_hop_path(0,25))
