"""I implemented breadth-first shortest-path reconstruction."""
from collections import deque

def shortest_path(graph, source, target):
    queue, parent = deque([source]), {source: None}
    while queue:
        node = queue.popleft()
        if node == target: break
        for neighbour in graph.get(node, []):
            if neighbour not in parent: parent[neighbour] = node; queue.append(neighbour)
    if target not in parent: return []
    path=[]
    while target is not None: path.append(target); target=parent[target]
    return path[::-1]

if __name__ == '__main__': print(shortest_path({'A':['B'],'B':['C'],'C':[]}, 'A', 'C'))