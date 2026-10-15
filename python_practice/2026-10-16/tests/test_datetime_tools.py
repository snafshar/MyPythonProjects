import unittest
from datetime import timezone
from datetime_tools import parse_timestamp, to_utc_iso

class DateTimeToolsTests(unittest.TestCase):
    def test_z_suffix(self):
        self.assertEqual(parse_timestamp("2026-10-15T12:00:00Z").utcoffset().total_seconds(), 0)

    def test_naive_timestamp_policy(self):
        self.assertEqual(parse_timestamp("2026-10-15T12:00:00").tzinfo, timezone.utc)

    def test_offset_conversion(self):
        self.assertEqual(to_utc_iso("2026-10-15T14:00:00+02:00"), "2026-10-15T12:00:00+00:00")

if __name__ == "__main__":
    unittest.main()
