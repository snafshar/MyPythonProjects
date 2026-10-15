import unittest

from dict_merge import merge_settings


class MergeSettingsTests(unittest.TestCase):
    def test_override_wins_without_mutating_inputs(self):
        defaults = {"theme": "light", "timeout": 10}
        overrides = {"theme": "dark"}
        result = merge_settings(defaults, overrides)
        self.assertEqual(result, {"theme": "dark", "timeout": 10})
        self.assertEqual(defaults["theme"], "light")

    def test_empty_inputs(self):
        self.assertEqual(merge_settings({}, {}), {})


if __name__ == "__main__":
    unittest.main()
