"""
Anvil Server Module: Callable Functions

This module provides server-side functions that can be called from the client.
"""

import anvil.server
import anvil.users
import anvil.tables as tables
from anvil.tables import app_tables
from datetime import datetime, timedelta
import secrets
import uuid
import csv
from io import StringIO

# Cache for global average (5 minute TTL)
_global_average_cache = {'data': None, 'timestamp': None}


@anvil.server.callable
def get_global_average():
    """
    Public, cacheable function.
    
    Calculates the average of all readings from the last 24 hours,
    excluding rooms with <3 readings. Cached for 5 minutes to reduce load.
    
    Returns:
        dict: {"average": 19.2, "sample_count": 450, "room_count": 15}
    """
    now = datetime.now()
    
    # Check cache
    if _global_average_cache['data'] and _global_average_cache['timestamp']:
        if (now - _global_average_cache['timestamp']).total_seconds() < 300:
            return _global_average_cache['data']
    
    # Calculate global average
    cutoff_time = now - timedelta(hours=24)
    recent_readings = app_tables.readings.search(
        tables.order_by('timestamp', ascending=False),
        timestamp=tables.greater_than(cutoff_time)
    )
    
    # Group by room
    room_readings = {}
    for reading in recent_readings:
        room_id = reading['room'].get_id()
        if room_id not in room_readings:
            room_readings[room_id] = []
        room_readings[room_id].append(reading['temperature'])
    
    # Filter rooms with <3 readings
    valid_rooms = {k: v for k, v in room_readings.items() if len(v) >= 3}
    
    # Calculate average
    all_temps = [temp for temps in valid_rooms.values() for temp in temps]
    
    if all_temps:
        result = {
            "average": round(sum(all_temps) / len(all_temps), 1),
            "sample_count": len(all_temps),
            "room_count": len(valid_rooms)
        }
    else:
        result = {
            "average": None,
            "sample_count": 0,
            "room_count": 0
        }
    
    # Update cache
    _global_average_cache['data'] = result
    _global_average_cache['timestamp'] = now
    
    return result


@anvil.server.callable
@anvil.users.require_login
def get_my_rooms():
    """
    Requires Login.
    
    Returns all rooms linked to the current user with last reading timestamp.
    
    Returns:
        list: [{"name": "Room_B12", "last_reading": datetime, ...}, ...]
    """
    user = anvil.users.get_user()
    rooms = app_tables.rooms.search(owner=user)
    
    result = []
    for room in rooms:
        # Get last reading
        last_reading = app_tables.readings.get(
            room=room,
            tables.order_by('timestamp', ascending=False)
        )
        
        result.append({
            "row": room,
            "name": room['name'],
            "created": room['created'],
            "last_reading": last_reading['timestamp'] if last_reading else None
        })
    
    return result


@anvil.server.callable
@anvil.users.require_login
def get_room_data(room, period):
    """
    Requires Login.
    
    Fetches readings for a given room and time range for plotting.
    
    Args:
        room: Room row object
        period: Time range ("24h", "7d", "30d")
    
    Returns:
        list: [{timestamp, temperature, temp_min, temp_max, is_anomaly}, ...]
    """
    user = anvil.users.get_user()
    
    # Verify ownership
    if room['owner'] != user:
        raise Exception("Unauthorized access to room data")
    
    # Parse period
    period_map = {
        "24h": timedelta(hours=24),
        "7d": timedelta(days=7),
        "30d": timedelta(days=30)
    }
    
    if period not in period_map:
        raise ValueError(f"Invalid period: {period}")
    
    cutoff_time = datetime.now() - period_map[period]
    
    # Fetch readings
    readings = app_tables.readings.search(
        tables.order_by('timestamp', ascending=True),
        room=room,
        timestamp=tables.greater_than(cutoff_time)
    )
    
    result = []
    for reading in readings:
        result.append({
            "timestamp": reading['timestamp'],
            "temperature": reading['temperature'],
            "temp_min": reading['temp_min'],
            "temp_max": reading['temp_max'],
            "is_anomaly": reading['is_anomaly']
        })
    
    return result


@anvil.server.callable
@anvil.users.require_login
def generate_api_key():
    """
    Requires Login.
    
    Generates a new API key token and stores it in ApiKeys table.
    
    Returns:
        str: The generated API key (only time it's shown unmasked)
    """
    user = anvil.users.get_user()
    
    # Generate secure random key
    key = "key_" + secrets.token_hex(32)
    
    # Store in database
    app_tables.apikeys.add_row(
        owner=user,
        key=key,
        created=datetime.now(),
        last_used=None
    )
    
    return key


@anvil.server.callable
@anvil.users.require_login
def revoke_api_key(key_row):
    """
    Requires Login.
    
    Verifies ownership and deletes the specified ApiKeys record.
    
    Args:
        key_row: ApiKeys row object to delete
    """
    user = anvil.users.get_user()
    
    # Verify ownership
    if key_row['owner'] != user:
        raise Exception("Unauthorized: Cannot revoke another user's API key")
    
    key_row.delete()


@anvil.server.callable
@anvil.users.require_login
def create_share_link(room_row, expires_days=None):
    """
    Requires Login.
    
    Generates a unique UUID token and creates a share link.
    
    Args:
        room_row: Room row object
        expires_days: Optional expiry (7, 30, 365, or None for permanent)
    
    Returns:
        str: Full public URL (e.g., "https://app.url/#share=UUID")
    """
    user = anvil.users.get_user()
    
    # Verify ownership
    if room_row['owner'] != user:
        raise Exception("Unauthorized: Cannot create share link for another user's room")
    
    # Generate UUID token
    token = str(uuid.uuid4())
    
    # Calculate expiry
    expires = None
    if expires_days:
        expires = datetime.now() + timedelta(days=expires_days)
    
    # Store in database
    app_tables.sharelinks.add_row(
        room=room_row,
        token=token,
        created=datetime.now(),
        expires=expires,
        view_count=0
    )
    
    # Return URL (adjust domain as needed)
    return f"https://itstoodamncoldinmyclassroom.co.uk/#share={token}"


@anvil.server.callable
@anvil.users.require_login
def revoke_share_link(link_row):
    """
    Requires Login.
    
    Verifies ownership and deletes the specified ShareLinks record.
    
    Args:
        link_row: ShareLinks row object to delete
    """
    user = anvil.users.get_user()
    
    # Verify ownership
    if link_row['room']['owner'] != user:
        raise Exception("Unauthorized: Cannot revoke another user's share link")
    
    link_row.delete()


@anvil.server.callable
def get_public_share_data(token):
    """
    Public function.
    
    Returns the last 7 days of data and room name for the specified token.
    Increments view_count.
    
    Args:
        token: UUID token string
    
    Returns:
        dict or None: {"room_name": "Room_B12", "data": [...], "view_count": 5}
    """
    # Find share link
    link = app_tables.sharelinks.get(token=token)
    
    if not link:
        return None
    
    # Check expiry
    if link['expires'] and link['expires'] < datetime.now():
        return None
    
    # Increment view count
    link['view_count'] = (link['view_count'] or 0) + 1
    
    # Get last 7 days of data
    cutoff_time = datetime.now() - timedelta(days=7)
    readings = app_tables.readings.search(
        tables.order_by('timestamp', ascending=True),
        room=link['room'],
        timestamp=tables.greater_than(cutoff_time)
    )
    
    data = []
    for reading in readings:
        data.append({
            "timestamp": reading['timestamp'],
            "temperature": reading['temperature'],
            "temp_min": reading['temp_min'],
            "temp_max": reading['temp_max'],
            "is_anomaly": reading['is_anomaly']
        })
    
    return {
        "room_name": link['room']['name'],
        "data": data,
        "view_count": link['view_count']
    }


@anvil.server.callable
@anvil.users.require_login
def export_room_data_csv(room, period):
    """
    Requires Login.
    
    Generates CSV file of readings for download.
    
    Args:
        room: Room row object
        period: Time range ("24h", "7d", "30d", "all")
    
    Returns:
        anvil.Media: CSV file for download
    """
    user = anvil.users.get_user()
    
    # Verify ownership
    if room['owner'] != user:
        raise Exception("Unauthorized access to room data")
    
    # Get readings
    if period == "all":
        readings = app_tables.readings.search(
            tables.order_by('timestamp', ascending=True),
            room=room
        )
    else:
        period_map = {
            "24h": timedelta(hours=24),
            "7d": timedelta(days=7),
            "30d": timedelta(days=30)
        }
        cutoff_time = datetime.now() - period_map[period]
        readings = app_tables.readings.search(
            tables.order_by('timestamp', ascending=True),
            room=room,
            timestamp=tables.greater_than(cutoff_time)
        )
    
    # Generate CSV
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['Timestamp', 'Temperature', 'Min', 'Max', 'Anomaly'])
    
    for reading in readings:
        writer.writerow([
            reading['timestamp'].isoformat(),
            reading['temperature'],
            reading['temp_min'],
            reading['temp_max'],
            'Yes' if reading['is_anomaly'] else 'No'
        ])
    
    return anvil.Media('text/csv', output.getvalue().encode(),
                       name=f"{room['name']}_{period}_data.csv")


@anvil.server.callable
def check_version(client_version):
    """
    Public function.
    
    Compares client version string with latest release.
    
    Args:
        client_version: Version string (e.g., "1.2.3")
    
    Returns:
        dict: {"update_available": true/false, "latest_version": "1.2.3"}
    """
    # This should be configured in Anvil app settings or environment
    latest_version = "1.0.0"  # Update this with each release
    
    return {
        "update_available": client_version != latest_version,
        "latest_version": latest_version
    }
