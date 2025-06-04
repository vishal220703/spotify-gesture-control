from flask import Flask, render_template, Response, jsonify
from flask_socketio import SocketIO
import cv2
import threading
import time
import sys
import os

# Add the parent directory to the path so we can import our existing modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.gestures.detector import HandGestureDetector
from src.spotify.client import SpotifyClient
from src.config.settings import CAMERA_INDEX, VOLUME_STEP, TARGET_FPS

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables
frame_buffer = None
frame_lock = threading.Lock()
current_gesture = "No Gesture"
spotify_client = SpotifyClient()
current_track = None
running = True

class WebGestureController:
    # In the WebGestureController.__init__ method, add these lines:
    def __init__(self):
        import logging
        logging.info(f"Initializing camera with index {CAMERA_INDEX}")
        self.cap = cv2.VideoCapture(CAMERA_INDEX)
        
        if not self.cap.isOpened():
            logging.error(f"Failed to open camera with index {CAMERA_INDEX}")
        else:
            logging.info(f"Successfully opened camera with index {CAMERA_INDEX}")
        
        # Set camera properties for higher FPS
        self.cap.set(cv2.CAP_PROP_FPS, TARGET_FPS)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        
        self.detector = HandGestureDetector()
        self.prev_time = 0
        self.current_time = 0
        self.prev_gesture = None
        self.gesture_cooldown = 1.0  # Cooldown in seconds to prevent multiple triggers
        self.last_action_time = 0
        self.frame_count = 0
        self.fps_update_interval = 10
        self.fps = 0
    
    def process_gesture(self, gesture):
        global current_gesture, current_track
        current_time = time.time()
        
        # Update the current gesture for the web interface
        current_gesture = gesture
        
        # Check cooldown to prevent multiple triggers
        if current_time - self.last_action_time < self.gesture_cooldown:
            return
        
        # Process different gestures
        if gesture == "Play/Pause" and self.prev_gesture != "Play/Pause":
            track = spotify_client.get_current_track()
            if track and track['is_playing']:
                spotify_client.pause()
                print("Paused playback")
            else:
                spotify_client.play()
                print("Started playback")
            self.last_action_time = current_time
            
        elif gesture == "Next Track" and self.prev_gesture != "Next Track":
            spotify_client.next_track()
            print("Skipped to next track")
            self.last_action_time = current_time
            
        elif gesture == "Previous Track" and self.prev_gesture != "Previous Track":
            spotify_client.previous_track()
            print("Went to previous track")
            self.last_action_time = current_time
            
        elif gesture == "Volume Up" and self.prev_gesture != "Volume Up":
            spotify_client.increase_volume(VOLUME_STEP)
            print(f"Increased volume by {VOLUME_STEP}%")
            self.last_action_time = current_time
            
        elif gesture == "Volume Down" and self.prev_gesture != "Volume Down":
            spotify_client.decrease_volume(VOLUME_STEP)
            print(f"Decreased volume by {VOLUME_STEP}%")
            self.last_action_time = current_time
            
        self.prev_gesture = gesture
        
        # Update track info after action
        current_track = spotify_client.get_current_track()
    
    def run(self):
        global frame_buffer, current_track, running
        
        try:
            while running:
                # Calculate time for frame rate control
                frame_start_time = time.time()
                
                success, img = self.cap.read()
                if not success:
                    print("Failed to capture image from camera")
                    break
                    
                # Find hands and get landmarks
                img = self.detector.find_hands(img)
                landmark_list = self.detector.find_position(img)
                
                # Get gesture and process it
                gesture = self.detector.get_gesture(landmark_list)
                
                # Update current track info periodically
                if time.time() % 5 < 0.1:  # Update roughly every 5 seconds
                    current_track = spotify_client.get_current_track()
                    # Emit track info to web clients
                    if current_track:
                        socketio.emit('track_update', current_track)
                
                # Process the detected gesture
                if gesture != "No Hand" and gesture != "Unknown Gesture":
                    self.process_gesture(gesture)
                
                # Calculate and update FPS
                self.current_time = time.time()
                self.frame_count += 1
                
                if self.frame_count >= self.fps_update_interval:
                    self.fps = self.fps_update_interval / (self.current_time - self.prev_time) if (self.current_time - self.prev_time) > 0 else 0
                    self.prev_time = self.current_time
                    self.frame_count = 0
                    # Emit FPS to web clients
                    socketio.emit('fps_update', {'fps': int(self.fps)})
                
                # Add FPS and gesture text to the image
                cv2.putText(img, f"FPS: {int(self.fps)}", (10, 30), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(img, f"Gesture: {gesture}", (10, 60), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                # Update the frame buffer with lock to prevent race conditions
                _, buffer = cv2.imencode('.jpg', img)
                with frame_lock:
                    frame_buffer = buffer.tobytes()
                
                # Emit gesture update to web clients
                socketio.emit('gesture_update', {'gesture': gesture})
                
                # Control frame rate
                frame_time = time.time() - frame_start_time
                wait_time = max(0.001, (1.0/TARGET_FPS - frame_time))
                time.sleep(wait_time)
                
        finally:
            self.cap.release()

def generate_frames():
    """Generate frames for the video feed"""
    while True:
        with frame_lock:
            if frame_buffer is not None:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_buffer + b'\r\n')
        time.sleep(1/TARGET_FPS)  # Match the target FPS

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_track_info')
def get_track_info():
    """Get current track information"""
    global current_track
    if current_track:
        return jsonify(current_track)
    return jsonify({"error": "No track playing"})

@app.route('/get_gesture')
def get_gesture():
    """Get current detected gesture"""
    global current_gesture
    return jsonify({"gesture": current_gesture})

@app.route('/control/<action>')
def control_spotify(action):
    """Control Spotify playback"""
    if action == "play":
        spotify_client.play()
        return jsonify({"status": "success", "action": "play"})
    elif action == "pause":
        spotify_client.pause()
        return jsonify({"status": "success", "action": "pause"})
    elif action == "next":
        spotify_client.next_track()
        return jsonify({"status": "success", "action": "next"})
    elif action == "previous":
        spotify_client.previous_track()
        return jsonify({"status": "success", "action": "previous"})
    elif action == "volume_up":
        spotify_client.increase_volume(VOLUME_STEP)
        return jsonify({"status": "success", "action": "volume_up"})
    elif action == "volume_down":
        spotify_client.decrease_volume(VOLUME_STEP)
        return jsonify({"status": "success", "action": "volume_down"})
    return jsonify({"status": "error", "message": "Invalid action"})

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@app.route('/exit')
def exit_application():
    """Exit the application"""
    global running
    running = False
    
    # Use a thread to shutdown the server after sending the response
    def shutdown_server():
        import logging
        logging.info("Shutting down server...")
        time.sleep(1)  # Give time for the response to be sent
        os._exit(0)  # Force exit the application
    
    threading.Thread(target=shutdown_server).start()
    return jsonify({"status": "success", "message": "Application shutting down"})

def start_gesture_controller():
    """Start the gesture controller in a separate thread"""
    controller = WebGestureController()
    controller.run()

if __name__ == '__main__':
    # Start the gesture controller in a separate thread
    gesture_thread = threading.Thread(target=start_gesture_controller)
    gesture_thread.daemon = True
    gesture_thread.start()
    
    # Start the Flask app
    socketio.run(app, host='127.0.0.1', port=5000, debug=False)