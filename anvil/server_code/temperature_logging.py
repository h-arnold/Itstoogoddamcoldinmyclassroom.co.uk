"""
Anvil Server Module: HTTP Endpoint for Temperature Data Logging

This module handles incoming temperature data from host scripts via HTTP POST.
"""

import anvil.server
import anvil.users
import anvil.tables as tables
from anvil.tables import app_tables
from datetime import datetime, timedelta
import json

# In-memory cache for rate limiting (API key -> last submission timestamp)
_rate_limit_cache = {}


@anvil.server.http_endpoint('/api/log_temp', methods=['POST'])
def log_temperature():
    """
    HTTP Endpoint: POST /_/api/log_temp
    
    Receives JSON payloads from the host applet and logs temperature data.
    
    Request Format:
    {
      "api_key": "key_abc123...",
      "room_name": "Room_B12",
      "temperature": 18.5,
      "temp_min": 17.8,
      "temp_max": 19.2,
      "timestamp": "2025-11-04T14:30:00Z"  # Optional
    }
    
    Returns:
    - 200 OK: {"status": "success", "reading_id": "..."}
    - 400 Bad Request: Missing required fields or invalid data format
    - 401 Unauthorized: Invalid or missing API key
    - 422 Unprocessable Entity: Temperature outside acceptable range
    - 429 Too Many Requests: Rate limit exceeded
    - 500 Internal Server Error: Database or server error
    """
    try:
        # Parse request body
        request_data = json.loads(anvil.server.request.body_json)
        
        # Extract required fields
        api_key = request_data.get('api_key')
        room_name = request_data.get('room_name')
        temperature = request_data.get('temperature')
        temp_min = request_data.get('temp_min')
        temp_max = request_data.get('temp_max')
        timestamp_str = request_data.get('timestamp')
        
        # Validate required fields
        if not api_key:
            return anvil.server.HttpResponse(
                status=401,
                body=json.dumps({"error": "Missing API key"}),
                headers={"Content-Type": "application/json"}
            )
        
        if not room_name or temperature is None:
            return anvil.server.HttpResponse(
                status=400,
                body=json.dumps({"error": "Missing required fields: room_name, temperature"}),
                headers={"Content-Type": "application/json"}
            )
        
        # Authenticate API key
        api_key_row = app_tables.apikeys.get(key=api_key)
        if not api_key_row:
            return anvil.server.HttpResponse(
                status=401,
                body=json.dumps({"error": "Invalid API key"}),
                headers={"Content-Type": "application/json"}
            )
        
        # Rate limiting: Max 1 submission per 19 minutes
        now = datetime.now()
        last_submission = _rate_limit_cache.get(api_key)
        if last_submission and (now - last_submission).total_seconds() < 19 * 60:
            return anvil.server.HttpResponse(
                status=429,
                body=json.dumps({"error": "Rate limit exceeded. Max 1 submission per 19 minutes."}),
                headers={"Content-Type": "application/json"}
            )
        
        # Update last_used timestamp on API key
        api_key_row['last_used'] = now
        
        # Validate temperature range (5°C to 35°C)
        is_anomaly = False
        if temperature < 5 or temperature > 35:
            is_anomaly = True
        
        # Parse or generate timestamp
        if timestamp_str:
            try:
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                # Validate timestamp is not in future or >7 days in past
                if timestamp > now:
                    timestamp = now
                elif (now - timestamp).days > 7:
                    timestamp = now
            except ValueError:
                timestamp = now
        else:
            timestamp = now
        
        # Get or create room
        user = api_key_row['owner']
        room = app_tables.rooms.get(owner=user, name=room_name)
        if not room:
            room = app_tables.rooms.add_row(
                owner=user,
                name=room_name,
                created=now
            )
        
        # Log reading
        reading = app_tables.readings.add_row(
            room=room,
            timestamp=timestamp,
            temperature=temperature,
            temp_min=temp_min if temp_min is not None else temperature,
            temp_max=temp_max if temp_max is not None else temperature,
            is_anomaly=is_anomaly
        )
        
        # Update rate limit cache
        _rate_limit_cache[api_key] = now
        
        # Return success
        return anvil.server.HttpResponse(
            status=200,
            body=json.dumps({
                "status": "success",
                "reading_id": reading.get_id()
            }),
            headers={"Content-Type": "application/json"}
        )
        
    except json.JSONDecodeError:
        return anvil.server.HttpResponse(
            status=400,
            body=json.dumps({"error": "Invalid JSON format"}),
            headers={"Content-Type": "application/json"}
        )
    except Exception as e:
        print(f"Error in log_temperature: {e}")
        return anvil.server.HttpResponse(
            status=500,
            body=json.dumps({"error": "Internal server error"}),
            headers={"Content-Type": "application/json"}
        )
