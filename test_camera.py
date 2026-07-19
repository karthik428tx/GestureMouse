#!/usr/bin/env python3
"""Test camera connectivity and properties."""

import cv2
import sys

def test_camera(device_id=0):
    """Test if camera is accessible."""
    print(f"Testing camera device {device_id}...")

    cap = cv2.VideoCapture(device_id)

    if not cap.isOpened():
        print(f"[ERROR] Could not open camera device {device_id}")
        return False

    print(f"[OK] Camera opened successfully")

    # Try to read a frame
    ret, frame = cap.read()

    if not ret or frame is None:
        print(f"[ERROR] Could not read frame from camera")
        cap.release()
        return False

    print(f"[OK] Successfully read frame")
    print(f"    Frame size: {frame.shape[1]}x{frame.shape[0]}")

    # Test a few more frames
    for i in range(5):
        ret, frame = cap.read()
        if not ret:
            print(f"[ERROR] Failed to read frame {i+1}")
            cap.release()
            return False

    print(f"[OK] Read 5 consecutive frames successfully")
    cap.release()
    return True

def main():
    print("=" * 60)
    print("Camera Diagnostics")
    print("=" * 60)

    # Test default camera
    if test_camera(0):
        print("\n[SUCCESS] Camera is working!")
        return 0
    else:
        print("\n[FAILED] Default camera (device 0) is not working")
        print("\nTroubleshooting:")
        print("1. Check if camera is physically connected")
        print("2. Check camera permissions in Windows Settings")
        print("3. Try a different device ID:")
        print("   python test_camera.py -d <device_id>")
        return 1

if __name__ == '__main__':
    # Check for device_id argument
    device_id = 0
    if len(sys.argv) > 2 and sys.argv[1] == '-d':
        device_id = int(sys.argv[2])

    sys.exit(main() if device_id == 0 else test_camera(device_id))
