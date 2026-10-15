import unittest
from datetime import timezone

from datetime_tools import parse_timestamp, to_utc_iso


class DateTimeToolsTests(unittest.TestCase):
    def test_z_suffix(self):
        value = parse_timestamp("2026-10-15T12:00:00Z")
        self.assertEqual(value.utcoffset().total_seconds(), 0)

    def test_naive_policy_is_utc(self):
        value = parse_timestamp("2026-10-15T12:00:00")
        self.assertEqual(value.tzinfo, timezone.utc)

    def test_offset_conversion(self):
        self.assertEqual(to_utc_iso("2026-10-15T14:00:00+02:00"),
                         "2026-10-15T12:00:00+00:00")


if __name__ == "__main__":
    unittest.main()
