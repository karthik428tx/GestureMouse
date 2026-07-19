#!/usr/bin/env python3
"""
Hand Gesture Mouse Control - Main Entry Point

Controls:
    - Move cursor: Point with index finger
    - Left click: Touch thumb to index finger once
    - Double click: Touch thumb to index finger twice
    - Right click: Touch thumb to index finger three times
    - Quit: Press 'Q'

Usage:
    python main.py [--config config.yaml] [--no-display]
"""

import sys
import os
import argparse
import time
import yaml

import cv2

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.hand_tracker import HandTracker
from src.gesture_detector import GestureDetector
from src.mouse_controller import MouseController
from src.state_manager import GestureStateManager
from src.smoothing import create_smoother
from src.visualizer import Visualizer


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def main():
    # Parse arguments
    parser = argparse.ArgumentParser(description='Hand Gesture Mouse Control')
    parser.add_argument('--config', type=str, default='config.yaml',
                        help='Path to config file')
    parser.add_argument('--no-display', action='store_true',
                        help='Run without visual overlay')
    args = parser.parse_args()
    
    # Load configuration
    print(f"Loading config from: {args.config}")
    try:
        config = load_config(args.config)
    except FileNotFoundError:
        print(f"Error: Config file not found: {args.config}")
        print("Creating default config...")
        # Create default config if not exists
        default_config = {
            'camera': {'device_id': 0, 'width': 640, 'height': 480, 'fps': 30},
            'hand': {'dominant_side': 'RIGHT', 'detection_confidence': 0.7,
                    'tracking_confidence': 0.5, 'max_num_hands': 1},
            'gestures': {
                'cursor': {'tracking_landmark': 8, 'smoothing': {'type': 'ema', 'ema_alpha': 0.35,
                         'one_euro': {'min_cutoff': 0.001, 'beta': 0.4}},
                         'dead_zone_pixels': 3, 'speed_multiplier': 1.2},
                'left_click': {'thumb_landmark': 4, 'index_landmark': 8,
                              'pinch_threshold': 0.055, 'release_threshold': 0.075,
                              'cooldown_ms': 250},
                'right_click': {'wrist_landmark': 0, 'index_mcp_landmark': 5,
                               'pinky_mcp_landmark': 17, 'twist_threshold_degrees': 70,
                               'twist_direction': -1, 'hold_duration_ms': 80,
                               'cooldown_ms': 500}
            },
            'display': {'show_overlay': True, 'overlay_width': 400, 'overlay_height': 300,
                       'show_fps': True, 'show_landmarks': True, 'show_cursor_trail': False}
        }
        with open('config.yaml', 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
        config = default_config
    
    # Initialize components
    print("Initializing hand tracker...")
    hand_tracker = HandTracker(config)
    
    print("Initializing state manager...")
    state_manager = GestureStateManager(config)
    
    print("Initializing smoother...")
    smoother = create_smoother(config)
    
    print("Initializing gesture detector...")
    gesture_detector = GestureDetector(config, state_manager, smoother)
    
    print("Initializing mouse controller...")
    mouse_controller = MouseController(config)
    
    print("Initializing visualizer...")
    visualizer = Visualizer(config)
    
    # Initialize camera
    print("Opening camera...")
    cap = cv2.VideoCapture(config['camera']['device_id'])
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, config['camera']['width'])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config['camera']['height'])
    cap.set(cv2.CAP_PROP_FPS, config['camera']['fps'])
    
    if not cap.isOpened():
        print("Error: Could not open camera!")
        sys.exit(1)
    
    actual_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    actual_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    print(f"Camera opened: {actual_width}x{actual_height}")
    
    screen_w, screen_h = mouse_controller.get_screen_size()
    print(f"Screen size: {screen_w}x{screen_h}")
    
    print("\n" + "="*50)
    print("HAND GESTURE MOUSE CONTROL")
    print("="*50)
    print("Controls:")
    print("  • Point index finger = move cursor")
    print("  • Touch 1x = LEFT CLICK")
    print("  • Touch 2x = DOUBLE CLICK")
    print("  • Touch 3x = RIGHT CLICK")
    print("  • Press 'Q' to quit")
    print("="*50 + "\n")
    
    # Main loop
    running = True
    frame_count = 0
    start_time = time.time()
    
    try:
        while running:
            # Read frame
            ret, frame = cap.read()
            if not ret:
                print("Error: Could not read frame!")
                break
            
            # Detect hand
            landmarks = hand_tracker.process(frame)
            
            # Process gestures
            result = gesture_detector.process_landmarks(landmarks)
            
            # Execute mouse actions
            if result.hand_detected:
                if result.cursor_position:
                    mouse_controller.move_to(*result.cursor_position)

                if result.should_double_click:
                    mouse_controller.double_click()

                if result.should_left_click:
                    mouse_controller.left_click()

                if result.should_right_click:
                    mouse_controller.right_click()
            
            # Display
            if not args.no_display and config['display']['show_overlay']:
                frame = visualizer.draw(frame, result, landmarks)
                cv2.imshow('Gesture Mouse Control', frame)
                
                # Check for quit key
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == ord('Q'):
                    running = False
                elif key == 27:  # ESC
                    running = False
            
            frame_count += 1
            
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    
    finally:
        # Cleanup
        print("\nShutting down...")
        cap.release()
        cv2.destroyAllWindows()
        hand_tracker.release()
        
        elapsed = time.time() - start_time
        print(f"Ran for {elapsed:.1f}s, processed {frame_count} frames")
        print(f"Average FPS: {frame_count / elapsed:.1f}")


if __name__ == '__main__':
    main()