# Complete Technical Specification: itstoodamncoldinmyclassroom.co.uk (Updated)

## 1. Project Overview and Goals

| Item | Detail |
|------|--------|
| Name | itstoodamncoldinmyclassroom.co.uk |
| Objective | Provide teachers with a reliable, shareable platform to track and visualise classroom temperatures using a BBC micro:bit. |
| Platform | Anvil (Web App, Database, API Endpoints) |
| Host Code | Python 3, distributed as a portable, vendored ZIP file. |
| Sensor | BBC micro:bit running MicroPython. |
| Key Metric | Processor temperature (proxy for ambient), logged every 20 minutes (average of 40 readings). |

---

## 2. Component 1: micro:bit (MicroPython Code)

**IDE**: Thonny or MakeCode Web Editor.

**Language**: MicroPython.

**Action**: Reads the internal processor temperature and outputs it to the USB serial port every 30 seconds.

**Caveat**: The temperature is the processor temperature, typically 2–3 °C higher than ambient. This is acceptable for tracking trends. Users can calibrate using the host script configuration.

**Enhancement**: The first reading is discarded after boot to avoid bias from the initial warm-up.

### MicroPython Code (main.py)

```python
# main.py for the micro:bit
from microbit import *
import time

uart.init(baudrate=115200)

# Discard the initial reading to stabilise
_ = temperature()
time.sleep(5)

while True:
    temp = temperature()
    print(f"temp:{temp}")
    time.sleep(30)
```

---

## 3. Component 2: Host Computer Applet (Python Script) – Portable Distribution

This applet bridges the micro:bit serial output to the Anvil HTTP endpoint.

### 3.1. Distribution and Execution Strategy (Final)

**No pip install or .exe files allowed.**

**Strategy**: Vendoring and Bundling. All required libraries (pyserial, requests, urllib3, etc.) are included as pure Python source files in a self-contained ZIP.

**User Requirement**: The host machine must have Python 3.7+ installed.

**Configuration**: Settings are read from a local `config.txt` file, ensuring the main script remains untouched.

**Serial Port Detection**: Automatic detection by USB VID/PID (`0x0d28:0x0204` for BBC micro:bit). If multiple devices found, user must confirm selection. Falls back to manual `SERIAL_PORT` config if detection fails.

### 3.2. Script Logic (host_script.py)

**Libraries Used**: `serial` (vendored pyserial), `requests` (vendored), `time`, `threading`, `queue`, `statistics`, `configparser` (standard library), `json`, `tempfile`, `os`.

**Loop**:
1. Reads configuration from `config.txt` (validates all required fields present).
2. Detects micro:bit serial port automatically using VID/PID, or uses configured `SERIAL_PORT`.
3. Starts a background thread to continuously read the serial port, parse lines starting with `temp:`, and queue the temperature values.
4. The main thread sleeps for 20 minutes (1200 seconds).
5. Upon waking, calculates the average, minimum, and maximum temperature from all queued readings.
6. Applies `TEMP_OFFSET` calibration to the average.
7. The average, min, max, and metadata (API key, room name) are sent via a POST request to the Anvil HTTP endpoint.
8. The queue is cleared, and the process repeats.

**Resilience Enhancements**:
- Implements retry logic (up to 3 attempts with exponential backoff: 5s, 15s, 45s) if a POST request fails.
- If all attempts fail, readings are cached locally using atomic writes to `pending_uploads.json`.
- On next successful connection, pending uploads are resent and cleared.
- Atomic writes: Write to temporary file, then rename to prevent corruption.
- Recovery: If `pending_uploads.json` is malformed, logs error and starts fresh (doesn't crash).

**Error Handling**:
- **micro:bit disconnection**: Detects serial read timeout, logs warning, attempts reconnection every 30 seconds.
- **Serial buffer overflow**: Clears buffer on detection, logs warning.
- **Malformed config.txt**: Script exits with clear error message indicating which field is missing/invalid.
- **Endpoint offline >1 hour**: Continues caching locally (file size limited to last 100 readings to prevent disk overflow).
- **Invalid temperature readings**: Values outside 5°C to 35°C are logged as anomalies but still recorded with a flag.

**Logging**: All operations logged to `classroom-temp.log` with timestamps (rolling file, max 5MB).

### 3.3. Configuration File (config.txt)

```ini
[Settings]
# Required: Your Anvil API key from the Settings page
API_KEY = your_api_key_here

# Required: Room identifier (e.g., "Room_B12" or "Physics_Lab")
ROOM_NAME = your_room_name

# Required: Anvil HTTP endpoint URL
ANVIL_ENDPOINT = https://your-app.anvil.app/_/api/log_temp

# Optional: Serial port (leave blank for auto-detection)
# Windows: COM3, Linux: /dev/ttyACM0, macOS: /dev/cu.usbmodem14201
SERIAL_PORT = 

# Optional: Temperature offset for calibration (default: -2.5)
# Adjust based on comparison with reference thermometer
TEMP_OFFSET = -2.5

# Optional: Reading interval in seconds (default: 1200 for 20 minutes)
INTERVAL_SECONDS = 1200
```

### 3.4. GitHub Action for Bundling 🤖

| Step | Detail |
|------|--------|
| Trigger | Manual `workflow_dispatch` or tag push (e.g. v1.0.1). |
| Action | Uses `pip download --no-binary :all:` to fetch source distributions only (.tar.gz, .zip) for pyserial, requests, and transitive dependencies (urllib3, certifi, idna, charset-normalizer). |
| Vendoring | Extracts and moves the pure Python package folders into a staging directory (`classroom-temp-tracker/`). |
| Files | Copies `host_script.py` and template `config.txt` into the staging directory. |
| Validation | Runs `find . -type f \( -name "*.so" -o -name "*.pyd" -o -name "*.dylib" \)` to confirm no compiled modules. Fails build if any found. |
| Cleanup | Removes all `__pycache__`, `.pyc`, and test directories. |
| Artifact | The entire staging directory is zipped (`classroom-temp-tracker-vX.X.X.zip`) and uploaded as a GitHub Release asset with SHA256 checksum. |

### 3.5. Required Folder Structure (Final ZIP Content)

```
classroom-temp-tracker/
├── host_script.py
├── config.txt                 # User editable template
├── README.txt                 # Setup instructions
├── pending_uploads.json       # Created dynamically if uploads fail
├── classroom-temp.log         # Created dynamically for logging
├── serial/                    # Vendored pyserial
├── requests/                  # Vendored requests
├── urllib3/                   # Vendored urllib3
├── certifi/                   # Vendored certifi
├── idna/                      # Vendored idna
└── charset_normalizer/        # Vendored charset_normalizer
```

---

## 4. Component 3: Anvil Web Application

The complete server-side application (frontend, backend, database) is hosted on Anvil.

### 4.1. Anvil Data Model (Tables)

| Table | Fields | Description |
|-------|--------|-------------|
| Users | email, password_hash, created (DateTime) | Managed by the built-in Anvil Users service. |
| ApiKeys | owner (Link to Users), key (Text, Unique, Indexed), created (DateTime), last_used (DateTime) | Used for host applet authentication. |
| Rooms | owner (Link to Users), name (Text, Unique per user, Indexed), created (DateTime) | Represents a teacher's classroom. |
| Readings | room (Link to Rooms), timestamp (DateTime, Indexed, UTC), temperature (Number), temp_min (Number), temp_max (Number), is_anomaly (Boolean) | Stores the 20-minute data points with min/max values. |
| ShareLinks | room (Link to Rooms), token (Text, Unique UUID, Indexed), created (DateTime), expires (DateTime, Optional), view_count (Number) | Manages public access links with optional expiry. |

**Data Retention**: Readings older than 90 days are automatically deleted via a daily scheduled task (Anvil Background Task). Configurable per deployment.

### 4.2. Anvil Server Logic

#### A. HTTP Endpoint (Data Logging)

**Path**: `/_/api/log_temp` (POST)

**Purpose**: Receives JSON payloads from the host applet.

**Request Format**:
```json
{
  "api_key": "key_abc123...",
  "room_name": "Room_B12",
  "temperature": 18.5,
  "temp_min": 17.8,
  "temp_max": 19.2,
  "timestamp": "2025-11-04T14:30:00Z"
}
```

**Logic**:
1. Parse `api_key`, `room_name`, `temperature`, `temp_min`, `temp_max`, and optional `timestamp` from request body.
2. Authenticate via `ApiKeys`; return `401 Unauthorized` if invalid.
3. Update `last_used` timestamp on the API key.
4. Validate temperature as numeric within 5°C to 35°C (flag as anomaly if outside range, but still accept).
5. If `timestamp` provided, validate it's not in future or >7 days in past; otherwise use server time (UTC).
6. Identify or create the corresponding `Rooms` record for that user.
7. Log data in `Readings` table with UTC timestamp.
8. Return `200 OK` with `{"status": "success", "reading_id": "..."}`.

**Rate Limiting**:
- Per-API-key: Maximum 1 submission per 19 minutes (allows slight drift/retries).
- Implemented via in-memory cache of last submission time per key.
- Returns `429 Too Many Requests` if violated.

**Error Responses**:
- `400 Bad Request`: Missing required fields or invalid data format.
- `401 Unauthorized`: Invalid or missing API key.
- `422 Unprocessable Entity`: Temperature outside acceptable range (still logged as anomaly).
- `429 Too Many Requests`: Rate limit exceeded.
- `500 Internal Server Error`: Database or server error.

#### B. Callable Functions

| Function | Requirement | Action |
|----------|-------------|--------|
| `get_global_average()` | Public, cacheable | Calculates the average of all readings from the last 24 hours, excluding rooms with <3 readings. Cached for 5 minutes to reduce load. Returns `{"average": 19.2, "sample_count": 450, "room_count": 15}`. |
| `get_my_rooms()` | Requires Login | Returns all rooms linked to the current user with last reading timestamp. |
| `get_room_data(room, period)` | Requires Login | Fetches readings for a given room and time range (e.g., "24h", "7d", "30d") for plotting. Returns list of `{timestamp, temperature, temp_min, temp_max, is_anomaly}`. |
| `generate_api_key()` | Requires Login | Generates a new token (`key_` + 32 hex chars using `secrets` module) and stores it in `ApiKeys`. Returns the key (only time it's shown unmasked). |
| `revoke_api_key(key_row)` | Requires Login | Verifies ownership and deletes the specified `ApiKeys` record. |
| `create_share_link(room_row, expires_days=None)` | Requires Login | Generates a unique UUID4, stores it in `ShareLinks` with optional expiry (e.g., 7, 30, 365 days, or null for permanent). Returns full public URL (`https://app.url/#share=UUID`). |
| `revoke_share_link(link_row)` | Requires Login | Verifies ownership and deletes the specified `ShareLinks` record. |
| `get_public_share_data(token)` | Public | Returns the last 7 days of data and room name for the specified token. Increments `view_count`. Returns `None` if invalid or expired. |
| `export_room_data_csv(room, period)` | Requires Login | Generates CSV file of readings for download. Includes timestamp (local timezone), temperature, min, max, anomaly flag. |
| `check_version(client_version)` | Public | Compares client version string with latest release. Returns `{"update_available": true/false, "latest_version": "1.2.3"}`. |

**Optional Enhancements**:
- `get_ntp_time()`: Public function to return server's current UTC time for client clock verification.
- `get_room_statistics(room, period)`: Returns aggregated stats (mean, median, std dev, trend).

### 4.3. Anvil Pages and UI

| Page | Access | Components & Functionality |
|------|--------|---------------------------|
| Homepage | Public | Displays the global average prominently (with context: "Based on N classrooms"); includes Login/Signup. Detects `#share=UUID` in the URL and calls `get_public_share_data()` to render shared charts with "View Count: X" displayed. |
| Dashboard | Requires Login | Displays interactive Plotly charts with dropdowns for room and time range (24h, 7d, 30d). Shows average line with min/max shaded band. Anomalies marked in red. Includes buttons to generate/revoke share links and export CSV. Shows "Last reading: X minutes ago" status. |
| Settings | Requires Login | Panels for: (1) API key management (display masked keys with "Copy" button, last used timestamp, create, revoke); (2) Share link management (list active links with expiry dates, view counts, revoke buttons); (3) Data export (download all historical data as CSV). |
| Help/Setup | Public | Step-by-step guide with screenshots for: installing Python, flashing micro:bit, extracting ZIP, editing config.txt, running script (per OS). Includes troubleshooting section. |
| Error Handling | Public & Private | Clear alerts for missing data, invalid tokens, expired links, server errors, or anomalous readings. |
| Time Display | — | All timestamps displayed in the user's local timezone (auto-detected) but stored in UTC. Clearly labeled (e.g., "2025-11-04 14:30 GMT"). |

**Accessibility**:
- Semantic HTML with ARIA labels.
- Keyboard navigation support.
- Color-blind safe palette for charts.
- Screen reader tested (optional but recommended).

---

## 5. Distribution and Maintenance

### 5.1. Release Process
- GitHub Action automates packaging and ensures reproducible ZIP builds.
- Each release includes:
  - ZIP file with vendored dependencies
  - SHA256 checksum file
  - CHANGELOG.md with version notes
  - PDF setup guide for teachers

### 5.2. Version Management
- Semantic versioning (e.g., v1.2.3).
- Host script includes version constant checked against Anvil on startup (non-blocking warning if outdated).
- **Optional**: Auto-update notification in dashboard.

### 5.3. Multi-Instance Support
- Template `config.txt` provided with placeholders for `API_KEY`, `ROOM_NAME`, `ANVIL_ENDPOINT`, and `SERIAL_PORT`.
- Each instance operates independently, allowing multiple classrooms to run concurrently.
- **Optional**: Single host script can manage multiple micro:bits via extended config format (advanced users only).

### 5.4. Testing and Quality Assurance
- **Unit Tests**: Python script includes test mode using mock serial data.
- **Integration Tests**: Anvil test environment with dummy data.
- **End-to-End**: Documented procedure using real micro:bit and test API key.
- **Performance**: Load testing for 100 concurrent classrooms (expected: <500ms response time).

### 5.5. Teacher Setup Guide (README.txt)

Contents:
1. **Requirements**: Python 3.7+, BBC micro:bit, USB cable.
2. **Step 1**: Flash micro:bit with provided `main.py` (screenshots for MakeCode web editor).
3. **Step 2**: Install Python (links for Windows/Mac/Linux, verification with `python --version`).
4. **Step 3**: Extract ZIP to Desktop or Documents folder.
5. **Step 4**: Edit `config.txt` with API key from website Settings page and room name.
6. **Step 5**: Run script:
   - Windows: Double-click `run.bat` (creates a `.bat` launcher)
   - Mac/Linux: Open Terminal, `cd` to folder, run `python3 host_script.py`
7. **Verification**: Check `classroom-temp.log` for "Successfully logged temperature" message.
8. **Troubleshooting**:
   - "Serial port not found": Check USB connection, try manual `SERIAL_PORT` config
   - "401 Unauthorized": Verify API key copied correctly
   - "Permission denied" (Linux): Add user to `dialout` group
   - Firewall blocking: Whitelist Python or add exception

### 5.6. Monitoring and Support
- Dashboard shows "System Health" indicator (all rooms, last seen times).
- Email alerts for administrators if >10% of rooms offline >24 hours (optional).
- Public status page showing Anvil uptime (optional).

---

## 6. Security Considerations

1. **API Keys**: 
   - Generated with cryptographically secure randomness (`secrets` module).
   - Stored hashed in database (SHA256 with salt) - **wait, no**: stored plain for validation but never logged.
   - Transmitted over HTTPS only.
   - Rate limited to prevent brute force.

2. **Share Links**:
   - UUID4 provides 122 bits of entropy (infeasible to guess).
   - Optional expiry prevents indefinite access.
   - View counts allow monitoring for abuse.

3. **Data Privacy**:
   - Temperature data is non-personal but could identify patterns.
   - Users can delete accounts and all associated data (GDPR compliance).
   - No tracking or analytics beyond functional needs.

4. **Input Validation**:
   - All user inputs sanitized to prevent injection attacks.
   - Temperature values bounded to prevent nonsense data.

---

## 7. Known Limitations and Future Enhancements

### Current Limitations
1. 20-minute averaging may miss brief temperature events (documented).
2. Processor temperature offset varies slightly between micro:bit boards (calibration mitigates this).
3. Host script requires Python installation (not always available on school computers).
4. No mobile app (web interface is responsive but not native).

### Optional Future Enhancements
- **Real-time Dashboard**: WebSocket for live updates without refresh.
- **Alerts**: Email/SMS notifications when temperature drops below threshold.
- **Comparison View**: Overlay multiple rooms on single chart.
- **Historical Reports**: Automated weekly summary emails.
- **API for Integrations**: Allow third-party tools to access data.
- **Offline Mode**: Desktop app with local database syncing when online.
- **Multi-Sensor Support**: External temperature probes via I2C.

---

## 8. Deployment Checklist

### Pre-Launch
- [ ] Anvil app deployed to production environment
- [ ] Database tables created with indexes
- [ ] Background task scheduled for data retention
- [ ] Rate limiting configured and tested
- [ ] GitHub Action tested with release candidate
- [ ] Teacher setup guide reviewed by non-technical user
- [ ] End-to-end test with real hardware
- [ ] Load testing completed (100 concurrent users)
- [ ] Error handling verified (disconnect scenarios)
- [ ] Accessibility audit (keyboard navigation, screen reader)

### Launch
- [ ] Domain configured (itstoodamncoldinmyclassroom.co.uk)
- [ ] SSL certificate verified
- [ ] Initial user accounts created for pilot teachers
- [ ] Support email/forum established
- [ ] Announcement materials prepared

### Post-Launch
- [ ] Monitor error logs daily (first week)
- [ ] Collect user feedback via survey
- [ ] Performance metrics tracked (response times, uptime)
- [ ] Bug fixes prioritized and released
- [ ] Documentation updated based on common questions

---

## Document Version
**Version**: 2.0  
**Date**: 2025-11-04  
**Changes**: Incorporated critical fixes for temperature calibration, error handling, data retention, serial port detection, atomic file writes, share link expiry, CSV export, endpoint configuration, and comprehensive documentation.
