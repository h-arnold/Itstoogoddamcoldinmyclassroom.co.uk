# Vendored Dependencies

This directory contains all Python dependencies bundled with the project for self-contained distribution.

## Why Vendor Dependencies?

- **No pip install required**: Users don't need to install dependencies
- **Offline capable**: Works without internet after initial download
- **Version locked**: Ensures consistent behavior across deployments
- **Pure Python only**: No compiled modules for maximum compatibility

## Included Libraries

### Core Dependencies

- **pyserial (3.5)**: Serial port communication with micro:bit
- **requests (2.32.3)**: HTTP client for Anvil API calls

### Transitive Dependencies

- **urllib3 (2.2.2)**: HTTP library used by requests
- **certifi (2024.7.4)**: SSL/TLS certificate bundle
- **idna (3.7)**: Internationalized domain name support
- **charset-normalizer (3.3.2)**: Character encoding detection (pure Python fallback)

## Validation

All dependencies are verified to be **pure Python only** (no `.so`, `.pyd`, or `.dylib` files).

The build process includes validation to ensure no compiled modules are present:
- GitHub Actions automatically checks on every build
- Build fails if any compiled modules are detected
- `vendor_dependencies.py` script removes compiled modules during installation

## Updating Dependencies

To update vendored dependencies:

```bash
# From repository root
python3 vendor_dependencies.py
```

This will:
1. Clean the vendor directory
2. Download latest compatible versions
3. Install to vendor/
4. Remove any compiled modules
5. Clean up unnecessary files

## Adding New Dependencies

1. Add to `requirements.txt` with version pin
2. Run `python3 vendor_dependencies.py`
3. Verify no compiled modules: `find vendor -name "*.so" -o -name "*.pyd"`
4. Test the build: `python3 build.py`
5. Check CI passes on GitHub Actions

## Structure

```
vendor/
├── serial/                    # pyserial package
├── requests/                  # requests package
├── urllib3/                   # urllib3 package
├── certifi/                   # certifi package
├── idna/                      # idna package
├── charset_normalizer/        # charset-normalizer package
├── pyserial-3.5.dist-info/
├── requests-2.32.5.dist-info/
├── urllib3-2.2.2.dist-info/
├── certifi-2024.7.4.dist-info/
├── idna-3.7.dist-info/
└── charset_normalizer-3.3.2.dist-info/
```

## Important Notes

- **Don't commit vendor contents**: The `.gitignore` file excludes vendor contents (except this README)
- **Regenerate before release**: Always run `vendor_dependencies.py` before creating a release
- **Test after update**: Verify the host script still works after dependency updates
- **Pure Python only**: Never include packages with compiled extensions

## Troubleshooting

### "Module not found" error

The vendor directory needs to be populated:
```bash
python3 vendor_dependencies.py
```

### Build fails with "compiled modules found"

Some packages may have compiled extensions. Options:
1. Find a pure Python alternative
2. Configure the package to use pure Python mode
3. Remove the problematic dependency

### Import errors after update

Check for API changes in updated dependencies:
```bash
# Test imports
python3 -c "import serial; import requests; print('OK')"
```

## Technical Details

### Installation Method

Dependencies are installed using:
```bash
pip install --target vendor --no-compile -r requirements.txt
```

Flags:
- `--target vendor`: Install to vendor directory
- `--no-compile`: Don't create `.pyc` files

### Cleanup Process

After installation:
1. Remove all `.so` files (Linux/macOS compiled)
2. Remove all `.pyd` files (Windows compiled)
3. Remove test directories
4. Remove `__pycache__` directories

### Import Mechanism

The host script adds vendor to the Python path:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'vendor'))
```

This allows importing vendored packages like regular packages.
