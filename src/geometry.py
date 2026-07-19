"""
Geometry utilities for hand landmark calculations.
"""

import math
from typing import Tuple
from dataclasses import dataclass


@dataclass
class Point2D:
    x: float
    y: float
    
    def distance_to(self, other: 'Point2D') -> float:
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def to_tuple(self) -> Tuple[float, float]:
        return (self.x, self.y)


@dataclass  
class Point3D:
    x: float
    y: float
    z: float
    
    def distance_to(self, other: 'Point3D') -> float:
        return math.sqrt(
            (self.x - other.x)**2 + 
            (self.y - other.y)**2 + 
            (self.z - other.z)**2
        )
    
    def project_2d(self) -> Point2D:
        return Point2D(self.x, self.y)


def calculate_angle(p1: Point2D, p2: Point2D, p3: Point2D) -> float:
    """
    Calculate angle at p2 formed by p1-p2-p3.
    Returns angle in degrees.
    """
    v1 = Point2D(p1.x - p2.x, p1.y - p2.y)
    v2 = Point2D(p3.x - p2.x, p3.y - p2.y)
    
    dot = v1.x * v2.x + v1.y * v2.y
    mag1 = math.sqrt(v1.x**2 + v1.y**2)
    mag2 = math.sqrt(v2.x**2 + v2.y**2)
    
    if mag1 * mag2 == 0:
        return 0.0
    
    cos_angle = max(-1, min(1, dot / (mag1 * mag2)))
    return math.degrees(math.acos(cos_angle))


def calculate_palm_tilt_angle(wrist: Point2D, index_mcp: Point2D, 
                               pinky_mcp: Point2D) -> float:
    """
    Calculate the tilt angle of the palm.
    
    Uses the line from index MCP to pinky MCP (across the knuckles).
    Returns angle in degrees where:
    - 0° = horizontal (pinky to the right of index)
    - 90° = vertical (pinky above index)
    - -90° = vertical (pinky below index)
    
    For RIGHT hand in mirrored view:
    - Neutral palm: ~0° to 10° (slightly tilted)
    - Palm twisted right: ~-70° to -90° (pinky drops below index)
    """
    dx = pinky_mcp.x - index_mcp.x
    dy = pinky_mcp.y - index_mcp.y
    return math.degrees(math.atan2(dy, dx))


def map_coordinates(normalized_x: float, normalized_y: float,
                    screen_width: int, screen_height: int,
                    mirror_x: bool = True) -> Tuple[float, float]:
    """
    Map normalized coordinates (0-1) to screen coordinates.
    
    Args:
        normalized_x: X position from MediaPipe (0=left, 1=right)
        normalized_y: Y position from MediaPipe (0=top, 1=bottom)
        screen_width: Screen width in pixels
        screen_height: Screen height in pixels
        mirror_x: If True, flip X axis for natural mirror behavior
    
    Returns:
        Tuple of (screen_x, screen_y) in pixels
    """
    if mirror_x:
        screen_x = (1 - normalized_x) * screen_width
    else:
        screen_x = normalized_x * screen_width
    
    screen_y = normalized_y * screen_height
    
    return screen_x, screen_y


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp value between min and max."""
    return max(min_val, min(max_val, value))