# Vendor Directory

This directory contains vendored pure Python dependencies for the host script.

## Dependencies

- **pyserial**: For serial communication with micro:bit
- **requests**: For HTTP POST to Anvil endpoint
- **charset-normalizer**: Dependency of requests (pure Python fallback used)
- **idna**: Dependency of requests (pure Python)
- **urllib3**: Dependency of requests (pure Python)
- **certifi**: Dependency of requests (pure Python)

## Setup

To populate this directory, run:

```bash
python3 vendor_dependencies.py
```

This will:
1. Download all dependencies
2. Remove any compiled modules (.so, .pyd)
3. Clean up unnecessary files

## Important

Only pure Python code should be in this directory. The GitHub Action build check will fail if any compiled modules (.so, .pyd files) are detected.
