import unittest

from retry import retry


class RetryTests(unittest.TestCase):
    def test_succeeds_after_retry(self):
        calls = []
        def operation():
            calls.append(1)
            if len(calls) < 3:
                raise ValueError("temporary")
            return "ok"
        delays = []
        result = retry(operation, attempts=3, initial_delay=0.1, sleep=delays.append,
                       retry_on=(ValueError,))
        self.assertEqual(result, "ok")
        self.assertEqual(len(calls), 3)
        self.assertEqual(delays, [0.1, 0.2])

    def test_invalid_attempts(self):
        with self.assertRaises(ValueError):
            retry(lambda: 1, attempts=0)


if __name__ == "__main__":
    unittest.main()
