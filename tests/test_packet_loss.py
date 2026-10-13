import unittest
from network_tools.packet_loss import packet_loss


class PacketLossTests(unittest.TestCase):
    def test_no_loss(self):
        self.assertEqual(packet_loss(10, 10), 0)

    def test_all_lost(self):
        self.assertEqual(packet_loss(10, 0), 100)

    def test_zero_sent(self):
        self.assertEqual(packet_loss(0, 0), 0)

    def test_invalid_counts(self):
        for sent, received in [(-1, 0), (3, 4), (3, -1)]:
            with self.subTest(sent=sent, received=received):
                with self.assertRaises(ValueError):
                    packet_loss(sent, received)


if __name__ == "__main__":
    unittest.main()
