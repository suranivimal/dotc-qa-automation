#!/usr/bin/env python3
"""
Run only the specific dating mode filter active test.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_specific_test():
    """Run only the dating mode filter active test."""
    print("🎯 Running Specific Test: Dating Mode Filter Active")
    print("=" * 60)

    # Change to project directory
    project_dir = Path(__file__).parent
    os.chdir(project_dir)

    # Run the specific test
    cmd = [
        sys.executable, "-m", "pytest",
        "tests/test_user_management.py::TestFilters::test_dating_mode_filter_active",
        "-v", "--tb=short",
        "--capture=no"  # Don't capture output
    ]

    print(f"Executing: {' '.join(cmd)}")
    print()

    try:
        result = subprocess.run(cmd, cwd=project_dir, timeout=300)
        print(f"\n✅ Test completed with exit code: {result.returncode}")

        if result.returncode == 0:
            print("🎉 TEST PASSED - Dating mode filtering is working correctly")
        elif result.returncode == 1:
            print("❌ TEST FAILED - Dating mode filtering is broken!")
            print("   This confirms the issue you identified with pagination still showing")
        else:
            print(f"⚠️  Test execution issue (exit code: {result.returncode})")

        return result.returncode

    except subprocess.TimeoutExpired:
        print("⏰ Test timed out after 5 minutes")
        return -1
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return -1

def main():
    """Main function."""
    exit_code = run_specific_test()

    print("\n" + "=" * 60)
    print("📋 SUMMARY:")
    if exit_code == 0:
        print("   ✅ Filter working: Only Active users shown, no pagination")
    elif exit_code == 1:
        print("   ❌ Filter broken: Still shows pagination with non-Active users")
        print("   📧 Email notification should be sent")
        print("   🐛 Bug report should be created")
    else:
        print("   ⚠️  Test execution failed")

    print("\n🔍 Check:")
    print("   📊 Excel report for FAIL status")
    print("   📧 Email inbox for failure notification")
    print("   🐛 reports/bugs/ for bug report")
    print("   📸 reports/screenshots/ for failure screenshot")

if __name__ == "__main__":
    main()
