import unittest

from network_tools.network_math import bits_per_second, packet_loss_percent


class NetworkMathTests(unittest.TestCase):
    def test_packet_loss_percent(self):
        self.assertAlmostEqual(packet_loss_percent(100, 97), 3.0)

    def test_zero_sent_packets(self):
        self.assertEqual(packet_loss_percent(0, 0), 0.0)

    def test_throughput(self):
        self.assertEqual(bits_per_second(1_000_000, 2), 4_000_000)

    def test_invalid_packet_counts(self):
        with self.assertRaises(ValueError):
            packet_loss_percent(10, 11)


if __name__ == "__main__":
    unittest.main()
