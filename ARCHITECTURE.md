# Architecture and Design

## System Overview

This project implements a temperature monitoring system that reads data from a micro:bit and posts it to an Anvil web service.

## Components

### 1. Host Script (`host_script.py`)

The main monitoring script with these responsibilities:

- **Configuration Management**: Loads settings from `config.txt`
- **Serial Communication**: Reads temperature from micro:bit via pyserial
- **Data Collection**: Maintains a 20-minute rolling buffer (40 readings at 30s intervals)
- **Data Aggregation**: Calculates average temperature
- **HTTP Client**: POSTs data to Anvil endpoint using requests library

**Key Design Decisions:**
- Uses `deque` with `maxlen=40` for efficient rolling buffer
- Non-blocking serial reads with 1-second timeout
- Graceful error handling for network and serial issues
- Clean shutdown on Ctrl+C

### 2. Configuration (`config.txt`)

Template configuration file with:
- `API_KEY`: Authentication for Anvil endpoint
- `ANVIL_ENDPOINT`: Target URL for data submission  
- `SERIAL_PORT`: Device path for micro:bit connection
- `BAUD_RATE`: Serial communication speed (default: 115200)

### 3. Vendored Dependencies (`vendor/`)

Pure Python libraries bundled with the distribution:

- **pyserial**: Serial port communication
- **requests**: HTTP client with auth and timeout support
- **charset-normalizer**: Character encoding (pure Python fallback)
- **idna**: Internationalized domain names
- **urllib3**: HTTP connection pooling
- **certifi**: SSL/TLS certificate bundle

**Why vendored?**
- Self-contained deployment (no pip install needed)
- Version pinning for reproducibility
- Works on systems without internet access
- Eliminates dependency conflicts

### 4. Build System

**`vendor_dependencies.py`**: Downloads and prepares dependencies
- Installs packages to vendor/ directory
- Removes compiled modules (.so, .pyd)
- Cleans test directories and cache files

**`build.py`**: Creates distributable ZIP
- Validates no compiled modules present
- Bundles host_script.py, config.txt, vendor/
- Creates timestamped ZIP file
- Fails build if validation fails

### 5. CI/CD Pipeline (`.github/workflows/build.yml`)

GitHub Actions workflow that:
1. Sets up Python 3.7 environment
2. Installs dependencies to vendor/
3. Removes compiled modules
4. **Validates no compiled modules remain** (fails if any found)
5. Builds ZIP bundle
6. Uploads as downloadable artifact
7. Shows bundle contents

**Critical Feature**: Build fails if ANY compiled modules are detected, ensuring pure Python distribution.

## Data Flow

```
Micro:bit → Serial → host_script.py → Buffer (40 readings) → Average → HTTP POST → Anvil
   (30s)              (pyserial)         (20 minutes)                  (requests)
```

## Timing

- Reading interval: 30 seconds
- Buffer size: 40 readings (20 minutes)
- POST interval: 20 minutes
- Serial timeout: 1 second

## Error Handling

- **Missing config**: Exit with error message
- **Serial connection failed**: Exit with error  
- **Temperature parse error**: Skip reading, continue
- **HTTP POST failed**: Log error, retry next cycle
- **Keyboard interrupt**: Clean shutdown, close serial

## Platform Compatibility

**Supported:**
- Python 3.7+ on Linux, macOS, Windows
- Any system with USB serial support

**Serial Port Names:**
- Linux: `/dev/ttyACM0`, `/dev/ttyUSB0`
- macOS: `/dev/cu.usbmodem*`
- Windows: `COM3`, `COM4`, etc.

## Security

- API key stored in local config file (not in repo)
- HTTPS communication with SSL certificate validation
- No hardcoded credentials
- Config template has placeholder values

## Testing Strategy

Multiple test scripts validate:
1. Compiled module detection works
2. Build validation catches violations
3. GitHub Action workflow logic
4. Configuration parsing
5. Python syntax validation

## Distribution

Users can:
1. Download pre-built ZIP from GitHub Actions artifacts
2. Build from source using `build.py`
3. Customize and rebuild as needed

All distributions are validated to contain only pure Python code.
