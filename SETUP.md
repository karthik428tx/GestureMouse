# Gesture Mouse Control - Setup Guide

## Problem: MediaPipe Model Not Available

Your environment has MediaPipe installed (v0.10.35), but the hand landmark model file is missing.

## Solution: Download the Model

### Option 1: Automatic Download (Recommended)
```bash
python download_models.py
```

### Option 2: Manual Download

1. Download the model file from:
   - URL: `https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker.task`
   - Alternative: Search "MediaPipe hand_landmarker.task" online

2. Place the file in the project root directory:
   ```
   D:\Gesture\hand_landmarker.task
   ```

3. Run the app:
   ```bash
   python main.py
   ```

### Option 3: Use Browser Download
If programmatic download fails due to network restrictions:

1. Open this URL in your browser:
   ```
   https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker.task
   ```

2. The file (~27 MB) will download

3. Move it to: `D:\Gesture\hand_landmarker.task`

4. Run:
   ```bash
   python main.py
   ```

## Verify Setup

After obtaining the model file, verify it's in the correct location:

```powershell
Test-Path D:\Gesture\hand_landmarker.task
```

Should return `True`.

## Run the Application

Once the model is in place:

```bash
# With display
python main.py

# Headless mode (no window)
python main.py --no-display

# With custom config
python main.py --config my_config.yaml
```

## Controls

- **Move cursor**: Point with index finger
- **Left click**: Pinch thumb + index finger
- **Right click**: Twist palm right ~90°
- **Quit**: Press Q or ESC

## Troubleshooting

If download still fails:
1. Check internet connection
2. Verify firewall isn't blocking Google Storage
3. Try from a different network
4. Download manually via browser (Option 3 above)

---

**File Size**: ~27 MB  
**Download Time**: 30 seconds - 2 minutes (depends on connection)
