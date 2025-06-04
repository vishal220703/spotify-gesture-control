# Spotify Gesture Control

![wmremove-transformed](https://github.com/user-attachments/assets/078ca176-27c0-4c58-af2c-5d1197bceddd)
![image](https://github.com/user-attachments/assets/d74c7aff-8beb-4dc7-93a6-3b611e36cd3d)


## Overview

Spotify Gesture Control is an innovative application that allows users to control their Spotify playback using hand gestures captured through a webcam. This project combines computer vision, gesture recognition, and the Spotify API to create a hands-free music control experience.

## Features

- **Gesture Recognition**: Control Spotify without touching your keyboard or mouse
- **Real-time Feedback**: See your gestures recognized in real-time
- **Web Interface**: User-friendly web interface showing current track and playback status
- **Multiple Control Options**: Play/pause, skip tracks, adjust volume with different hand gestures

## Gestures

| Gesture | Action |
|---------|--------|
| Peace Sign (Index + Middle fingers up) | Play/Pause |
| Thumb + Index up | Next Track |
| Thumb + Pinky up | Previous Track |
| All fingers except thumb up | Volume Up |
| Only thumb up | Volume Down |

## Technologies Used

- **Python**: Core programming language
- **OpenCV**: Computer vision for camera access and image processing
- **MediaPipe**: Hand tracking and gesture recognition
- **Flask**: Web server framework
- **Socket.IO**: Real-time communication between server and web client
- **Spotipy**: Python library for Spotify Web API

## Installation

### Prerequisites

- Python 3.8 or higher
- Spotify Premium account
- Webcam
- Spotify Developer account and API credentials

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/vishal220703/spotify-gesture-control.git
   cd spotify-gesture-control
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a .env file in the project root with your Spotify API credentials:
   SPOTIFY_CLIENT_ID=your_client_id
   SPOTIFY_CLIENT_SECRET=your_client_secret
   SPOTIFY_REDIRECT_URI=http://127.0.0.1:8888/callback
4. Register your app in the Spotify Developer Dashboard and add the redirect URI.

## Usage
1. Start the web application:
   ```bash
   python web_app.py
   ```
2. A browser window will automatically open to http://127.0.0.1:5000
3. Grant permission to access your webcam when prompted
4. Use the gestures shown in the interface to control your Spotify playback
