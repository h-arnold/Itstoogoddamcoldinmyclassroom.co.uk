# GitHub Copilot Custom Instructions

## Project Context

This is a classroom temperature monitoring system using BBC micro:bit hardware and Python host scripts. The system:

- Reads temperature from micro:bit via USB serial
- Calculates rolling averages over 20-minute periods
- Posts data to an Anvil web application
- Uses vendored pure Python dependencies (no compiled modules)

## Code Style Guidelines

### Python
- Follow PEP 8 style guidelines
- Use type hints where appropriate
- Maximum line length: 100 characters
- Use descriptive variable names
- Add docstrings to all functions and classes
- Prefer f-strings for string formatting

### File Organization
- `src/`: Main application code
- `microbit/`: MicroPython code for BBC micro:bit
- `docs/`: All documentation files
- `vendor/`: Vendored dependencies (pure Python only)

## Important Constraints

### Pure Python Only
- **CRITICAL**: No compiled modules (.so, .pyd, .dylib)
- All dependencies must be pure Python
- The build process validates this and fails if violated

### Dependencies
- pyserial (serial communication)
- requests (HTTP client)
- All transitive dependencies must be pure Python

### Configuration
- Use `config.txt` for all user-configurable settings
- Never hardcode API keys or endpoints
- Provide clear error messages for missing/invalid config

## Testing Approach

- Validate builds don't contain compiled modules
- Test serial communication with mock data when no hardware available
- Verify HTTP posting with test endpoints
- Check error handling for disconnections and network issues

## Common Tasks

### Adding New Features
- Maintain backward compatibility with existing config files
- Update both the host script and documentation
- Ensure changes work across Windows, macOS, and Linux

### Updating Dependencies
- Use `vendor_dependencies.py` to update vendored packages
- Verify no compiled modules introduced
- Update `requirements.txt` with version pins
- Test build process after updates

### Documentation Updates
- Keep README.md in sync with code changes
- Update SETUP_GUIDE.md for user-facing changes
- Update technical spec for architectural changes

## Architecture Notes

### Data Flow
```
micro:bit → Serial (USB) → host_script.py → HTTP POST → Anvil
  (30s)         (pyserial)      (20min avg)    (requests)
```

### Build Process
1. Vendor dependencies (pure Python only)
2. Validate no compiled modules
3. Bundle host script + config + vendor/
4. Create timestamped ZIP
5. Upload as GitHub Actions artifact

## Security Considerations

- API keys stored in local config (never committed)
- HTTPS for all web communication
- Rate limiting on server side
- Input validation for temperature readings

## Common Pitfalls to Avoid

- Don't commit `config.txt` with real API keys
- Don't add dependencies without checking for compiled modules
- Don't hardcode file paths (use Path objects)
- Don't skip error handling for serial/network operations
- Don't break the pure Python constraint

## Helpful Resources

- [Anvil Documentation](https://anvil.works/docs)
- [BBC micro:bit Python API](https://microbit-micropython.readthedocs.io/)
- [pyserial Documentation](https://pyserial.readthedocs.io/)
- Technical Specification: `docs/classroom_temp_spec.md`
