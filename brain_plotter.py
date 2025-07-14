import collections
import csv
import time
from collections import deque
from datetime import datetime

import matplotlib.pyplot as plt
import numpy as np
try:
    import serial
except ImportError:
    # Mock the serial module if it is not available
    class Serial:
        def __init__(self, port, baudrate):
            pass
        def write(self, data):
            pass
        def close(self):
            pass
    serial = type("serial", (), {"Serial": Serial, "SerialException": type("SerialException", (Exception,), {})})()

from brain_control.bt_manager import BtManager

# Constants
FOCUS_THRESHOLD = 1.15
FOCUS_SCOPE = 0.2
SAVE_FILE_NAME = datetime.now().strftime("%d__%H-%M-%S") + ".csv"

# Global variables
points = collections.deque(maxlen=100)
write_threshold = 0

try:
    from pynput.mouse import Button, Controller
except ImportError:
    # Mock the Controller and Button classes if pynput is not available
    class Controller:
        def click(self, button):
            pass
    class Button:
        left = "left"

def check_focus_threshold(vals):
    """
    Checks if the focus threshold has been met.
    """
    full_range = list(vals)
    focus_range_len = int(len(full_range) * FOCUS_SCOPE)
    focus_range = full_range[:focus_range_len]

    if np.mean(focus_range) > np.mean(full_range) * FOCUS_THRESHOLD:
        print("Focus detected!")
        # Simulate a mouse click
        mouse = Controller()
        mouse.click(Button.left)

        # Send a command to the Arduino
        try:
            ser = serial.Serial("COM4", 9600)
            ser.write(b"ON")
            ser.close()
        except serial.SerialException as e:
            print(f"Error sending command to Arduino: {e}")
        return True
    return False

def append_to_file(path, txt):
    """
    Appends text to a file.
    """
    with open(path, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(txt)

def main():
    """
    Main function.
    """
    # Create a BtManager object
    bt_manager = BtManager("COM10")

    # Add a data parsed handler
    bt_manager.add_data_parsed_handler(lambda sender, e: {
        points.append(e.raw_value),
        plt.clf(),
        plt.plot(points),
        plt.draw(),
        plt.pause(0.001),

        # Check focus threshold
        check_focus_threshold(points),

        # Write to CSV
        append_to_file(SAVE_FILE_NAME, points)
    })

    # Start the BtManager
    bt_manager.start()

    # Show the plot
    plt.show()

    # Stop the BtManager
    bt_manager.stop()

if __name__ == "__main__":
    main()
