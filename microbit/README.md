# BBC micro:bit Temperature Sensor Code

## Overview

This MicroPython script runs on the BBC micro:bit and reads the processor temperature every 30 seconds, outputting it via the USB serial port.

## Features

- Reads processor temperature (typically 2-3°C higher than ambient)
- Outputs temperature readings in format: `temp:XX`
- Baud rate: 115200
- Reading interval: 30 seconds
- Discards first reading after boot to avoid warm-up bias

## Installation Instructions

### Using MakeCode Web Editor

1. Go to [MakeCode for micro:bit](https://makecode.microbit.org/)
2. Create a new project
3. Switch to Python mode (click "JavaScript" and select "Python")
4. Delete the default code
5. Copy and paste the contents of `main.py`
6. Click "Download" to save the `.hex` file
7. Connect your micro:bit via USB
8. Drag and drop the `.hex` file onto the micro:bit drive

### Using Thonny

1. Install [Thonny](https://thonny.org/)
2. Connect your micro:bit via USB
3. In Thonny, go to Tools > Options > Interpreter
4. Select "MicroPython (BBC micro:bit)" as the interpreter
5. Open `main.py` in Thonny
6. Click the "Run" button or press F5
7. The code will be transferred to the micro:bit

### Using mu Editor

1. Install [mu editor](https://codewith.mu/)
2. Connect your micro:bit via USB
3. Select "BBC micro:bit" mode
4. Open `main.py`
5. Click "Flash" to transfer the code to the micro:bit

## Verification

After flashing:

1. The micro:bit should start immediately
2. Connect to the serial port at 115200 baud
3. You should see output like:
   ```
   temp:21
   temp:22
   temp:21
   ```

## Temperature Calibration

The micro:bit reports processor temperature, which is typically 2-3°C higher than ambient temperature. The host script applies a calibration offset (default: -2.5°C) to compensate for this. You can adjust this offset in the host script's `config.txt` file.

## Troubleshooting

- **No output**: Check that the micro:bit is powered and the USB cable supports data transfer (not just power)
- **Incorrect values**: This is expected - calibration is handled by the host script
- **Connection issues**: Try a different USB cable or port
- **Permission denied (Linux)**: Add your user to the `dialout` group: `sudo usermod -a -G dialout $USER`

## Technical Details

- **Temperature source**: Processor temperature sensor
- **Accuracy**: Suitable for trend monitoring, not precise measurements
- **Baud rate**: 115200 (matches host script configuration)
- **Protocol**: Simple text format over USB serial
- **Power**: USB powered (no battery required for continuous monitoring)
