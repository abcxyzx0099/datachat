#!/usr/bin/env python3
"""
Simple test script to verify logging functionality.
This will be run manually to test the logging system.
"""
import sys
import time
import json

def main():
    # Test stdout
    print("TEST STDOUT: This is a test message to stdout")
    print("TEST STDOUT: Multiple lines to verify capture")

    # Test stderr
    sys.stderr.write("TEST STDERR: This is a test message to stderr\n")
    sys.stderr.write("TEST STDERR: Multiple stderr lines\n")
    sys.stderr.flush()

    # Add a small delay to ensure duration > 0
    time.sleep(0.5)

    # Create a result
    result = {
        "status": "completed",
        "stdout_test": "passed",
        "stderr_test": "passed",
        "duration_test": "passed",
        "message": "All logging tests completed successfully"
    }

    print(f"\nRESULT: {json.dumps(result, indent=2)}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
