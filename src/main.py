import cv2
import time
import numpy as np
from src.gestures.detector import HandGestureDetector
from src.spotify.client import SpotifyClient
from src.config.settings import CAMERA_INDEX, VOLUME_STEP, TARGET_FPS

class SpotifyGestureController:
    def __init__(self):
        self.cap = cv2.VideoCapture(CAMERA_INDEX)
        
        # Set camera properties for higher FPS
        self.cap.set(cv2.CAP_PROP_FPS, TARGET_FPS)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        
        self.detector = HandGestureDetector()
        self.spotify = SpotifyClient()
        self.prev_time = 0
        self.current_time = 0
        self.prev_gesture = None
        self.gesture_cooldown = 1.0  # Cooldown in seconds to prevent multiple triggers
        self.last_action_time = 0
        self.current_track = None
        self.frame_count = 0
        self.fps_update_interval = 10  # Update FPS display every 10 frames
        self.fps = 0
        
    def display_track_info(self, img):
        if self.current_track:
            # Create a semi-transparent overlay for text background
            overlay = img.copy()
            cv2.rectangle(overlay, (5, 5), (350, 100), (0, 0, 0), -1)
            alpha = 0.7  # Transparency factor
            img = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)
            
            # Display track info on the image with better formatting
            cv2.putText(img, f"Track: {self.current_track['name']}", (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            cv2.putText(img, f"Artist: {self.current_track['artist']}", (10, 60), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            status = "Playing" if self.current_track['is_playing'] else "Paused"
            cv2.putText(img, f"Status: {status}", (10, 90), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        
    def process_gesture(self, gesture):
        current_time = time.time()
        
        # Check cooldown to prevent multiple triggers
        if current_time - self.last_action_time < self.gesture_cooldown:
            return
        
        # Process different gestures
        if gesture == "Play/Pause" and self.prev_gesture != "Play/Pause":
            current_track = self.spotify.get_current_track()
            if current_track and current_track['is_playing']:
                self.spotify.pause()
                print("Paused playback")
            else:
                self.spotify.play()
                print("Started playback")
            self.last_action_time = current_time
            
        elif gesture == "Next Track" and self.prev_gesture != "Next Track":
            self.spotify.next_track()
            print("Skipped to next track")
            self.last_action_time = current_time
            
        elif gesture == "Previous Track" and self.prev_gesture != "Previous Track":
            self.spotify.previous_track()
            print("Went to previous track")
            self.last_action_time = current_time
            
        elif gesture == "Volume Up" and self.prev_gesture != "Volume Up":
            self.spotify.increase_volume(VOLUME_STEP)
            print(f"Increased volume by {VOLUME_STEP}%")
            self.last_action_time = current_time
            
        elif gesture == "Volume Down" and self.prev_gesture != "Volume Down":
            self.spotify.decrease_volume(VOLUME_STEP)
            print(f"Decreased volume by {VOLUME_STEP}%")
            self.last_action_time = current_time
            
        self.prev_gesture = gesture
    
    def run(self):
        try:
            while True:
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
                    self.current_track = self.spotify.get_current_track()
                
                # Display track info
                self.display_track_info(img)
                
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
                
                # Create a semi-transparent overlay for text background
                h, w, c = img.shape
                overlay = img.copy()
                cv2.rectangle(overlay, (5, h-90), (350, h-5), (0, 0, 0), -1)
                alpha = 0.7  # Transparency factor
                img = cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0)
                
                # Display FPS and detected gesture with better formatting
                cv2.putText(img, f"FPS: {int(self.fps)}", (10, h-60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                cv2.putText(img, f"Gesture: {gesture}", (10, h-30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Display gesture instructions with better formatting
                instructions = [
                    "Peace Sign: Play/Pause",
                    "Thumb + Index: Next Track",
                    "Thumb + Pinky: Previous Track",
                    "All fingers except thumb: Volume Up",
                    "Only thumb up: Volume Down",
                    "Press 'q' to exit"
                ]
                
                # Create instruction background
                cv2.rectangle(img, (w-320, h-140), (w-10, h-10), (0, 0, 0), -1)
                cv2.rectangle(img, (w-320, h-140), (w-10, h-10), (255, 255, 255), 1)
                
                for i, instruction in enumerate(instructions):
                    cv2.putText(img, instruction, (w-310, h-110 + (i * 20)), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # Show the image
                cv2.imshow("Spotify Gesture Control", img)
                
                # Break the loop if 'q' is pressed - ensure this works properly
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    print("Exiting application...")
                    break
                
                # Control frame rate to target FPS
                frame_time = time.time() - frame_start_time
                wait_time = max(1, int((1.0/TARGET_FPS - frame_time) * 1000))
                cv2.waitKey(wait_time)
                    
        finally:
            print("Cleaning up resources...")
            self.cap.release()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    controller = SpotifyGestureController()
    controller.run()