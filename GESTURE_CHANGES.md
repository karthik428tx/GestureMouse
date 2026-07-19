# Gesture Control Changes - Press-Based System

## Summary
The gesture detection system has been redesigned to use **finger pressing** (like pressing a button) instead of wiggling or pinching.

## New Gesture Controls

### 1. **Cursor Movement** (Unchanged)
- **Gesture**: Point index finger
- **Result**: Move mouse cursor to finger position

### 2. **Single Left Click** (NEW)
- **Gesture**: Press thumb down once (like clicking a button)
- **Result**: Single left mouse click
- **Cooldown**: 300ms

### 3. **Double Left Click** (NEW)
- **Gesture**: Press thumb down twice (two separate press cycles)
- **Result**: Double left mouse click
- **Cooldown**: 300ms

### 4. **Right Click** (NEW)
- **Gesture**: Press pinky finger down (like clicking a button)
- **Result**: Right mouse click
- **Cooldown**: 500ms

## How It Works

The system tracks the **vertical position (Y coordinate)** of your fingers:

1. **Idle**: Finger at resting position
2. **Press**: Finger moves down by `press_threshold_pixels` (15px default)
3. **Release**: Finger moves back up by `release_threshold_pixels` (10px default)
4. **Click**: When you complete a press cycle, a click is registered

### Example:
```
Thumb position:  Press down 15px → Release up 10px → Click registered!
                 [DOWN]          [UP]              [CLICK]
```

## Configuration

File: `config.yaml`

```yaml
gestures:
  left_click:
    thumb_landmark: 4  # Thumb tip
    index_landmark: 8  # Index finger tip
    press_detection:
      press_threshold_pixels: 15  # How far down to register press
      release_threshold_pixels: 10  # How far up to register release
      single_click_presses: 1  # 1 press = single click
      double_click_presses: 2  # 2 presses = double click
      cooldown_ms: 300

  right_click:
    pinky_landmark: 20  # Pinky tip
    press_detection:
      press_threshold_pixels: 15
      release_threshold_pixels: 10
      cooldown_ms: 500
```

## Tuning Guide

### If presses aren't being detected:

**Increase thresholds:**
```yaml
press_threshold_pixels: 20  # Require bigger press
release_threshold_pixels: 15
```

### If presses are too sensitive:

**Decrease thresholds:**
```yaml
press_threshold_pixels: 10  # Easier to trigger
release_threshold_pixels: 8
```

### If accidental clicks happen:

**Increase cooldown:**
```yaml
cooldown_ms: 500  # Wait longer between clicks
```

## Technical Details

### Press State Machine
```
IDLE ──[press]──> PRESSED ──[release]──> RELEASED ──[reset]──> IDLE
                                           ↓
                                      [CLICK]
```

### Coordinate System
- Y increases downward (camera coordinates)
- Pressing down = Y increases
- Releasing up = Y decreases

## Removed Features
- ❌ Wiggle detection
- ❌ Pinch detection
- ❌ Palm twist detection
- ❌ Palm calibration

## Modified Files

1. **config.yaml** - Press detection parameters
2. **src/gesture_detector.py** - New press-based algorithm
3. **src/visualizer.py** - Shows press counts instead of wiggles
4. **main.py** - Updated control instructions

## Testing

Run with display to see press counts in real-time:
```bash
python main.py
```

Shows:
- Current press count
- Maximum presses detected
- Click feedback (LEFT/DOUBLE/RIGHT CLICK)

---

**Version**: 3.0 - Press-based gestures  
**Date**: 2026-07-19
