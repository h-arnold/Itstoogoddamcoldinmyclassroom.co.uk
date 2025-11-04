#!/usr/bin/env python3
"""
Script to vendor pure Python dependencies for the host script.

This script downloads pyserial and requests (with their dependencies) and
ensures only pure Python code is included (no compiled modules).
"""

import subprocess
import sys
import os
import shutil
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n{description}...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(result.stdout)
    return True


def check_for_compiled_modules(vendor_dir):
    """Check for compiled modules (.so, .pyd) in vendor directory."""
    compiled_modules = []
    for ext in ['*.so', '*.pyd']:
        compiled_modules.extend(Path(vendor_dir).rglob(ext))
    return compiled_modules


def remove_compiled_modules(vendor_dir):
    """Remove compiled modules from vendor directory."""
    compiled_modules = check_for_compiled_modules(vendor_dir)
    if compiled_modules:
        print(f"\nFound {len(compiled_modules)} compiled modules:")
        for module in compiled_modules:
            print(f"  Removing: {module}")
            os.remove(module)
        print("Compiled modules removed.")
        return True
    else:
        print("\nNo compiled modules found. Good!")
        return False


def main():
    """Main vendoring function."""
    script_dir = Path(__file__).parent
    vendor_dir = script_dir / "vendor"
    
    print("=" * 60)
    print("Vendoring Pure Python Dependencies")
    print("=" * 60)
    
    # Clean vendor directory
    if vendor_dir.exists():
        print(f"\nCleaning existing vendor directory...")
        shutil.rmtree(vendor_dir)
    vendor_dir.mkdir(exist_ok=True)
    
    # Install dependencies
    packages = [
        "pyserial",
        "requests",
        "charset-normalizer",
        "idna",
        "urllib3",
        "certifi"
    ]
    
    print(f"\nInstalling packages: {', '.join(packages)}")
    cmd = f"pip install --target {vendor_dir} --no-compile {' '.join(packages)}"
    
    if not run_command(cmd, "Downloading and installing packages"):
        print("\nFailed to install packages. Please check your network connection.")
        sys.exit(1)
    
    # Remove compiled modules
    print("\n" + "=" * 60)
    print("Checking for compiled modules...")
    print("=" * 60)
    
    had_compiled = remove_compiled_modules(vendor_dir)
    
    # Verify no compiled modules remain
    remaining = check_for_compiled_modules(vendor_dir)
    if remaining:
        print(f"\nERROR: {len(remaining)} compiled modules still present:")
        for module in remaining:
            print(f"  {module}")
        print("\nPlease remove these manually or find pure Python alternatives.")
        sys.exit(1)
    
    # Remove unnecessary files
    print("\n" + "=" * 60)
    print("Cleaning up unnecessary files...")
    print("=" * 60)
    
    patterns_to_remove = [
        "**/__pycache__",
        "**/*.pyc",
        "**/*.pyo",
        "**/*.egg-info",
        "**/tests",
        "**/test",
    ]
    
    for pattern in patterns_to_remove:
        for path in vendor_dir.rglob(pattern):
            if path.is_dir():
                print(f"  Removing directory: {path}")
                shutil.rmtree(path)
            elif path.is_file():
                print(f"  Removing file: {path}")
                os.remove(path)
    
    print("\n" + "=" * 60)
    print("Vendoring complete!")
    print("=" * 60)
    print(f"\nVendored libraries are in: {vendor_dir}")
    print("\nNext steps:")
    print("1. Run build.py to create the distributable ZIP")
    print("2. GitHub Actions will verify no compiled modules are present")


if __name__ == "__main__":
    main()
