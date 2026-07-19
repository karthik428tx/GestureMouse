"""
Smoothing filters for cursor movement.
"""

import math
from typing import Tuple


class EMASmoother:
    """Exponential Moving Average filter."""
    
    def __init__(self, alpha: float = 0.35):
        """
        Args:
            alpha: Smoothing factor (0-1). Lower = smoother but slower.
        """
        self.alpha = alpha
        self.initialized = False
        self.smoothed_x = 0.0
        self.smoothed_y = 0.0
    
    def smooth(self, x: float, y: float) -> Tuple[float, float]:
        if not self.initialized:
            self.smoothed_x = x
            self.smoothed_y = y
            self.initialized = True
        else:
            self.smoothed_x = self.alpha * x + (1 - self.alpha) * self.smoothed_x
            self.smoothed_y = self.alpha * y + (1 - self.alpha) * self.smoothed_y
        return self.smoothed_x, self.smoothed_y
    
    def reset(self):
        self.initialized = False


class OneEuroFilter:
    """
    1-Euro Filter - adaptive smoothing based on signal velocity.
    Better than EMA for cursor control as it reduces jitter while
    maintaining responsiveness during fast movements.
    
    Reference: https://cristal.univ-lille.fr/~casiez/1euro/
    """
    
    def __init__(self, min_cutoff: float = 0.001, beta: float = 0.4, 
                 d_cutoff: float = 1.0):
        """
        Args:
            min_cutoff: Minimum cutoff frequency (lower = smoother)
            beta: Speed coefficient (higher = more responsive to fast movement)
            d_cutoff: Derivative cutoff frequency
        """
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff
        
        # Previous values
        self.prev_x = None
        self.prev_y = None
        self.prev_dx = 0.0
        self.prev_dy = 0.0
        self.prev_timestamp = None
    
    def _smooth_axis(self, value: float, prev_value: float, 
                     prev_derivative: float, timestamp: float) -> Tuple[float, float]:
        """Smooth a single axis."""
        if prev_value is None:
            return value, 0.0
        
        # Calculate time delta
        if self.prev_timestamp is None:
            dt = 0.016  # Assume ~60fps
        else:
            dt = timestamp - self.prev_timestamp
            dt = max(dt, 0.001)  # Prevent division by zero
        
        # Calculate derivative (velocity)
        derivative = (value - prev_value) / dt
        
        # Smooth the derivative
        alpha_d = 1.0 if self.d_cutoff == 0 else self._alpha(dt, self.d_cutoff)
        smoothed_derivative = alpha_d * derivative + (1 - alpha_d) * prev_derivative
        
        # Calculate adaptive cutoff
        cutoff = self.min_cutoff + self.beta * abs(smoothed_derivative)
        
        # Smooth the value
        alpha = self._alpha(dt, cutoff)
        smoothed_value = alpha * value + (1 - alpha) * prev_value
        
        return smoothed_value, smoothed_derivative
    
    def _alpha(self, dt: float, cutoff: float) -> float:
        """Calculate smoothing coefficient."""
        tau = 1.0 / (2 * math.pi * cutoff)
        return 1.0 / (1.0 + tau / dt)
    
    def smooth(self, x: float, y: float, timestamp: float = None) -> Tuple[float, float]:
        """Smooth x, y coordinates."""
        if timestamp is None:
            import time
            timestamp = time.time()
        
        smoothed_x, dx = self._smooth_axis(x, self.prev_x, self.prev_dx, timestamp)
        smoothed_y, dy = self._smooth_axis(y, self.prev_y, self.prev_dy, timestamp)
        
        self.prev_x = smoothed_x
        self.prev_y = smoothed_y
        self.prev_dx = dx
        self.prev_dy = dy
        self.prev_timestamp = timestamp
        
        return smoothed_x, smoothed_y
    
    def reset(self):
        self.prev_x = None
        self.prev_y = None
        self.prev_dx = 0.0
        self.prev_dy = 0.0
        self.prev_timestamp = None


def create_smoother(config: dict):
    """Factory function to create smoother based on config."""
    smoothing_config = config['gestures']['cursor']['smoothing']
    
    if smoothing_config['type'] == 'one_euro':
        one_euro_config = smoothing_config['one_euro']
        return OneEuroFilter(
            min_cutoff=one_euro_config['min_cutoff'],
            beta=one_euro_config['beta']
        )
    else:  # EMA
        return EMASmoother(alpha=smoothing_config['ema_alpha'])