"""
MediaPipe hand tracking wrapper.
"""

import cv2
import mediapipe as mp
from mediapipe.tasks.python import vision
from typing import Optional
import os
import urllib.request


class HandTracker:
    """Wraps MediaPipe Hands for simplified hand detection."""

    def __init__(self, config: dict):
        self.config = config
        hand_config = config['hand']

        # Get model path (download if necessary)
        model_path = self._get_model()

        # Create hand landmarker with new API
        options = vision.HandLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(
                model_asset_path=model_path
            ),
            running_mode=vision.RunningMode.IMAGE,
            num_hands=hand_config['max_num_hands'],
            min_hand_detection_confidence=hand_config['detection_confidence'],
            min_hand_presence_confidence=hand_config['tracking_confidence']
        )
        self.landmarker = vision.HandLandmarker.create_from_options(options)

    def _get_model(self):
        """Get or download the hand landmarker model."""
        # Check possible locations
        possible_paths = [
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'hand_landmarker.task'),
            os.path.expanduser('~/.mediapipe/hand_landmarker.task'),
            os.path.expanduser('~/Downloads/hand_landmarker.task'),
        ]

        for path in possible_paths:
            if os.path.exists(path):
                print(f"Found model at: {path}")
                return path

        # Download model to project root
        model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'hand_landmarker.task')
        os.makedirs(os.path.dirname(model_path), exist_ok=True)

        print(f"Downloading hand landmark model (this may take a moment)...")

        # Try multiple sources
        urls = [
            "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker.task",
            "https://download.tensorflow.org/models/mediapipe/hand_landmarker.task",
        ]

        for url in urls:
            try:
                print(f"Trying: {url}")
                urllib.request.urlretrieve(url, model_path, reporthook=self._download_progress)
                print(f"\nModel downloaded successfully!")
                return model_path
            except Exception as e:
                print(f"Failed: {e}")
                if os.path.exists(model_path):
                    os.remove(model_path)

        # If all downloads fail, provide instructions
        raise RuntimeError(
            f"\n{'='*70}\n"
            f"ERROR: Hand Landmark Model Not Found\n"
            f"{'='*70}\n\n"
            f"The MediaPipe hand landmark model file is missing.\n\n"
            f"Please follow these steps to set up the model:\n\n"
            f"1. Read: {os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'SETUP.md')}\n\n"
            f"2. Option A - Automatic download:\n"
            f"   python download_models.py\n\n"
            f"3. Option B - Manual download:\n"
            f"   Download from: https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker.task\n"
            f"   Save to: {model_path}\n\n"
            f"4. Then run:\n"
            f"   python main.py\n\n"
            f"{'='*70}\n"
        )

    @staticmethod
    def _download_progress(block_num, block_size, total_size):
        """Show download progress."""
        downloaded = block_num * block_size
        if total_size > 0:
            percent = min(downloaded * 100 // total_size, 100)
            print(f"\rDownload: {percent}%", end="")

    def process(self, frame) -> Optional[object]:
        """
        Process a frame and return hand landmarks.

        Args:
            frame: BGR image from OpenCV

        Returns:
            MediaPipe hand landmarks object or None if no hand detected
        """
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Create MediaPipe Image
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        # Detect hand landmarks
        detection_result = self.landmarker.detect(mp_image)

        if detection_result.hand_landmarks:
            return detection_result.hand_landmarks[0]

        return None

    def release(self):
        """Release resources."""
        pass