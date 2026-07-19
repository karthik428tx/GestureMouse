# Debugging Wiggle Detection

If thumb/pinky wiggles aren't being detected, use this debug script to test and tune.

## Quick Test

```bash
python debug_wiggles.py
```

This will:
1. Open camera feed
2. Display wiggle counts in real-time
3. Show which threshold reached for clicks
4. Track maximum wiggles detected

## What to Look For

- **Thumb/Pinky history**: Should build up to 30 frames as you hold your hand steady
- **Wiggle count**: Should increase when you move finger back and forth
- **Click detection**: Should trigger when reaching threshold (2 or 4)

## If Wiggles Aren't Detected

### Step 1: Check Movement Detection
- Move your finger slowly back and forth
- Watch if the "history" counter goes up
- If history stays at 0-5, the hand isn't being detected or movement is too small

### Step 2: Adjust Threshold
Edit `config.yaml` and try lower values:

```yaml
wiggle_detection:
  threshold_pixels: 8   # Current (was 15)
  # Try these if still not working:
  # threshold_pixels: 5  # Very sensitive
  # threshold_pixels: 3  # Ultra sensitive
```

Lower threshold = more sensitive to small movements

### Step 3: Test Again
```bash
python debug_wiggles.py
```

Try wiggles with:
- **Small movements**: Just moving finger left-right slightly
- **Large movements**: Full hand wiggle
- **Different speeds**: Slow vs fast wiggles

## Understanding Wiggle Counting

A "wiggle" is counted when:
1. Finger moves beyond threshold distance
2. Direction changes significantly (60° angle)
3. Back-and-forth motion = 1 complete wiggle (2 direction changes)

**Example:**
- Slow left-right wiggle = 1 wiggle per cycle
- Fast shaking = Multiple wiggles per second

## Optimal Settings

**For small, precise wiggles:**
```yaml
threshold_pixels: 5
single_click_wiggles: 2
double_click_wiggles: 4
```

**For large, obvious wiggles:**
```yaml
threshold_pixels: 10
single_click_wiggles: 1
double_click_wiggles: 2
```

**For medium wiggles (default):**
```yaml
threshold_pixels: 8
single_click_wiggles: 2
double_click_wiggles: 4
```

## Tips

1. **Make sure hand is detected first** - Check "HAND: YES" displays
2. **Wiggle perpendicular to camera** - Wiggle in/out or left/right, not rotation
3. **Keep index finger extended** - Gesture requires index pointing
4. **Be consistent** - Same wiggle size = reliable detection
5. **Give it space** - Don't block with other fingers

## Still Having Issues?

Try extreme values to understand the system:

```yaml
threshold_pixels: 2    # Ultra sensitive (may have false positives)
single_click_wiggles: 1
double_click_wiggles: 2
```

Run `python debug_wiggles.py` and wiggle slowly. You should see very high wiggle counts (10+).

If counts are still 0, the issue is likely:
- Hand detection failing (camera issue)
- Position history not being populated
- Algorithm bug (report with debug output)

---

**Run the debug script, watch the numbers, and adjust `threshold_pixels` until it works for your hand size and movement style.**
