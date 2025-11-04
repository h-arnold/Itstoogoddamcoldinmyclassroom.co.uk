================================================================================
Classroom Temperature Tracker - Setup Instructions
================================================================================

WHAT IS THIS?

This package helps teachers monitor classroom temperature using a BBC micro:bit
and upload data to a secure web dashboard (powered by Anvil).

The micro:bit reads temperature every 30 seconds, and the host script calculates
a 20-minute average and posts it to your online dashboard.

================================================================================
REQUIREMENTS
================================================================================

- Python 3.7 or higher installed on your computer
  (Check: open terminal/command prompt and type: python3 --version)
  
- BBC micro:bit with temperature reading code flashed
  (See microbit/README.md for setup instructions)
  
- USB cable to connect micro:bit to computer

- Active internet connection

- Anvil account with API key
  (Sign up at https://anvil.works and create your temperature tracking app)

================================================================================
QUICK START GUIDE
================================================================================

STEP 1: SETUP YOUR MICRO:BIT
-----------------------------
1. Flash the MicroPython code to your micro:bit (see microbit/README.md)
2. Connect micro:bit to your computer via USB
3. Note the serial port name (see "Finding Serial Port" below)

STEP 2: CONFIGURE THE HOST SCRIPT
----------------------------------
1. Open config.txt in a text editor (Notepad, TextEdit, nano, etc.)

2. Fill in the REQUIRED settings:
   
   API_KEY = [Your API key from Anvil Settings page]
   ROOM_NAME = [Name for this classroom, e.g., "Room_B12" or "Physics_Lab"]
   ANVIL_ENDPOINT = [Your Anvil app URL, e.g., https://your-app.anvil.app/_/api/log_temp]

3. OPTIONAL settings:
   
   SERIAL_PORT = [Leave blank for auto-detection, or specify manually]
   TEMP_OFFSET = -2.5  [Adjust if calibration needed]
   INTERVAL_SECONDS = 1200  [20 minutes default]

4. Save the file

STEP 3: RUN THE SCRIPT
-----------------------
Open a terminal/command prompt in this folder and run:

   python3 host_script.py

Or on Windows:

   python host_script.py

The script will:
- Connect to your micro:bit
- Read temperature every 30 seconds
- Calculate 20-minute average
- Post to your Anvil dashboard
- Log all activity to classroom-temp.log

Press Ctrl+C to stop the script.

================================================================================
FINDING YOUR SERIAL PORT
================================================================================

LINUX:
------
Run: ls /dev/tty*
Look for: /dev/ttyACM0 or /dev/ttyUSB0

You may need to add your user to the dialout group:
   sudo usermod -a -G dialout $USER
Then log out and back in.

MACOS:
------
Run: ls /dev/cu.*
Look for: /dev/cu.usbmodem14201 or similar

WINDOWS:
--------
1. Open Device Manager
2. Look under "Ports (COM & LPT)"
3. Find "USB Serial Device (COMX)" where X is a number
4. Use COMX in your config (e.g., COM3)

================================================================================
RUNNING AS A BACKGROUND SERVICE (Optional)
================================================================================

To have the script run automatically when your computer starts:

LINUX (systemd):
----------------
See USAGE.md in the repository for detailed systemd setup instructions.

MACOS (launchd):
----------------
See USAGE.md in the repository for detailed launchd setup instructions.

WINDOWS (Task Scheduler):
--------------------------
1. Open Task Scheduler
2. Create Basic Task
3. Trigger: "When the computer starts"
4. Action: "Start a program"
5. Program: python3 (or path to python)
6. Arguments: host_script.py
7. Start in: [path to this folder]

================================================================================
TROUBLESHOOTING
================================================================================

ERROR: "Could not open serial port"
-------------------------------------
- Check micro:bit is connected via USB
- Verify serial port name in config.txt is correct
- On Linux: ensure you're in the dialout group
- Try unplugging and reconnecting the micro:bit

ERROR: "API_KEY not configured"
--------------------------------
- Edit config.txt and replace "your_api_key_here" with your actual API key
- Make sure there are no extra spaces
- Save the file

ERROR: "Failed to post to Anvil"
---------------------------------
- Check your internet connection
- Verify ANVIL_ENDPOINT URL is correct
- Confirm API_KEY is valid in your Anvil app settings
- Check if firewall is blocking outgoing connections

NO TEMPERATURE READINGS:
-------------------------
- Verify micro:bit has the temperature code flashed
- Connect with a serial monitor to check output (see microbit/README.md)
- Ensure baud rate is 115200 in both micro:bit code and config
- Try pressing the reset button on the micro:bit

TEMPERATURE SEEMS INCORRECT:
-----------------------------
- Remember: processor temp is 2-3°C higher than ambient
- Adjust TEMP_OFFSET in config.txt for calibration
- Compare with a reference thermometer
- Wait a few minutes after connecting for stabilization

================================================================================
FILES IN THIS PACKAGE
================================================================================

host_script.py           - Main Python script
config.txt               - Configuration file (EDIT THIS!)
README.txt               - This file
microbit/                - Micro:bit MicroPython code and setup guide
vendor/                  - Required Python libraries (pre-installed)
  - serial/              - PySerial for USB communication
  - requests/            - HTTP client for Anvil API
  - urllib3/, certifi/, idna/, charset_normalizer/ - Dependencies

GENERATED FILES (created automatically):
classroom-temp.log       - Activity log
pending_uploads.json     - Cached data if internet connection fails

================================================================================
FEATURES
================================================================================

✓ Automatic micro:bit detection (by USB VID/PID)
✓ 20-minute rolling average with min/max tracking
✓ Calibration support (TEMP_OFFSET)
✓ Retry logic with exponential backoff
✓ Local caching if internet connection fails
✓ Automatic reconnection if micro:bit disconnects
✓ Anomaly detection (temperatures outside 5-35°C are flagged)
✓ Comprehensive logging
✓ Pure Python - no compiled modules

================================================================================
SUPPORT
================================================================================

For issues, questions, or contributions:
GitHub: https://github.com/h-arnold/Itstoogoddamcoldinmyclassroom.co.uk

For Anvil-specific questions:
Anvil Documentation: https://anvil.works/docs

================================================================================
LICENSE
================================================================================

MIT License - See repository for details

================================================================================
VERSION INFORMATION
================================================================================

This is part of the itstoodamncoldinmyclassroom.co.uk project.
Check the repository for the latest version and updates.
