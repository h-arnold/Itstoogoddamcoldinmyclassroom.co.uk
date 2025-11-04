# Micro:bit Temperature Sensor Setup

This directory contains the MicroPython code to run on your BBC micro:bit.

## What it does

The micro:bit code:
1. Initializes the UART (serial) connection at 115200 baud
2. Discards the first temperature reading (to avoid warm-up bias)
3. Continuously reads the processor temperature every 30 seconds
4. Outputs readings in the format `temp:XX` via USB serial

## Important Notes

- The temperature reading is from the micro:bit's processor, not an external sensor
- Processor temperature is typically **2-3°C higher** than ambient temperature
- This is acceptable for tracking temperature trends over time
- The host script can apply a calibration offset (TEMP_OFFSET in config.txt)

## How to Flash the Code

### Option 1: Using Thonny (Recommended)

1. Download and install [Thonny](https://thonny.org/)
2. Connect your micro:bit via USB
3. In Thonny, select the micro:bit interpreter (View → Interpreter → BBC micro:bit)
4. Open `main.py` from this directory
5. Click the "Run" button to flash the code to the micro:bit
6. The code will run automatically and persist across power cycles

### Option 2: Using MakeCode Web Editor

The MicroPython code above can be adapted for MakeCode:

1. Go to [https://makecode.microbit.org/](https://makecode.microbit.org/)
2. Create a new project
3. Switch to JavaScript mode
4. Replace the code with this equivalent:

```javascript
serial.setBaudRate(BaudRate.BaudRate115200)

// Discard initial reading
input.temperature()
basic.pause(5000)

basic.forever(function () {
    serial.writeLine("temp:" + input.temperature())
    basic.pause(30000)
})
```

5. Download the .hex file and copy it to your micro:bit

## Verifying the Setup

After flashing, you can verify the micro:bit is sending data:

**Linux/macOS:**
```bash
# Install screen if not available
sudo apt-get install screen  # Linux
# or brew install screen      # macOS

# Connect to serial port (adjust port as needed)
screen /dev/ttyACM0 115200

# You should see output like:
# temp:21
# temp:22
# temp:21
```

**Windows:**
Use PuTTY or the Arduino Serial Monitor to connect to the COM port at 115200 baud.

Press `Ctrl+A` then `K` to exit screen.

## Troubleshooting

### No output visible
- Ensure the micro:bit LED display shows it's running (should be blank if code is correct)
- Check USB connection is secure
- Try unplugging and reconnecting the micro:bit
- Verify baud rate is set to 115200 in both the code and your serial monitor

### Temperature seems wrong
- Remember: processor temp is 2-3°C higher than ambient
- The first reading is discarded to stabilize
- Use TEMP_OFFSET in config.txt to calibrate the readings

### Code not persisting
- Make sure you saved the code as `main.py` (not just ran it temporarily)
- Some editors require explicit "Flash to device" action

## Technical Details

- **IDE**: Thonny or MakeCode Web Editor
- **Language**: MicroPython (or JavaScript for MakeCode)
- **Baud Rate**: 115200
- **Reading Interval**: 30 seconds
- **Output Format**: `temp:XX` where XX is temperature in Celsius
- **Temperature Source**: micro:bit processor (ARM Cortex-M0)
