import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Spotify API credentials
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

# Gesture recognition settings
CAMERA_INDEX = 0  # Default camera (usually webcam)
DETECTION_CONFIDENCE = 0.8  # Increased from 0.7 for better accuracy
TRACKING_CONFIDENCE = 0.8  # Increased from 0.7 for better accuracy
GESTURE_SMOOTHING_FRAMES = 5  # Number of frames to smooth gesture detection

# Volume control settings
VOLUME_STEP = 5  # Percentage to increase/decrease volume

# FPS settings
TARGET_FPS = 60  # Target frames per second