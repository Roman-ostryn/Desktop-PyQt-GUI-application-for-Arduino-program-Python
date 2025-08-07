#!/usr/bin/env python3
"""
Test script to verify command/response compatibility between backend and hardware
"""

import sys
import time
from PyQt6.QtCore import QCoreApplication
from serialcom.mock_serial_manager import SerialManager

def test_commands():
    print("Testing command/response compatibility...")
    
    app = QCoreApplication(sys.argv)
    serial = SerialManager()
    
    responses = []
    def capture_response(line):
        responses.append(line)
        print(f"Response: {line}")
    
    serial.line_received.connect(capture_response)
    serial.start()
    
    # Wait for READY
    time.sleep(0.1)
    app.processEvents()
    
    test_cases = [
        # Temperature commands
        ("SET_TEMP BREW 93", "OK:BREW_TEMP_SET"),
        ("SET_TEMP STEAM 130", "OK:STEAM_TEMP_SET"),
        ("SET_TEMP BREW 200", "ERROR:BREW_TEMP_OUT_OF_RANGE"),
        
        # State transitions
        ("START_BREW", "OK:BREW_STARTED"),
        ("BEGIN_BREW", "OK:BREWING_STARTED"),
        ("STOP", "OK:STOPPED"),
        
        ("START_STEAM", "OK:STEAM_STARTED"),
        ("STOP", "OK:STOPPED"),
        
        ("START_FLUSH", "OK:FLUSH_STARTED"),
        ("STOP", "OK:STOPPED"),
        
        # Utility commands
        ("TARE_SCALES", "OK:SCALES_TARED"),
        ("PING", "PONG"),
        ("ABORT", "OK:ABORTED"),
        ("INVALID_CMD", "ERROR:UNKNOWN_COMMAND"),
    ]
    
    passed = 0
    failed = 0
    
    for cmd, expected in test_cases:
        responses.clear()
        print(f"\nTesting: {cmd}")
        serial.send_command(cmd)
        
        # Wait for response
        time.sleep(0.1)
        app.processEvents()
        
        if responses and expected in responses[-1]:
            print(f"✅ PASS")
            passed += 1
        else:
            print(f"❌ FAIL - Expected: {expected}, Got: {responses}")
            failed += 1
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Total: {passed + failed}")
    
    # Test data format
    print(f"\n=== Testing Data Format ===")
    responses.clear()
    time.sleep(1)  # Wait for telemetry
    app.processEvents()
    
    if responses:
        data_msg = responses[-1]
        if data_msg.startswith("DATA:"):
            parts = data_msg[5:].split(',')
            if len(parts) >= 8:
                print(f"✅ Data format correct: {len(parts)} fields")
                print(f"   Format: state,temp,pressure,weight,pump%,valve,heater,brewTime")
            else:
                print(f"❌ Data format incorrect: {len(parts)} fields")
        else:
            print(f"❌ Expected DATA: message, got: {data_msg}")
    
    serial.stop()
    return failed == 0

if __name__ == "__main__":
    success = test_commands()
    sys.exit(0 if success else 1)