#!/usr/bin/env python3
"""
Debug script to test wiggle detection sensitivity.
Run with: python debug_wiggles.py
"""

import cv2
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.hand_tracker import HandTracker
from src.gesture_detector import GestureDetector
from src.smoothing import create_smoother
from src.state_manager import GestureStateManager
import yaml

def load_config(config_path: str) -> dict:
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def main():
    print("="*60)
    print("WIGGLE DETECTION DEBUG")
    print("="*60)
    print("Wiggle your fingers and watch the counts update.")
    print("Press 'Q' to quit\n")

    # Load config
    config = load_config('config.yaml')

    # Initialize components
    hand_tracker = HandTracker(config)
    state_manager = GestureStateManager(config)
    smoother = create_smoother(config)
    gesture_detector = GestureDetector(config, state_manager, smoother)

    # Initialize camera
    cap = cv2.VideoCapture(config['camera']['device_id'])
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config['camera']['width'])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config['camera']['height'])
    cap.set(cv2.CAP_PROP_FPS, config['camera']['fps'])

    if not cap.isOpened():
        print("Error: Could not open camera!")
        return 1

    print(f"Camera opened: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x"
          f"{int(cap.get(cv2.CAP_PROP_HEIGHT))}\n")

    print("Config parameters:")
    print(f"  Thumb threshold: {config['gestures']['left_click']['wiggle_detection']['threshold_pixels']} pixels")
    print(f"  Pinky threshold: {config['gestures']['right_click']['wiggle_detection']['threshold_pixels']} pixels")
    print(f"  Single click: {config['gestures']['left_click']['wiggle_detection']['single_click_wiggles']} wiggles")
    print(f"  Double click: {config['gestures']['left_click']['wiggle_detection']['double_click_wiggles']} wiggles\n")

    frame_count = 0
    max_thumb_wiggles = 0
    max_pinky_wiggles = 0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame!")
                break

            # Flip for mirror effect
            frame = cv2.flip(frame, 1)

            # Detect hand
            landmarks = hand_tracker.process(frame)

            # Process gestures
            result = gesture_detector.process_landmarks(landmarks)

            if result.hand_detected:
                thumb_wiggles = result.debug_info.get('thumb_wiggles', 0)
                pinky_wiggles = result.debug_info.get('pinky_wiggles', 0)

                # Track max wiggles seen
                if thumb_wiggles > max_thumb_wiggles:
                    max_thumb_wiggles = thumb_wiggles
                if pinky_wiggles > max_pinky_wiggles:
                    max_pinky_wiggles = pinky_wiggles

                # Display on frame
                h, w = frame.shape[:2]

                # Thumb info
                thumb_color = (0, 200, 255)
                cv2.putText(frame, f"THUMB: {thumb_wiggles} wiggles", (20, 40),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.0, thumb_color, 2)
                cv2.putText(frame, f"Max: {max_thumb_wiggles}", (20, 70),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, thumb_color, 1)

                # Pinky info
                pinky_color = (255, 100, 0)
                cv2.putText(frame, f"PINKY: {pinky_wiggles} wiggles", (20, 120),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.0, pinky_color, 2)
                cv2.putText(frame, f"Max: {max_pinky_wiggles}", (20, 150),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, pinky_color, 1)

                # History length
                thumb_history_len = len(gesture_detector.thumb_history)
                pinky_history_len = len(gesture_detector.pinky_history)
                cv2.putText(frame, f"Thumb history: {thumb_history_len}/30", (20, 200),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 1)
                cv2.putText(frame, f"Pinky history: {pinky_history_len}/30", (20, 230),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (100, 100, 100), 1)

                # Click feedback
                if result.should_double_click:
                    cv2.putText(frame, "DOUBLE CLICK!", (w//2 - 100, h//2),
                               cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)
                elif result.should_left_click:
                    cv2.putText(frame, "SINGLE CLICK!", (w//2 - 100, h//2),
                               cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
                elif result.should_right_click:
                    cv2.putText(frame, "RIGHT CLICK!", (w//2 - 100, h//2),
                               cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 0, 0), 3)

            else:
                cv2.putText(frame, "NO HAND DETECTED", (20, 40),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)

            # Instructions
            cv2.putText(frame, "Press 'Q' to quit | Wiggle fingers to test", (20, h - 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

            cv2.imshow('Wiggle Detection Debug', frame)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == ord('Q'):
                break

            frame_count += 1

    except KeyboardInterrupt:
        print("\nInterrupted")

    finally:
        print("\nShutting down...")
        cap.release()
        cv2.destroyAllWindows()
        hand_tracker.release()

        print(f"\nDebug Summary:")
        print(f"  Frames processed: {frame_count}")
        print(f"  Max thumb wiggles detected: {max_thumb_wiggles}")
        print(f"  Max pinky wiggles detected: {max_pinky_wiggles}")

        if max_thumb_wiggles == 0 and max_pinky_wiggles == 0:
            print("\n[!] No wiggles detected. Suggestions:")
            print("    1. Try wiggles with larger movements")
            print("    2. Lower threshold_pixels in config.yaml (currently 15)")
            print("    3. Try adjusting to 10 or 8 pixels for more sensitivity")

if __name__ == '__main__':
    sys.exit(main())
