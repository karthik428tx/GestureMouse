"""
Mouse control wrapper using PyAutoGUI.
"""

import pyautogui
import time


class MouseController:
    """Controls mouse cursor and clicks."""
    
    # PyAutoGUI safety settings
    pyautogui.PAUSE = 0.001  # Min pause between actions
    pyautogui.FAILSAFE = True  # Move mouse to corner to abort
    
    def __init__(self, config: dict):
        self.config = config
        self.screen_width, self.screen_height = pyautogui.size()
        
        # Track last position to avoid unnecessary moves
        self.last_x = None
        self.last_y = None
        
        # Minimum movement threshold (pixels)
        self.move_threshold = config['gestures']['cursor']['dead_zone_pixels']
    
    def move_to(self, x: float, y: float):
        """
        Move mouse to position.
        
        Args:
            x: X coordinate in screen pixels
            y: Y coordinate in screen pixels
        """
        # Round to integers
        target_x = int(round(x))
        target_y = int(round(y))
        
        # Skip if position hasn't changed significantly
        if self.last_x is not None:
            dx = abs(target_x - self.last_x)
            dy = abs(target_y - self.last_y)
            if dx < self.move_threshold and dy < self.move_threshold:
                return
        
        # Clamp to screen bounds
        target_x = max(0, min(target_x, self.screen_width - 1))
        target_y = max(0, min(target_y, self.screen_height - 1))
        
        pyautogui.moveTo(target_x, target_y, duration=0)
        self.last_x = target_x
        self.last_y = target_y
    
    def left_click(self):
        """Perform left mouse click."""
        pyautogui.click(button='left')
        print(f"[{time.time():.3f}] Left click")

    def double_click(self):
        """Perform double left mouse click."""
        pyautogui.click(button='left', clicks=2, interval=0.1)
        print(f"[{time.time():.3f}] Double click")

    def right_click(self):
        """Perform right mouse click."""
        pyautogui.click(button='right')
        print(f"[{time.time():.3f}] Right click")
    
    def get_screen_size(self) -> tuple:
        """Return screen dimensions."""
        return self.screen_width, self.screen_height