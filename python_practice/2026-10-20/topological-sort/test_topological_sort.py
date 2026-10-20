import unittest

from topological_sort import topological_sort


class TopologicalSortTests(unittest.TestCase):
    def test_order_respects_edges(self):
        graph = {"build": ["test"], "lint": ["test"], "test": ["release"], "docs": []}
        order = topological_sort(graph)
        position = {name: index for index, name in enumerate(order)}
        for source, targets in graph.items():
            for target in targets:
                self.assertLess(position[source], position[target])

    def test_empty_graph(self):
        self.assertEqual(topological_sort({}), [])

    def test_neighbor_not_listed_as_key_is_included(self):
        self.assertEqual(topological_sort({"start": ["end"]}), ["start", "end"])

    def test_cycle_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "cycle"):
            topological_sort({"a": ["b"], "b": ["a"]})

    def test_self_loop_is_rejected(self):
        with self.assertRaises(ValueError):
            topological_sort({"a": ["a"]})


if __name__ == "__main__":
    unittest.main()
