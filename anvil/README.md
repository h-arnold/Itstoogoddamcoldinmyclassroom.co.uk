# Anvil Web Application Code

This directory contains the server-side Python code for the Anvil web application that powers the classroom temperature monitoring dashboard.

## Overview

The Anvil application provides:
- HTTP endpoint for receiving temperature data from host scripts
- User authentication and API key management
- Data storage and retrieval
- Public sharing links for classroom data
- Interactive dashboard with charts
- CSV data export

## Directory Structure

```
anvil/
├── server_code/              # Server-side Python modules
│   ├── temperature_logging.py   # HTTP endpoint for data ingestion
│   ├── server_functions.py      # Callable functions for client
│   └── background_tasks.py      # Scheduled tasks (data retention)
├── client_code/              # Client-side Python/JavaScript (not included)
└── README.md                 # This file
```

## Server Modules

### temperature_logging.py

HTTP endpoint that receives temperature data from host scripts.

**Endpoint**: `POST /_/api/log_temp`

**Features**:
- API key authentication
- Rate limiting (1 submission per 19 minutes per key)
- Temperature validation (5°C to 35°C, flags anomalies)
- Automatic room creation
- Error handling with appropriate HTTP status codes

### server_functions.py

Callable functions that can be invoked from the client interface.

**Functions**:

**Public (no login required)**:
- `get_global_average()` - Returns average temperature across all classrooms (cached 5 min)
- `get_public_share_data(token)` - Returns data for public share links
- `check_version(client_version)` - Version checking for host scripts

**Requires Login**:
- `get_my_rooms()` - Returns user's rooms with last reading timestamps
- `get_room_data(room, period)` - Fetches readings for plotting (24h/7d/30d)
- `generate_api_key()` - Creates new API key for host scripts
- `revoke_api_key(key_row)` - Deletes API key
- `create_share_link(room_row, expires_days)` - Creates public share link with optional expiry
- `revoke_share_link(link_row)` - Deletes share link
- `export_room_data_csv(room, period)` - Generates CSV download

### background_tasks.py

Scheduled background task for data maintenance.

**Task**:
- `cleanup_old_readings()` - Deletes readings older than 90 days (configurable)

Should be scheduled to run daily via Anvil's Background Tasks UI.

## Data Model

### Database Tables

**Users**
- Managed by Anvil's built-in Users service
- Fields: email, password_hash, created

**ApiKeys**
- owner: Link to Users
- key: Text (Unique, Indexed) - Format: "key_" + 32 hex chars
- created: DateTime
- last_used: DateTime

**Rooms**
- owner: Link to Users
- name: Text (Unique per user, Indexed)
- created: DateTime

**Readings**
- room: Link to Rooms
- timestamp: DateTime (Indexed, UTC)
- temperature: Number
- temp_min: Number
- temp_max: Number
- is_anomaly: Boolean

**ShareLinks**
- room: Link to Rooms
- token: Text (Unique UUID, Indexed)
- created: DateTime
- expires: DateTime (Optional)
- view_count: Number

## Setup Instructions

### 1. Create Anvil App

1. Go to [anvil.works](https://anvil.works)
2. Create a new app (Python/Full Stack)
3. Enable the Users service
4. Create the database tables as specified above

### 2. Add Server Modules

1. In Anvil editor, go to Server Code section
2. Add new modules:
   - `temperature_logging`
   - `server_functions`
   - `background_tasks`
3. Copy the code from the corresponding `.py` files

### 3. Configure HTTP Endpoint

The HTTP endpoint is automatically created when you use the `@anvil.server.http_endpoint` decorator.

Access it at: `https://your-app.anvil.app/_/api/log_temp`

### 4. Set Up Background Task

1. In Anvil editor, go to Background Tasks
2. Create new task: "Data Retention"
3. Set to call `background_tasks.cleanup_old_readings`
4. Schedule: Daily at 2:00 AM (or preferred time)

### 5. Configure Client Pages

Client pages should be created in Anvil's visual designer:

**Pages to create**:
- **Homepage**: Display global average, login/signup, handle share links
- **Dashboard**: Interactive charts, room selector, time range picker
- **Settings**: API key management, share links, data export
- **Help**: Setup instructions, troubleshooting

See `docs/classroom_temp_spec.md` section 4.3 for detailed page specifications.

## Security Considerations

### API Keys
- Generated with cryptographically secure randomness (`secrets` module)
- Stored plain in database for validation
- Never logged or exposed except at generation time
- Transmitted over HTTPS only

### Rate Limiting
- Implemented via in-memory cache
- Prevents abuse (1 submission per 19 minutes)
- Per-API-key enforcement

### Share Links
- UUID4 tokens (122 bits of entropy)
- Optional expiry dates
- View count tracking for monitoring

### Data Access
- Room ownership verified on all operations
- User authentication required for management functions
- Public functions limited to read-only aggregated data

## API Usage Examples

### Logging Temperature (from host script)

```bash
curl -X POST https://your-app.anvil.app/_/api/log_temp \
  -H "Content-Type: application/json" \
  -d '{
    "api_key": "key_abc123...",
    "room_name": "Room_B12",
    "temperature": 18.5,
    "temp_min": 17.8,
    "temp_max": 19.2,
    "timestamp": "2025-11-04T14:30:00Z"
  }'
```

### Getting Global Average (from client)

```python
import anvil.server

data = anvil.server.call('get_global_average')
# Returns: {"average": 19.2, "sample_count": 450, "room_count": 15}
```

### Creating Share Link (from client)

```python
import anvil.server

room_row = app_tables.rooms.get(name="Room_B12")
url = anvil.server.call('create_share_link', room_row, expires_days=30)
# Returns: "https://itstoodamncoldinmyclassroom.co.uk/#share=uuid..."
```

## Performance Optimization

### Caching
- Global average cached for 5 minutes
- Reduces database load for public homepage

### Indexing
- Timestamp field indexed for fast queries
- API keys and tokens indexed for lookups
- Room names indexed for user searches

### Rate Limiting
- In-memory cache for speed
- Prevents database overload from excessive submissions

## Monitoring and Maintenance

### Daily Tasks
- Review Background Task logs for data retention
- Monitor API endpoint error rates

### Weekly Tasks
- Check for rooms with no recent readings (>24 hours)
- Review anomaly flags for patterns

### Monthly Tasks
- Analyze usage patterns
- Optimize queries if needed
- Review and adjust rate limits

## Troubleshooting

### "401 Unauthorized" errors
- Verify API key exists in ApiKeys table
- Check API key hasn't been revoked
- Ensure key matches format: "key_" + 32 hex chars

### "429 Too Many Requests" errors
- Normal if host script retries too quickly
- Check rate limit cache or adjust interval

### Missing readings
- Check host script is running
- Verify network connectivity
- Review HTTP endpoint logs for errors

### Background task not running
- Verify task is scheduled in Anvil UI
- Check task execution logs
- Ensure retention period is set correctly

## Development Notes

### Testing
- Use Anvil's test environment with dummy data
- Create test API keys separate from production
- Test rate limiting with multiple submissions

### Deployment
- Anvil handles hosting and scaling
- SSL certificates managed automatically
- Database backups handled by Anvil

### Updates
- Update server code directly in Anvil editor
- No downtime required for code changes
- Test in development environment first

## Support

For Anvil-specific issues:
- [Anvil Documentation](https://anvil.works/docs)
- [Anvil Forum](https://anvil.works/forum)

For project-specific issues:
- See main repository documentation
- Open issue on GitHub
- Check technical specification: `docs/classroom_temp_spec.md`

## Version

Server Code Version: 1.0.0  
Last Updated: 2025-11-04  
Compatible with: Host Script v1.0.0+
