#!/usr/bin/env python3
"""
Build script to create a self-contained ZIP distribution.

This script bundles:
- host_script.py
- config.txt (template)
- vendor/ directory with pure Python dependencies

The resulting ZIP can be extracted and run on any system with Python 3.8+
"""

import zipfile
import sys
from pathlib import Path
from datetime import datetime


def check_for_compiled_modules(vendor_dir):
    """Check for compiled modules (.so, .pyd) in vendor directory."""
    compiled_modules = []
    for ext in ['*.so', '*.pyd']:
        compiled_modules.extend(Path(vendor_dir).rglob(ext))
    return compiled_modules


def create_zip_bundle(output_filename="microbit_temp_monitor.zip"):
    """Create ZIP bundle with all required files."""
    script_dir = Path(__file__).parent
    vendor_dir = script_dir / "vendor"
    
    print("=" * 60)
    print("Building Self-Contained ZIP Distribution")
    print("=" * 60)
    
    # Check vendor directory exists and has content
    if not vendor_dir.exists():
        print(f"\nError: Vendor directory does not exist: {vendor_dir}")
        print("Please run vendor_dependencies.py first to populate dependencies.")
        sys.exit(1)
    
    # Check for Python packages in vendor
    has_packages = any((vendor_dir / pkg).exists() for pkg in ['serial', 'requests'])
    if not has_packages:
        print(f"\nWarning: Vendor directory appears empty or incomplete.")
        print("Expected to find 'serial' and 'requests' packages.")
        print("Please run vendor_dependencies.py to populate dependencies.")
        # Continue anyway for demonstration purposes
    
    # Check for compiled modules
    print("\nChecking for compiled modules...")
    compiled_modules = check_for_compiled_modules(vendor_dir)
    
    if compiled_modules:
        print(f"\nERROR: Found {len(compiled_modules)} compiled modules:")
        for module in compiled_modules:
            print(f"  - {module.relative_to(script_dir)}")
        print("\nThe bundle must contain only pure Python code.")
        print("Please run vendor_dependencies.py to clean the vendor directory.")
        sys.exit(1)
    print("  ✓ No compiled modules found")
    
    # Files to include from src/
    files_to_bundle = [
        ("src/host_script.py", "host_script.py"),
        ("src/config.txt", "config.txt"),
    ]
    
    # Check required files exist
    print("\nChecking required files...")
    missing_files = []
    for src_path, _ in files_to_bundle:
        filepath = script_dir / src_path
        if not filepath.exists():
            missing_files.append(src_path)
        else:
            print(f"  ✓ {src_path}")
    
    if missing_files:
        print(f"\nError: Missing required files:")
        for src_path in missing_files:
            print(f"  - {src_path}")
        sys.exit(1)
    
    # Create ZIP
    output_path = script_dir / output_filename
    print(f"\nCreating ZIP bundle: {output_filename}")
    
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add main files from src/
        for src_path, dest_name in files_to_bundle:
            filepath = script_dir / src_path
            print(f"  Adding: {src_path} -> {dest_name}")
            zipf.write(filepath, dest_name)
        
        # Add vendor directory
        print(f"  Adding: vendor/ directory")
        for filepath in vendor_dir.rglob('*'):
            if filepath.is_file():
                # Get path relative to script directory
                arcname = filepath.relative_to(script_dir)
                zipf.write(filepath, arcname)
    
    # Report success
    file_size = output_path.stat().st_size
    print(f"\n{'=' * 60}")
    print(f"Build complete!")
    print(f"{'=' * 60}")
    print(f"Output: {output_path}")
    print(f"Size: {file_size:,} bytes ({file_size / 1024:.1f} KB)")
    print(f"\nTo use:")
    print(f"  1. Extract {output_filename}")
    print(f"  2. Edit config.txt with your API key and settings")
    print(f"  3. Run: python3 host_script.py")


def main():
    """Main build function."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_filename = f"microbit_temp_monitor_{timestamp}.zip"
    
    try:
        create_zip_bundle(output_filename)
    except KeyboardInterrupt:
        print("\n\nBuild cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError during build: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
