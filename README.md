# Itstoogoddamcoldinmyclassroom.co.uk

Micro:bit Temperature Monitoring System - A Python host script that reads temperature data from a micro:bit via serial connection and posts it to an Anvil HTTP endpoint.

## Overview

This system continuously monitors classroom temperature using a micro:bit:
- Reads temperature every 30 seconds from micro:bit via serial
- Calculates 20-minute rolling average
- Posts data to Anvil HTTP endpoint with API key authentication
- Pure Python implementation (no compiled modules)
- Self-contained ZIP distribution

## Repository Structure

```
.
├── host_script.py           # Main monitoring script
├── config.txt               # Configuration template
├── vendor/                  # Vendored pure Python dependencies
│   ├── serial/              # pyserial
│   ├── requests/            # requests library
│   └── ...                  # Other dependencies
├── build.py                 # Builds distributable ZIP
├── vendor_dependencies.py   # Downloads and vendors dependencies
├── requirements.txt         # Python dependencies
└── .github/workflows/
    └── build.yml            # CI/CD validation and build
```

## Quick Start

### Option 1: Download Pre-built ZIP (Recommended)

1. Go to [Actions](../../actions) tab
2. Click on the latest successful build
3. Download `microbit-temp-monitor` artifact
4. Extract and skip to [Configuration](#configuration)

### Option 2: Build from Source

```bash
# Clone repository
git clone https://github.com/h-arnold/Itstoogoddamcoldinmyclassroom.co.uk.git
cd Itstoogoddamcoldinmyclassroom.co.uk

# Vendor dependencies
python3 vendor_dependencies.py

# Build distributable
python3 build.py
```

## Configuration

1. Edit `config.txt`:
   ```ini
   API_KEY=your_actual_api_key_here
   ANVIL_ENDPOINT=https://your-app.anvil.app/_/api/your-endpoint
   SERIAL_PORT=/dev/ttyACM0  # Adjust for your system
   BAUD_RATE=115200
   ```

2. Determine your serial port:
   - **Linux**: Usually `/dev/ttyACM0` or `/dev/ttyUSB0`
   - **macOS**: Usually `/dev/cu.usbmodem*`
   - **Windows**: Usually `COM3`, `COM4`, etc.

## Running

```bash
python3 host_script.py
```

The script will:
1. Connect to micro:bit via serial
2. Read temperature every 30 seconds
3. Calculate 20-minute average (40 readings)
4. POST to Anvil endpoint every 20 minutes
5. Clear buffer after successful post

Press `Ctrl+C` to stop.

## Micro:bit Setup

Your micro:bit should be programmed to output temperature readings via serial. Example MicroPython code:

```python
from microbit import *

while True:
    temp = temperature()
    print(temp)
    sleep(1000)  # 1 second
```

## Dependencies

All dependencies are vendored as pure Python:
- **pyserial** (3.5): Serial communication
- **requests** (2.32.3): HTTP client
- **charset-normalizer** (3.3.2): Character encoding (pure Python fallback)
- **idna** (3.7): Domain name support
- **urllib3** (2.2.2): HTTP library
- **certifi** (2024.7.4): SSL certificates

## GitHub Actions CI/CD

The build workflow (`.github/workflows/build.yml`) automatically:
1. ✅ Vendors dependencies
2. ✅ Removes any compiled modules (.so, .pyd)
3. ✅ Validates no compiled modules remain (build fails if any found)
4. ✅ Creates self-contained ZIP
5. ✅ Uploads as downloadable artifact

## Requirements

- Python 3.7 or higher
- USB connection to micro:bit
- Internet connection (for posting to Anvil)

## License

MIT License - See LICENSE file for details

## Support

For issues or questions, please open an issue on GitHub.