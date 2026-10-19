import random
import unittest

from algokit import binary_search, linear_search, two_sum


class RandomizedAlgoKitTests(unittest.TestCase):
    def test_searches_agree_with_reference(self):
        rng = random.Random(20261019)
        for _ in range(100):
            values = sorted(rng.randint(-20, 20) for _ in range(rng.randint(0, 40)))
            for target in range(-22, 23):
                expected = linear_search(values, target)
                actual = binary_search(values, target)
                if expected == -1:
                    self.assertEqual(actual, -1)
                else:
                    self.assertNotEqual(actual, -1)
                    self.assertEqual(values[actual], target)

    def test_two_sum_result_is_valid(self):
        rng = random.Random(77)
        for _ in range(150):
            values = [rng.randint(-15, 15) for _ in range(rng.randint(0, 30))]
            target = rng.randint(-20, 20)
            result = two_sum(values, target)
            valid_pairs = [
                (i, j)
                for i in range(len(values))
                for j in range(i + 1, len(values))
                if values[i] + values[j] == target
            ]
            if not valid_pairs:
                self.assertIsNone(result)
            else:
                self.assertIsNotNone(result)
                i, j = result
                self.assertLess(i, j)
                self.assertEqual(values[i] + values[j], target)


if __name__ == "__main__":
    unittest.main()
