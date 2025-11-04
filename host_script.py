#!/usr/bin/env python3
"""
Host script for reading micro:bit temperature data via serial and posting to Anvil.

Reads temperature every 30 seconds, averages over 20 minutes, and POSTs to Anvil HTTP endpoint.
"""

import time
import sys
from datetime import datetime, timezone
from collections import deque

try:
    import serial
    import requests
except ImportError as e:
    print(f"Error: Missing required dependency: {e}")
    print("Please ensure pyserial and requests are available.")
    sys.exit(1)


def load_config(config_path="config.txt"):
    """Load configuration from config file."""
    config = {}
    try:
        with open(config_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        config[key.strip()] = value.strip()
    except FileNotFoundError:
        print(f"Error: Configuration file '{config_path}' not found.")
        sys.exit(1)
    
    return config


def read_temperature(ser):
    """Read temperature from micro:bit serial connection."""
    try:
        # Read a line from serial
        line = ser.readline().decode('utf-8').strip()
        if line:
            # Try to parse as float
            try:
                temp = float(line)
                return temp
            except ValueError:
                print(f"Warning: Could not parse temperature value: {line}")
                return None
    except Exception as e:
        print(f"Error reading from serial: {e}")
        return None
    
    return None


def post_to_anvil(api_key, endpoint, average_temp):
    """POST average temperature to Anvil HTTP endpoint."""
    try:
        headers = {
            'Content-Type': 'application/json',
        }
        payload = {
            'api_key': api_key,
            'temperature': average_temp,
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        response = requests.post(endpoint, json=payload, headers=headers, timeout=10)
        response.raise_for_status()
        
        print(f"Successfully posted temperature {average_temp}°C to Anvil")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"Error posting to Anvil: {e}")
        return False


def main():
    """Main function to run the temperature monitoring loop."""
    # Load configuration
    config = load_config()
    
    # Required configuration
    api_key = config.get('API_KEY')
    serial_port = config.get('SERIAL_PORT', '/dev/ttyACM0')
    
    try:
        baud_rate = int(config.get('BAUD_RATE', '115200'))
    except ValueError:
        print(f"Error: Invalid BAUD_RATE in config.txt. Must be a number.")
        sys.exit(1)
    
    anvil_endpoint = config.get('ANVIL_ENDPOINT')
    
    if not api_key:
        print("Error: API_KEY not configured in config.txt")
        sys.exit(1)
    
    if not anvil_endpoint:
        print("Error: ANVIL_ENDPOINT not configured in config.txt")
        sys.exit(1)
    
    print(f"Starting temperature monitoring...")
    print(f"Serial port: {serial_port}")
    print(f"Baud rate: {baud_rate}")
    print(f"Anvil endpoint: {anvil_endpoint}")
    
    # Open serial connection
    try:
        ser = serial.Serial(serial_port, baud_rate, timeout=1)
        print(f"Connected to {serial_port}")
    except serial.SerialException as e:
        print(f"Error: Could not open serial port {serial_port}: {e}")
        sys.exit(1)
    
    # Temperature readings buffer (20 minutes = 40 readings at 30s intervals)
    readings_buffer = deque(maxlen=40)
    
    last_post_time = time.time()
    post_interval = 20 * 60  # 20 minutes in seconds
    
    try:
        while True:
            # Read temperature
            temp = read_temperature(ser)
            
            if temp is not None:
                readings_buffer.append(temp)
                print(f"Temperature reading: {temp}°C (buffer size: {len(readings_buffer)})")
            
            # Check if it's time to post
            current_time = time.time()
            if current_time - last_post_time >= post_interval and readings_buffer:
                # Calculate average
                average_temp = sum(readings_buffer) / len(readings_buffer)
                print(f"Average temperature over {len(readings_buffer)} readings: {average_temp:.2f}°C")
                
                # Post to Anvil
                if post_to_anvil(api_key, anvil_endpoint, average_temp):
                    last_post_time = current_time
                    # Clear buffer after successful post
                    readings_buffer.clear()
            
            # Wait 30 seconds before next reading
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\nStopping temperature monitoring...")
    finally:
        ser.close()
        print("Serial connection closed.")


if __name__ == '__main__':
    main()
