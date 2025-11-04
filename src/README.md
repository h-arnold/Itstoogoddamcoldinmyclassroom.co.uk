# Source Code

This directory contains the main host script and configuration template.

## Files

### host_script.py

The main Python script that:
- Connects to the micro:bit via serial port
- Reads temperature data every 30 seconds
- Calculates a 20-minute rolling average
- Posts data to the Anvil HTTP endpoint
- Handles errors and retries

**Dependencies**: All dependencies are vendored in the `vendor/` directory (no pip install required).

### config.txt

Configuration template with the following settings:

API_KEY = your_api_key_here
ROOM_NAME = your_room_name
ANVIL_ENDPOINT = https://your-app.anvil.app/_/api/log_temp
SERIAL_PORT = 
TEMP_OFFSET = -2.5
INTERVAL_SECONDS = 1200
```

**Note**: In the distributed ZIP, these files are placed at the root for easy access by users.

## Building

The `build.py` script (in the repository root) packages these files along with the vendored dependencies into a self-contained ZIP distribution.

## Development

To test changes during development:

```bash
# From the repository root
cd src
python3 host_script.py
```

Make sure to run `vendor_dependencies.py` first to populate the vendor directory.
