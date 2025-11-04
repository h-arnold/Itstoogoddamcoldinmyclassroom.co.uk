# Usage Examples

## Basic Usage

### 1. First Time Setup

```bash
# Extract the ZIP
unzip microbit_temp_monitor_*.zip
cd microbit_temp_monitor/

# Edit configuration
nano config.txt
# or
vi config.txt
# or use any text editor

# Update these values:
# - API_KEY=your_actual_api_key
# - ANVIL_ENDPOINT=https://your-app.anvil.app/_/api/endpoint
# - SERIAL_PORT=/dev/ttyACM0 (adjust for your system)
```

### 2. Find Your Serial Port

**Linux:**
```bash
# List all serial devices
ls -l /dev/tty*

# Or use dmesg to see connected devices
dmesg | grep tty

# Common: /dev/ttyACM0 or /dev/ttyUSB0
```

**macOS:**
```bash
ls /dev/cu.*

# Usually: /dev/cu.usbmodem14201 or similar
```

**Windows:**
```powershell
# Open Device Manager and look under "Ports (COM & LPT)"
# Usually: COM3, COM4, COM5, etc.
```

### 3. Run the Monitor

```bash
python3 host_script.py
```

Expected output:
```
Starting temperature monitoring...
Serial port: /dev/ttyACM0
Baud rate: 115200
Anvil endpoint: https://your-app.anvil.app/_/api/temp
Connected to /dev/ttyACM0
Temperature reading: 21.5°C (buffer size: 1)
Temperature reading: 22.0°C (buffer size: 2)
...
Temperature reading: 21.8°C (buffer size: 40)
Average temperature over 40 readings: 21.73°C
Successfully posted temperature 21.73°C to Anvil
```

### 4. Stop the Monitor

Press `Ctrl+C`:
```
^C
Stopping temperature monitoring...
Serial connection closed.
```

## Advanced Usage

### Running as a Background Service

**Linux (systemd):**

Create `/etc/systemd/system/microbit-temp.service`:
```ini
[Unit]
Description=Micro:bit Temperature Monitor
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/microbit_monitor
ExecStart=/usr/bin/python3 /home/pi/microbit_monitor/host_script.py
Restart=always
RestartSec=30

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable microbit-temp.service
sudo systemctl start microbit-temp.service

# Check status
sudo systemctl status microbit-temp.service

# View logs
sudo journalctl -u microbit-temp.service -f
```

**macOS (launchd):**

Create `~/Library/LaunchAgents/com.classroom.tempmonitor.plist`:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.classroom.tempmonitor</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/yourname/microbit_monitor/host_script.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/yourname/microbit_monitor</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

Load the service:
```bash
launchctl load ~/Library/LaunchAgents/com.classroom.tempmonitor.plist
```

### Custom Intervals

To modify timing, edit `host_script.py`:

```python
# Line 124: Change sleep interval (default: 30 seconds)
time.sleep(30)  # Change to desired seconds

# Line 105: Change buffer size (default: 40 readings = 20 minutes at 30s)
readings_buffer = deque(maxlen=40)  # maxlen = (minutes * 60) / sleep_interval

# Line 107: Change POST interval (default: 20 minutes)
post_interval = 20 * 60  # Change to desired seconds
```

### Logging to File

Redirect output to a log file:
```bash
python3 host_script.py >> temp_monitor.log 2>&1
```

With automatic log rotation:
```bash
python3 host_script.py 2>&1 | rotatelogs temp_monitor-%Y%m%d.log 86400
```

### Multiple micro:bits

Run multiple instances with different configs:
```bash
# Terminal 1
python3 host_script.py  # Uses config.txt

# Terminal 2  
python3 host_script.py --config config2.txt  # If you modify script to accept args
```

## Troubleshooting

### "Could not open serial port"

**Problem:** Permission denied or device not found

**Solution:**
```bash
# Linux: Add user to dialout group
sudo usermod -a -G dialout $USER
# Log out and back in

# Check port exists
ls -l /dev/ttyACM0

# Test with screen
screen /dev/ttyACM0 115200
```

### "Error: API_KEY not configured"

**Problem:** config.txt not edited

**Solution:**
```bash
# Edit config.txt and replace YOUR_API_KEY_HERE with actual key
nano config.txt
```

### "Error posting to Anvil"

**Problem:** Network issue or wrong endpoint

**Solution:**
```bash
# Test endpoint manually
curl -X POST https://your-app.anvil.app/_/api/test \
  -H "Content-Type: application/json" \
  -d '{"api_key": "test", "temperature": 20.5}'
```

### No temperature readings

**Problem:** micro:bit not sending data

**Solution:**
1. Check micro:bit is running the temperature program
2. Test with serial monitor: `screen /dev/ttyACM0 115200`
3. Verify micro:bit is printing temperature values
4. Check baud rate matches (115200)

## micro:bit Program Examples

### MicroPython

```python
from microbit import *

while True:
    temp = temperature()
    print(temp)
    sleep(1000)
```

### MakeCode (JavaScript)

```javascript
basic.forever(function () {
    serial.writeLine("" + input.temperature())
    basic.pause(1000)
})
```

## Development

### Rebuilding from Source

```bash
# Clone repo
git clone https://github.com/h-arnold/Itstoogoddamcoldinmyclassroom.co.uk.git
cd Itstoogoddamcoldinmyclassroom.co.uk

# Vendor dependencies
python3 vendor_dependencies.py

# Build ZIP
python3 build.py

# Result: microbit_temp_monitor_YYYYMMDD_HHMMSS.zip
```

### Testing Changes

```bash
# Validate syntax
python3 -m py_compile host_script.py

# Test config loading
python3 -c "from host_script import load_config; print(load_config())"

# Dry run (will fail without micro:bit, but tests config)
python3 host_script.py
```
