# BtManager Class Documentation

The `BtManager` class is responsible for managing the connection to the brainwave sensor and parsing the data received from it.

## Data Parsing

The `parsePacket` method is the core of the data parsing logic. It iterates through the packet data and extracts the values for signal quality, focus, meditation, and EEG power bands.

### EEG Power Values

The EEG power values are 24-bit values that are constructed from three bytes. The C# code uses the following logic to parse the EEG power values:

```csharp
for (int j = 0; j < EEG_POWER_BANDS; j++)
    eegPower[j] = ((uint)packetData[++i] << 16) | ((uint)packetData[++i] << 8) | packetData[++i];
```

This code is equivalent to the following Python code:

```python
for j in range(EEG_POWER_BANDS):
    i += 1
    eeg_power[j] = (packet_data[i] << 16) | (packet_data[i + 1] << 8) | packet_data[i + 2]
    i += 2
```

This is because the `++i` in the C# code is a pre-increment operator, which means that the value of `i` is incremented *before* it is used. In Python, we can achieve the same result by incrementing `i` before we use it in the array index.

## Focus Actions

The `checkFocusThreshold` method checks if the focus threshold has been met. If it has, it can perform two actions:

*   **Simulate a mouse click:** This is done using the `pynput` library.
*   **Send a command to an Arduino:** This is done using the `pyserial` library.

### Mocking pynput

To test the `checkFocusThreshold` method without a display server, you can mock the `pynput` library. This can be done by creating a mock `Controller` and `Button` class in your test file:

```python
class MockController:
    def click(self, button):
        pass

class MockButton:
    left = "left"

with patch('brain_plotter.Controller', MockController):
    with patch('brain_plotter.Button', MockButton):
        # Your test code here
```
