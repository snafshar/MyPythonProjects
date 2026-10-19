import unittest

from graph_algorithms import bfs_shortest_path, dijkstra


class GraphAlgorithmsTests(unittest.TestCase):
    def test_bfs_shortest_path(self):
        graph = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
        self.assertEqual(bfs_shortest_path(graph, "A", "D"), ["A", "B", "D"])
        self.assertEqual(bfs_shortest_path(graph, "D", "D"), ["D"])
        self.assertIsNone(bfs_shortest_path(graph, "A", "Z"))

    def test_dijkstra(self):
        graph = {
            "A": [("B", 4), ("C", 1)],
            "C": [("B", 2), ("D", 5)],
            "B": [("D", 1)],
            "D": [],
        }
        self.assertEqual(dijkstra(graph, "A"), {"A": 0, "C": 1, "B": 3, "D": 4})

    def test_negative_weight_rejected(self):
        with self.assertRaises(ValueError):
            dijkstra({"A": [("B", -1)]}, "A")


if __name__ == "__main__":
    unittest.main()
