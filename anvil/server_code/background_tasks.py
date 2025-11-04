"""
Anvil Background Task: Data Retention

This module handles automatic deletion of old readings (>90 days).
Should be scheduled to run daily.
"""

import anvil.server
from anvil.tables import app_tables
from datetime import datetime, timedelta


@anvil.server.background_task
def cleanup_old_readings():
    """
    Background Task: Delete readings older than 90 days.
    
    This task should be scheduled to run daily via Anvil's Background Tasks.
    Retention period is configurable (default: 90 days).
    """
    retention_days = 90  # Configurable
    cutoff_date = datetime.now() - timedelta(days=retention_days)
    
    # Find old readings
    old_readings = app_tables.readings.search(
        timestamp=tables.less_than(cutoff_date)
    )
    
    # Count for logging
    count = 0
    for reading in old_readings:
        reading.delete()
        count += 1
    
    print(f"Data retention task completed. Deleted {count} readings older than {retention_days} days.")
    
    return {
        "deleted_count": count,
        "cutoff_date": cutoff_date.isoformat(),
        "retention_days": retention_days
    }
