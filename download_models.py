#!/usr/bin/env python3
"""Download MediaPipe models required for hand tracking."""

import os
import urllib.request
import sys

def download_with_progress(url, destination):
    """Download a file from URL to destination with progress."""
    print(f"\nDownloading from: {url}")
    try:
        def progress_hook(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(downloaded * 100 // total_size, 100)
                mb_downloaded = downloaded / (1024 * 1024)
                mb_total = total_size / (1024 * 1024)
                print(f"\rProgress: {percent}% ({mb_downloaded:.1f}MB / {mb_total:.1f}MB)", end="")

        urllib.request.urlretrieve(url, destination, reporthook=progress_hook)
        print(f"\n[OK] Downloaded successfully!")
        return True
    except Exception as e:
        print(f"\n[ERROR] Download failed: {e}")
        return False

def main():
    models_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(models_dir, "hand_landmarker.task")

    if os.path.exists(model_path):
        size_mb = os.path.getsize(model_path) / (1024 * 1024)
        print(f"[OK] Model already exists at {model_path} ({size_mb:.1f}MB)")
        return 0

    print("=" * 60)
    print("MediaPipe Hand Landmark Model Downloader")
    print("=" * 60)

    # Try multiple sources
    urls = [
        "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker.task",
    ]

    for url in urls:
        if download_with_progress(url, model_path):
            print("\n" + "=" * 60)
            print("Setup complete!")
            print(f"Model saved to: {model_path}")
            print("\nYou can now run:")
            print("  python main.py")
            print("=" * 60)
            return 0

        # Clean up failed download
        if os.path.exists(model_path):
            os.remove(model_path)

    # If all downloads fail
    print("\n" + "=" * 60)
    print("[ERROR] Failed to download model")
    print("=" * 60)
    print("\nPlease try one of the following:")
    print("1. Check your internet connection and try again")
    print("2. Download manually from:")
    print("   https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker.task")
    print(f"3. Save the file to: {model_path}")
    print("\nOr try running this script again:")
    print("   python download_models.py")
    return 1

if __name__ == '__main__':
    sys.exit(main())
