import unittest
from dict_merge import merge_settings

class MergeSettingsTests(unittest.TestCase):
    def test_overrides_win_without_mutating_defaults(self):
        defaults = {"theme": "light", "timeout": 10}
        result = merge_settings(defaults, {"theme": "dark"})
        self.assertEqual(result, {"theme": "dark", "timeout": 10})
        self.assertEqual(defaults["theme"], "light")

    def test_empty_inputs(self):
        self.assertEqual(merge_settings({}, {}), {})

if __name__ == "__main__":
    unittest.main()
