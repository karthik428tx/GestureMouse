"""
Visual feedback overlay using OpenCV.
"""

import cv2
import numpy as np
import math
from typing import Optional, Tuple, Dict, Any


class Visualizer:
    """Draws visual feedback for gesture detection."""

    # Colors (BGR format)
    COLOR_BG = (40, 40, 40)
    COLOR_TEXT = (255, 255, 255)
    COLOR_CURSOR = (0, 255, 0)  # Green
    COLOR_TOUCH = (0, 200, 255)  # Orange-blue
    COLOR_LANDMARK = (255, 255, 255)
    COLOR_CONNECTION = (100, 100, 100)
    COLOR_GOOD = (0, 255, 0)
    COLOR_WARNING = (0, 165, 255)
    COLOR_DANGER = (0, 0, 255)

    def __init__(self, config: dict):
        self.config = config
        self.show_fps = config['display']['show_fps']
        self.show_landmarks = config['display']['show_landmarks']
        self.overlay_width = config['display']['overlay_width']
        self.overlay_height = config['display']['overlay_height']

        # FPS tracking
        self.fps = 0.0
        self.frame_count = 0
        self.fps_update_time = 0

    def update_fps(self):
        """Calculate current FPS."""
        import time
        self.frame_count += 1
        current_time = time.time()

        if current_time - self.fps_update_time >= 1.0:
            self.fps = self.frame_count / (current_time - self.fps_update_time)
            self.frame_count = 0
            self.fps_update_time = current_time

    def draw(self, frame, gesture_result, landmarks) -> np.ndarray:
        """
        Draw visual feedback on frame.

        Args:
            frame: OpenCV frame from webcam
            gesture_result: GestureResult from detector
            landmarks: MediaPipe landmarks (or None)

        Returns:
            Annotated frame
        """
        self.update_fps()

        # Flip frame for mirror effect
        frame = cv2.flip(frame, 1)

        if landmarks is not None:
            if self.show_landmarks:
                self._draw_landmarks(frame, landmarks)
            self._draw_gesture_indicator(frame, gesture_result)

        # Draw status panel
        self._draw_status_panel(frame, gesture_result)

        return frame

    def _draw_landmarks(self, frame, landmarks):
        """Draw hand landmarks and connections."""
        h, w = frame.shape[:2]

        # Handle both old and new API
        def get_landmark(idx):
            if hasattr(landmarks, 'landmark'):
                return landmarks.landmark[idx]
            else:
                return landmarks[idx]

        # Draw connections
        connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),  # Thumb
            (0, 5), (5, 6), (6, 7), (7, 8),  # Index
            (0, 9), (9, 10), (10, 11), (11, 12),  # Middle
            (0, 13), (13, 14), (14, 15), (15, 16),  # Ring
            (0, 17), (17, 18), (18, 19), (19, 20),  # Pinky
            (5, 9), (9, 13), (13, 17)  # Palm
        ]

        for start, end in connections:
            start_point = (int(get_landmark(start).x * w),
                          int(get_landmark(start).y * h))
            end_point = (int(get_landmark(end).x * w),
                        int(get_landmark(end).y * h))
            cv2.line(frame, start_point, end_point, self.COLOR_CONNECTION, 2)

        # Draw landmarks
        for idx in range(21):
            landmark = get_landmark(idx)
            point = (int(landmark.x * w), int(landmark.y * h))
            color = self.COLOR_LANDMARK
            radius = 3

            # Highlight key points
            if idx == 8:  # Index tip (cursor)
                color = self.COLOR_CURSOR
                radius = 6
            elif idx == 4:  # Thumb tip (touch detection)
                color = self.COLOR_TOUCH
                radius = 5
            elif idx == 6:  # Index middle (touch target)
                color = self.COLOR_TOUCH
                radius = 5

            cv2.circle(frame, point, radius, color, -1)

    def _draw_gesture_indicator(self, frame, gesture_result):
        """Draw visual indicator for touch gestures."""
        debug_info = gesture_result.debug_info
        if not debug_info:
            return

        h, w = frame.shape[:2]

        # Draw touch count
        touch_count = debug_info.get('touch_count', 0)
        touch_max = debug_info.get('touch_max', 0)
        touch_distance = debug_info.get('touch_distance', 999)

        cv2.putText(frame, f"Touches: {touch_count} (max: {touch_max})", (20, 40),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.COLOR_TOUCH, 2)

        # Draw touch distance
        distance_color = self.COLOR_GOOD if touch_distance > 0.08 else self.COLOR_DANGER
        cv2.putText(frame, f"Distance: {touch_distance:.3f}", (20, 70),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, distance_color, 1)

    def _draw_status_panel(self, frame, gesture_result):
        """Draw status information panel."""
        h, w = frame.shape[:2]
        y_offset = h - 100

        # Background rectangle
        cv2.rectangle(frame, (10, y_offset - 10), (280, h - 5),
                      (0, 0, 0), -1)

        # FPS
        if self.show_fps:
            fps_color = self.COLOR_GOOD if self.fps > 25 else self.COLOR_DANGER
            cv2.putText(frame, f"FPS: {self.fps:.1f}", (15, y_offset + 15),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, fps_color, 1)

        # Hand status
        hand_status = "HAND: YES" if gesture_result.hand_detected else "HAND: NO"
        hand_color = self.COLOR_GOOD if gesture_result.hand_detected else self.COLOR_DANGER
        cv2.putText(frame, hand_status, (15, y_offset + 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, hand_color, 1)

        # Click feedback
        click_text = ""
        click_color = (255, 255, 255)

        if gesture_result.should_double_click:
            click_text = "DOUBLE CLICK!"
            click_color = (0, 0, 255)
        elif gesture_result.should_left_click:
            click_text = "SINGLE CLICK!"
            click_color = self.COLOR_GOOD
        elif gesture_result.should_right_click:
            click_text = "RIGHT CLICK!"
            click_color = (255, 0, 0)

        if click_text:
            cv2.putText(frame, click_text, (15, y_offset + 55),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, click_color, 2)

        # Instructions
        cv2.putText(frame, "Press Q to quit | Touch=Click", (15, y_offset + 75),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)
