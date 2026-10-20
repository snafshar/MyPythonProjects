# Graph Representations

| Representation | Space | Useful for |
|---|---:|---|
| Adjacency list | (O(V+E)) | Sparse graphs and neighbor iteration |
| Adjacency matrix | (O(V^2)) | Dense graphs and constant-time edge lookup |
| Edge list | (O(E)) | Input storage and edge-centric algorithms |

For an undirected graph, each edge normally appears in both endpoint lists. Decide whether self-loops and parallel edges are allowed, and document whether weights are stored with neighbors. Representation choices affect the complexity of traversal and updates.
