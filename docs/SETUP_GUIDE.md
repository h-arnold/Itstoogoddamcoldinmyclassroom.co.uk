# Teacher Setup Guide

## Complete Setup Instructions for Classroom Temperature Monitoring

This guide will help you set up temperature monitoring in your classroom using a BBC micro:bit.

---

## Requirements

Before you begin, make sure you have:

- ✅ BBC micro:bit (any version)
- ✅ USB cable (data transfer capable, not just power)
- ✅ Computer with Python 3.7 or higher installed
- ✅ Internet connection (for initial setup and data upload)
- ✅ Your API key from the website (get this from Settings page after creating an account)

---

## Step 1: Install Python (if not already installed)

### Windows

1. Download Python from [python.org/downloads](https://www.python.org/downloads/)
2. Run the installer
3. **Important**: Check "Add Python to PATH" during installation
4. Open Command Prompt and verify: `python --version`

### macOS

1. Download Python from [python.org/downloads](https://www.python.org/downloads/)
2. Run the installer
3. Open Terminal and verify: `python3 --version`

### Linux

Most Linux distributions come with Python pre-installed. Verify with:

```bash
python3 --version
```

If not installed:

```bash
sudo apt update
sudo apt install python3 python3-pip
```

---

## Step 2: Flash the micro:bit

### Option A: Using MakeCode Web Editor (Recommended)

1. Go to [makecode.microbit.org](https://makecode.microbit.org/)
2. Create a new project
3. Switch to Python mode (click "JavaScript" and select "Python")
4. Delete any existing code
5. Copy the code from `microbit/main.py` in this repository
6. Click "Download" to save the `.hex` file
7. Connect your micro:bit via USB
8. Drag and drop the `.hex` file onto the MICROBIT drive
9. The micro:bit will flash and restart automatically

### Option B: Using Thonny (Alternative)

1. Install Thonny from [thonny.org](https://thonny.org/)
2. Connect your micro:bit via USB
3. In Thonny: Tools > Options > Interpreter
4. Select "MicroPython (BBC micro:bit)"
5. Open `microbit/main.py`
6. Click "Run" (F5)

---

## Step 3: Download and Extract the Host Script

### Option A: Download Pre-built Package (Recommended)

1. Go to the [GitHub Actions](https://github.com/h-arnold/Itstoogoddamcoldinmyclassroom.co.uk/actions) page
2. Click on the latest successful build (green checkmark)
3. Scroll down to "Artifacts"
4. Download `microbit-temp-monitor.zip`
5. Extract to your Desktop or Documents folder

### Option B: Build from Source

If you're comfortable with git:

```bash
git clone https://github.com/h-arnold/Itstoogoddamcoldinmyclassroom.co.uk.git
cd Itstoogoddamcoldinmyclassroom.co.uk
python3 vendor_dependencies.py
python3 build.py
```

---

## Step 4: Configure the Host Script

1. Open the extracted folder
2. Find `config.txt` and open it in a text editor
3. Fill in the required values:

```ini
[Settings]
# Get this from the website Settings page after creating an account
API_KEY = your_api_key_here

# Choose a unique name for your classroom (e.g., "Room_B12" or "Physics_Lab")
ROOM_NAME = your_room_name

# This URL is provided when you create your account
ANVIL_ENDPOINT = https://your-app.anvil.app/_/api/log_temp

# Leave blank for automatic detection, or specify manually:
# Windows: COM3, COM4, etc.
# Linux: /dev/ttyACM0
# macOS: /dev/cu.usbmodem14201
SERIAL_PORT = 

# Calibration offset (processor temp is typically 2-3°C higher than ambient)
TEMP_OFFSET = -2.5

# Reading interval (default: 1200 seconds = 20 minutes)
INTERVAL_SECONDS = 1200
```

4. Save the file

---

## Step 5: Run the Host Script

### Windows

**Option 1**: Create a startup script

1. Create a new file called `run.bat` in the same folder
2. Add this content:
   ```batch
   @echo off
   python host_script.py
   pause
   ```
3. Double-click `run.bat` to start monitoring

**Option 2**: Use Command Prompt

1. Open Command Prompt
2. Navigate to the folder: `cd C:\path\to\folder`
3. Run: `python host_script.py`

### macOS / Linux

1. Open Terminal
2. Navigate to the folder: `cd ~/Desktop/microbit-temp-monitor`
3. Run: `python3 host_script.py`

**Optional**: Make it executable

```bash
chmod +x host_script.py
./host_script.py
```

---

## Step 6: Verify It's Working

After starting the script, check the following:

1. **Console output**: You should see messages like:
   ```
   Successfully connected to micro:bit on /dev/ttyACM0
   Reading temperature...
   ```

2. **Log file**: Check `classroom-temp.log` for detailed information:
   ```
   2025-11-04 14:30:00 - Successfully logged temperature: 19.5°C
   ```

3. **Website**: Log in to your account and check the dashboard
   - Your room should appear in the list
   - Data should start appearing after the first 20-minute cycle

---

## Troubleshooting

### "Serial port not found"

**Solution**: 
- Check USB connection
- Try a different USB cable (must support data, not just power)
- Manually specify `SERIAL_PORT` in `config.txt`
- **Linux only**: Add your user to the `dialout` group:
  ```bash
  sudo usermod -a -G dialout $USER
  ```
  Then log out and log back in

### "401 Unauthorized"

**Solution**:
- Verify your API key is correct (copy it again from the website)
- Make sure there are no extra spaces in `config.txt`
- Check that you're using the correct `ANVIL_ENDPOINT`

### "Connection refused" or "Network error"

**Solution**:
- Check your internet connection
- Verify the Anvil endpoint URL is correct
- Check if a firewall is blocking Python
- Add Python to your firewall exceptions if needed

### Readings seem incorrect

**Solution**:
- The micro:bit reports processor temperature (2-3°C higher than ambient)
- Adjust `TEMP_OFFSET` in `config.txt` after comparing with a reference thermometer
- Wait for the micro:bit to stabilize (first reading after boot is discarded)

### Script crashes or stops working

**Solution**:
- Check `classroom-temp.log` for error messages
- Ensure the micro:bit is connected and the code is flashed correctly
- Try restarting both the script and the micro:bit
- Check if pending_uploads.json is corrupted (delete it if necessary)

### Python not found (Windows)

**Solution**:
- Reinstall Python and check "Add Python to PATH"
- Or use the full path: `C:\Python39\python.exe host_script.py`

---

## Advanced Configuration

### Multiple Classrooms

To monitor multiple classrooms:

1. Create a separate folder for each classroom
2. Copy all files to each folder
3. Edit each `config.txt` with unique `ROOM_NAME` values
4. Run a separate script instance for each classroom

### Auto-start on Boot (Linux/macOS)

Create a systemd service or use cron:

```bash
@reboot cd /path/to/folder && python3 host_script.py >> /var/log/classroom-temp.log 2>&1
```

### Auto-start on Boot (Windows)

1. Create a shortcut to `run.bat`
2. Press Win+R, type `shell:startup`, press Enter
3. Move the shortcut to the Startup folder

---

## Data and Privacy

- Temperature data is stored for 90 days by default
- You can delete your account and all data at any time
- API keys can be revoked from the Settings page
- Share links can be set to expire or revoked at any time

---

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review `classroom-temp.log` for error messages
3. Open an issue on [GitHub](https://github.com/h-arnold/Itstoogoddamcoldinmyclassroom.co.uk/issues)
4. Contact support via the website

---

## Tips for Best Results

- Keep the micro:bit away from heat sources (radiators, computers, windows)
- Place it at student desk height for accurate classroom temperature
- USB power from a computer works fine (no need for battery)
- The script will retry failed uploads automatically
- Check the log file weekly to ensure everything is working

---

## Maintenance

- **Weekly**: Check the log file and website dashboard
- **Monthly**: Verify calibration with a reference thermometer
- **Termly**: Review data and adjust placement if needed
- **Yearly**: Update to the latest version from GitHub

---

## Next Steps

Once setup is complete:

1. Monitor the dashboard for the first few days
2. Compare readings with a reference thermometer and adjust `TEMP_OFFSET` if needed
3. Create share links to display data on classroom screens
4. Export CSV data for analysis
5. Set up additional classrooms if desired

---

**Congratulations!** Your classroom temperature monitoring is now active. The system will automatically log data every 20 minutes and upload it to your dashboard.
