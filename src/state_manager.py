"""
State management for gesture detection.
Note: Now mostly a stub since wiggle detection handles its own state/cooldowns.
"""

import time
from typing import Dict, Any


class GestureStateManager:
    """
    Minimal state manager for gesture detection.
    Wiggle detection now handles its own state tracking and cooldowns.
    """

    def __init__(self, config: dict):
        self.config = config
        pass

    def reset_calibration(self):
        """Reset state (called when hand is lost and re-detected)."""
        pass

    def get_debug_info(self) -> Dict[str, Any]:
        """Return current state information for debugging."""
        return {}
