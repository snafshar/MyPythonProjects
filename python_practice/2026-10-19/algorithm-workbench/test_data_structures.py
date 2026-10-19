import unittest

from data_structures import DisjointSet


class DisjointSetTests(unittest.TestCase):
    def test_union_and_connectivity(self):
        groups = DisjointSet([1, 2, 3, 4])
        self.assertTrue(groups.union(1, 2))
        self.assertTrue(groups.union(3, 4))
        self.assertTrue(groups.union(2, 3))
        self.assertTrue(groups.connected(1, 4))
        self.assertFalse(groups.union(1, 4))

    def test_unknown_item_is_added_by_union(self):
        groups = DisjointSet()
        groups.union("alpha", "beta")
        self.assertTrue(groups.connected("alpha", "beta"))

    def test_find_unknown_item_raises(self):
        with self.assertRaises(KeyError):
            DisjointSet().find("missing")


if __name__ == "__main__":
    unittest.main()
