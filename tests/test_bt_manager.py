import unittest
from unittest.mock import Mock
from brain_control.bt_manager import BtManager

class TestBtManager(unittest.TestCase):
    def test_parse_packet(self):
        # Create a mock serial port
        mock_serial = Mock()

        # Create a BtManager instance with the mock serial port
        bt_manager = BtManager("COM10")
        bt_manager.serial = mock_serial

        # Test case 1: Focus and meditation
        bt_manager.packet_data = [0x04, 0x37, 0x05, 0x64]
        bt_manager.packet_length = 4
        bt_manager._parse_packet()
        self.assertEqual(bt_manager.focus, 0x37)
        self.assertEqual(bt_manager.meditation, 0x64)

        # Test case 2: Signal quality
        bt_manager.packet_data = [0x02, 0xC8]
        bt_manager.packet_length = 2
        bt_manager._parse_packet()
        self.assertEqual(bt_manager.signal_quality, 0xC8)

        # Test case 3: EEG power
        bt_manager.packet_data = [0x83, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F, 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17, 0x18]
        bt_manager.packet_length = 25
        bt_manager._parse_packet()
        self.assertEqual(bt_manager.eeg_power, [66051, 263430, 460809, 658188, 855567, 1052946, 1250325, 1447704])

        # Test case 4: Raw value
        bt_manager.packet_data = [0x80, 0x01, 0x02]
        bt_manager.packet_length = 3
        bt_manager._parse_packet()
        # The raw value is not stored in the BtManager instance, so we can't test it directly

if __name__ == "__main__":
    unittest.main()
