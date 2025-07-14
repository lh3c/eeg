import serial
import threading
from collections import deque

class BtDataEventArgs:
    def __init__(self, raw_value):
        self.raw_value = raw_value

class BtManager:
    def __init__(self, com_port, baud_rate=9600):
        self.port = com_port
        self.baud_rate = baud_rate
        self.serial = None
        self.is_running = False
        self.data_parsed_handlers = []

        self.MAX_PACKET_LENGTH = 32
        self.EEG_POWER_BANDS = 8
        self.last_byte = 0
        self.in_packet = False
        self.fresh_packet = False
        self.packet_index = 0
        self.checksum_accumulator = 0
        self.packet_length = 0
        self.check_sum = 0
        self.eeg_power = [0] * self.EEG_POWER_BANDS
        self.packet_data = [0] * self.MAX_PACKET_LENGTH

        self.signal_quality = 200
        self.focus = 0
        self.meditation = 0

    def add_data_parsed_handler(self, handler):
        self.data_parsed_handlers.append(handler)

    def remove_data_parsed_handler(self, handler):
        self.data_parsed_handlers.remove(handler)

    def _on_data_parsed(self, e):
        for handler in self.data_parsed_handlers:
            handler(self, e)

    def start(self):
        self.serial = serial.Serial(self.port, self.baud_rate)
        self.is_running = True
        self.thread = threading.Thread(target=self._read_data)
        self.thread.start()

    def stop(self):
        self.is_running = False
        if self.thread.is_alive():
            self.thread.join()
        if self.serial.is_open:
            self.serial.close()

    def _read_data(self):
        while self.is_running:
            try:
                buffer = self.serial.read(self.serial.in_waiting or 1)
                for b in buffer:
                    self._parse_byte(b)
            except serial.SerialException as e:
                print(f"Serial error: {e}")
                self.is_running = False

    def _parse_byte(self, b):
        if self.in_packet:
            if self.packet_index == 0:
                self.packet_length = b
                if self.packet_length > self.MAX_PACKET_LENGTH:
                    self.in_packet = False
            elif self.packet_index <= self.packet_length:
                self.packet_data[self.packet_index - 1] = b
                self.checksum_accumulator += b
            elif self.packet_index > self.packet_length:
                self.check_sum = b
                self.checksum_accumulator = 255 - self.checksum_accumulator
                if self.check_sum == self.checksum_accumulator:
                    if self._parse_packet():
                        self.fresh_packet = True
                    else:
                        print("ERROR: PARSING PACKET FAILED")
                else:
                    # print("ERROR: CHECKSUM")
                    pass
                self.in_packet = False
            self.packet_index += 1

        if b == 170 and self.last_byte == 170 and not self.in_packet:
            self.in_packet = True
            self.packet_index = 0
            self.checksum_accumulator = 0

        self.last_byte = b

        if self.fresh_packet:
            self.fresh_packet = False

    def _parse_packet(self):
        parse_success = True
        raw_value = 0
        i = 0
        self._clear_eeg_power()

        while i < self.packet_length:
            packet = self.packet_data[i]
            if packet == 0x2:
                i += 1
                self.signal_quality = self.packet_data[i]
            elif packet == 0x4:
                i += 1
                self.focus = self.packet_data[i]
            elif packet == 0x5:
                i += 1
                self.meditation = self.packet_data[i]
            elif packet == 0x83:
                i += 1
                for j in range(self.EEG_POWER_BANDS):
                    if i + 2 < len(self.packet_data):
                        self.eeg_power[j] = (self.packet_data[i] << 16) | (self.packet_data[i + 1] << 8) | self.packet_data[i + 2]
                        i += 3
            elif packet == 0x80:
                i += 1
                if i + 1 < len(self.packet_data):
                    raw_value = (self.packet_data[i] << 8) | self.packet_data[i + 1]
                    i += 1
            else:
                parse_success = False
            i += 1

        if parse_success:
            self._on_data_parsed(BtDataEventArgs(raw_value=raw_value))

        return parse_success

    def _clear_eeg_power(self):
        self.eeg_power = [0] * self.EEG_POWER_BANDS

    def print_values(self):
        print(f"Focus: {self.focus}")
        print(f"Meditation: {self.meditation}")
        print(f"Signal: {self.signal_quality}")
