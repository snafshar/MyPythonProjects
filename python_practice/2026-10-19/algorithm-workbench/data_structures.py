"""Disjoint-set union (union-find) with path compression and union by size."""


class DisjointSet:
    def __init__(self, items=()):
        self.parent = {item: item for item in items}
        self.size = {item: 1 for item in items}

    def add(self, item):
        if item not in self.parent:
            self.parent[item] = item
            self.size[item] = 1

    def find(self, item):
        if item not in self.parent:
            raise KeyError(item)
        root = item
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[item] != item:
            parent = self.parent[item]
            self.parent[item] = root
            item = parent
        return root

    def union(self, first, second):
        """Join two sets; return True if the sets were different."""
        self.add(first)
        self.add(second)
        root_a, root_b = self.find(first), self.find(second)
        if root_a == root_b:
            return False
        if self.size[root_a] < self.size[root_b]:
            root_a, root_b = root_b, root_a
        self.parent[root_b] = root_a
        self.size[root_a] += self.size[root_b]
        return True

    def connected(self, first, second):
        return self.find(first) == self.find(second)
