"""
Gesture detection from hand landmarks - Touch-based gestures.
"""

import math
import time
from typing import Optional, Tuple, Dict, Any
from dataclasses import dataclass
from enum import Enum

from .geometry import Point2D


class TouchState(Enum):
    """State of a touch gesture."""
    IDLE = 0      # Fingers apart
    TOUCHING = 1  # Fingers touching
    RELEASED = 2  # Just released after touching


@dataclass
class GestureResult:
    """Result of gesture detection for a single frame."""
    hand_detected: bool
    cursor_position: Optional[Tuple[float, float]]
    should_left_click: bool
    should_double_click: bool
    should_right_click: bool
    should_quit: bool
    debug_info: Dict[str, Any]


class GestureDetector:
    """
    Detects gestures from MediaPipe hand landmarks.

    Gestures:
    - 1 touch: Single left click
    - 2 touches: Double left click
    - 3 touches: Right click
    - Fist close: Quit application
    """

    def __init__(self, config: dict, state_manager, smoother):
        self.config = config
        self.state_manager = state_manager
        self.smoother = smoother

        # Landmark indices
        self.index_tip = config['gestures']['cursor']['tracking_landmark']
        self.thumb_tip = config['gestures']['left_click']['thumb_landmark']
        self.index_middle = config['gestures']['left_click']['index_landmark']

        # Screen dimensions
        import pyautogui
        self.screen_width, self.screen_height = pyautogui.size()

        # Speed multiplier
        self.speed_multiplier = config['gestures']['cursor']['speed_multiplier']
        self.dead_zone = config['gestures']['cursor']['dead_zone_pixels']

        # Previous position for dead zone calculation
        self.prev_screen_pos: Optional[Tuple[float, float]] = None

        # Touch detection parameters
        self.touch_threshold = config['gestures']['left_click']['touch_detection']['touch_threshold']
        self.single_click_touches = config['gestures']['left_click']['touch_detection']['single_click_touches']
        self.double_click_touches = config['gestures']['left_click']['touch_detection']['double_click_touches']
        self.right_click_touches = config['gestures']['right_click']['touch_detection']['right_click_touches']
        self.touch_cooldown_ms = config['gestures']['left_click']['touch_detection']['cooldown_ms']
        self.right_click_cooldown_ms = config['gestures']['right_click']['touch_detection']['cooldown_ms']

        # Touch state tracking
        self.touch_state = TouchState.IDLE
        self.touch_count = 0
        self.max_touch_count = 0
        self.release_frame_count = 0  # Track frames in RELEASED state for multi-touch

        # Cooldown tracking
        self.last_left_click_time = 0
        self.last_right_click_time = 0

        # Allow ~300ms observation time for multiple touches (at 30fps = ~9 frames)
        self.release_hold_frames = 10

        # Hand closure (for quit gesture)
        self.closure_threshold = config['gestures']['quit_gesture']['hand_closure_threshold']
        self.closure_hold_frames = config['gestures']['quit_gesture']['hold_frames']
        self.closure_frame_count = 0

    def process_landmarks(self, landmarks) -> GestureResult:
        """
        Process hand landmarks and detect touch gestures.

        Args:
            landmarks: MediaPipe hand landmarks

        Returns:
            GestureResult with detected gestures
        """
        if landmarks is None:
            self.smoother.reset()
            self.prev_screen_pos = None
            self.touch_state = TouchState.IDLE
            self.touch_count = 0
            self.closure_frame_count = 0
            return GestureResult(
                hand_detected=False,
                cursor_position=None,
                should_left_click=False,
                should_double_click=False,
                should_right_click=False,
                should_quit=False,
                debug_info={}
            )

        # Handle both old and new API
        def get_landmark(idx):
            if hasattr(landmarks, 'landmark'):
                return landmarks.landmark[idx]
            else:
                return landmarks[idx]

        # Extract key points
        index_tip = get_landmark(self.index_tip)
        thumb_tip = get_landmark(self.thumb_tip)
        index_mid = get_landmark(self.index_middle)

        index_tip_point = Point2D(index_tip.x, index_tip.y)
        thumb_tip_point = Point2D(thumb_tip.x, thumb_tip.y)
        index_mid_point = Point2D(index_mid.x, index_mid.y)

        # --- Cursor Position ---
        from .geometry import map_coordinates, clamp

        raw_screen_x, raw_screen_y = map_coordinates(
            index_tip_point.x, index_tip_point.y,
            self.screen_width, self.screen_height,
            mirror_x=True
        )

        # Apply smoothing
        smoothed_x, smoothed_y = self.smoother.smooth(raw_screen_x, raw_screen_y)

        # Apply dead zone
        if self.prev_screen_pos is not None:
            dx = smoothed_x - self.prev_screen_pos[0]
            dy = smoothed_y - self.prev_screen_pos[1]
            distance = math.sqrt(dx*dx + dy*dy)

            if distance < self.dead_zone:
                smoothed_x, smoothed_y = self.prev_screen_pos

        cursor_x = clamp(smoothed_x, 0, self.screen_width - 1)
        cursor_y = clamp(smoothed_y, 0, self.screen_height - 1)
        self.prev_screen_pos = (cursor_x, cursor_y)

        # --- Touch Detection ---
        current_time = time.time() * 1000

        # Measure distance between thumb and index middle
        touch_distance = thumb_tip_point.distance_to(index_mid_point)

        # Update touch state - allow ~300ms for multiple touches
        if self.touch_state == TouchState.IDLE:
            if touch_distance < self.touch_threshold:
                self.touch_state = TouchState.TOUCHING
                self.release_frame_count = 0

        elif self.touch_state == TouchState.TOUCHING:
            if touch_distance > self.touch_threshold:
                self.touch_state = TouchState.RELEASED
                self.touch_count += 1
                self.max_touch_count = max(self.max_touch_count, self.touch_count)
                self.release_frame_count = 0

        elif self.touch_state == TouchState.RELEASED:
            # Keep waiting in RELEASED state for ~10 frames (~300ms at 30fps)
            # This allows user to touch again for multiple touches
            if touch_distance < self.touch_threshold:
                # User touching again - go back to TOUCHING
                self.touch_state = TouchState.TOUCHING
                self.release_frame_count = 0
            else:
                self.release_frame_count += 1
                # After holding released for several frames, go back to IDLE
                if self.release_frame_count >= self.release_hold_frames:
                    self.touch_state = TouchState.IDLE
                    self.release_frame_count = 0

        # Check for click triggers (only once per gesture sequence)
        # No cooldown restrictions - unlimited actions
        should_left_click = False
        should_double_click = False
        should_right_click = False

        # Right click: trigger on 3 touches, then reset
        if self.touch_count >= self.right_click_touches and self.touch_state == TouchState.IDLE:
            should_right_click = True
            self.touch_count = 0  # Reset after right click

        # Double click: trigger on 2 touches (but not 3+)
        elif self.touch_count == self.double_click_touches and self.touch_state == TouchState.IDLE:
            should_double_click = True
            self.touch_count = 0  # Reset after double click

        # Single click: trigger on 1 touch (but not 2+)
        elif self.touch_count == self.single_click_touches and self.touch_state == TouchState.IDLE:
            should_left_click = True
            self.touch_count = 0  # Reset after single click

        # --- Hand Closure Detection (Disabled for now) ---
        should_quit = False
        hand_closure = self._calculate_hand_closure(landmarks)
        # Fist gesture disabled - only 'Q' key quits
        # if hand_closure > self.closure_threshold:
        #     self.closure_frame_count += 1
        #     if self.closure_frame_count >= self.closure_hold_frames:
        #         should_quit = True
        #         self.closure_frame_count = 0
        # else:
        #     self.closure_frame_count = 0

        debug_info = {
            'touch_distance': touch_distance,
            'touch_count': self.touch_count,
            'touch_max': self.max_touch_count,
            'hand_closure': hand_closure,
            'closure_frames': self.closure_frame_count,
        }

        return GestureResult(
            hand_detected=True,
            cursor_position=(cursor_x, cursor_y),
            should_left_click=should_left_click,
            should_double_click=should_double_click,
            should_right_click=should_right_click,
            should_quit=should_quit,
            debug_info=debug_info
        )

    def _calculate_hand_closure(self, landmarks) -> float:
        """
        Calculate how closed the hand is (0 = open, 1 = closed fist).
        Measures how far all fingertips are from wrist center.
        """
        def get_landmark(idx):
            if hasattr(landmarks, 'landmark'):
                return landmarks.landmark[idx]
            else:
                return landmarks[idx]

        # Get wrist position (landmark 0)
        wrist = get_landmark(0)
        wrist_pos = Point2D(wrist.x, wrist.y)

        # Fingertip landmarks: 4=thumb, 8=index, 12=middle, 16=ring, 20=pinky
        fingertip_indices = [4, 8, 12, 16, 20]
        distances = []

        for idx in fingertip_indices:
            tip = get_landmark(idx)
            tip_pos = Point2D(tip.x, tip.y)
            dist = wrist_pos.distance_to(tip_pos)
            distances.append(dist)

        # Average distance from fingertips to wrist
        avg_distance = sum(distances) / len(distances)

        # Normalize: typical open hand ~0.3, closed fist ~0.1
        # Return inverted so closed = high value
        closure = 1.0 - min(avg_distance / 0.3, 1.0)

        return max(0, min(closure, 1.0))
