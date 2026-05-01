#!/usr/bin/env python3
"""
Diagnose and fix virtual environment issues.
"""

import sys
import os
import subprocess
from pathlib import Path

def diagnose():
    """Diagnose virtual environment issues."""
    print("🔍 Diagnosing Virtual Environment Issues")
    print("=" * 50)
    
    project_dir = Path(__file__).parent
    venv_dir = project_dir / ".venv"
    
    print(f"Project Directory: {project_dir}")
    print(f"Virtual Env Path: {venv_dir}")
    print(f"Virtual Env Exists: {venv_dir.exists()}")
    
    # Check Python
    print(f"\nPython Executable: {sys.executable}")
    print(f"Python Version: {sys.version}")
    
    # Check if pytest is accessible
    try:
        import pytest
        print(f"✅ pytest is installed: {pytest.__file__}")
    except ImportError:
        print(f"❌ pytest is NOT installed")
    
    # Check if requirements are met
    try:
        import playwright
        print(f"✅ playwright is installed")
    except ImportError:
        print(f"❌ playwright is NOT installed")
    
    try:
        import openpyxl
        print(f"✅ openpyxl is installed")
    except ImportError:
        print(f"❌ openpyxl is NOT installed")

def run_tests():
    """Try to run tests using the current Python."""
    print("\n🚀 Attempting to Run Tests")
    print("=" * 50)
    
    project_dir = Path(__file__).parent
    os.chdir(project_dir)
    
    # Try running pytest directly
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/test_user_management.py",
        "-v", "--tb=short"
    ]
    
    print(f"Command: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(cmd, timeout=300)
        return result.returncode
    except Exception as e:
        print(f"❌ Error: {e}")
        return -1

def main():
    """Main function."""
    diagnose()
    exit_code = run_tests()
    
    if exit_code == 0:
        print("\n✅ Tests passed!")
    elif exit_code == 1:
        print("\n⚠️  Some tests failed")
    else:
        print(f"\n❌ Tests failed with exit code {exit_code}")

if __name__ == "__main__":
    main()
