import cv2
import mediapipe as mp
import numpy as np
from collections import deque
from src.config.settings import DETECTION_CONFIDENCE, TRACKING_CONFIDENCE, GESTURE_SMOOTHING_FRAMES

class HandGestureDetector:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=DETECTION_CONFIDENCE,
            min_tracking_confidence=TRACKING_CONFIDENCE,
            model_complexity=1  # Use more complex model for better accuracy
        )
        self.mp_draw = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        # Gesture smoothing
        self.gesture_history = deque(maxlen=GESTURE_SMOOTHING_FRAMES)
        self.last_gesture = "No Hand"
        
    def find_hands(self, img, draw=True):
        # Convert BGR image to RGB
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        
        # Process the image and find hands
        self.results = self.hands.process(img_rgb)
        
        if self.results.multi_hand_landmarks:
            for hand_landmarks in self.results.multi_hand_landmarks:
                if draw:
                    # Enhanced visualization with different colors for connections
                    self.mp_draw.draw_landmarks(
                        img, 
                        hand_landmarks, 
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing_styles.get_default_hand_landmarks_style(),
                        self.mp_drawing_styles.get_default_hand_connections_style()
                    )
        
        return img
    
    def find_position(self, img, hand_no=0):
        landmark_list = []
        
        if self.results.multi_hand_landmarks:
            if len(self.results.multi_hand_landmarks) > hand_no:
                my_hand = self.results.multi_hand_landmarks[hand_no]
                
                for id, lm in enumerate(my_hand.landmark):
                    h, w, c = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    landmark_list.append([id, cx, cy])
                
                # Determine if this is a left or right hand
                if self.results.multi_handedness:
                    handedness = self.results.multi_handedness[hand_no].classification[0].label
                    landmark_list.append(["handedness", handedness])
        
        return landmark_list
    
    def get_gesture(self, landmark_list):
        if not landmark_list:
            self.gesture_history.append("No Hand")
            return self._smooth_gesture("No Hand")
        
        # Get fingertips (landmarks 4, 8, 12, 16, 20)
        # Thumb, Index, Middle, Ring, Pinky
        fingertips = [4, 8, 12, 16, 20]
        finger_bases = [2, 5, 9, 13, 17]  # Base points for comparison
        finger_mids = [3, 6, 10, 14, 18]  # Middle joints for better accuracy
        
        # Check if fingers are up or down
        fingers_up = []
        
        # Check handedness if available
        handedness = "Right"
        for point in landmark_list:
            if isinstance(point[0], str) and point[0] == "handedness":
                handedness = point[1]
                break
        
        # Special case for thumb based on handedness
        if handedness == "Right":
            # For right hand, thumb is up if it's to the left of the base
            if landmark_list[fingertips[0]][1] < landmark_list[finger_bases[0]][1]:
                fingers_up.append(1)
            else:
                fingers_up.append(0)
        else:  # Left hand
            # For left hand, thumb is up if it's to the right of the base
            if landmark_list[fingertips[0]][1] > landmark_list[finger_bases[0]][1]:
                fingers_up.append(1)
            else:
                fingers_up.append(0)
        
        # For other fingers (vertical comparison with additional check)
        for i in range(1, 5):
            # Primary check: fingertip is above base
            primary_check = landmark_list[fingertips[i]][2] < landmark_list[finger_bases[i]][2]
            
            # Secondary check: middle joint is above base (for bent fingers)
            secondary_check = landmark_list[finger_mids[i]][2] < landmark_list[finger_bases[i]][2]
            
            # A finger is considered up if the fingertip is above the base
            # and the middle joint is in a reasonable position
            if primary_check and (secondary_check or 
                                 abs(landmark_list[finger_mids[i]][2] - landmark_list[finger_bases[i]][2]) < 20):
                fingers_up.append(1)  # Finger is up
            else:
                fingers_up.append(0)  # Finger is down
        
        # Recognize gestures based on finger positions
        gesture = "Unknown Gesture"
        
        if sum(fingers_up) == 0:  # All fingers down
            gesture = "Fist"
        elif sum(fingers_up) == 5:  # All fingers up
            gesture = "Open Hand"
        elif fingers_up == [0, 1, 0, 0, 0]:  # Only index finger up
            gesture = "Point"
        elif fingers_up == [0, 1, 1, 0, 0]:  # Index and middle fingers up (peace sign)
            gesture = "Play/Pause"
        elif fingers_up == [1, 1, 0, 0, 0]:  # Thumb and index up
            gesture = "Next Track"
        elif fingers_up == [1, 0, 0, 0, 1]:  # Thumb and pinky up
            gesture = "Previous Track"
        elif fingers_up == [0, 1, 1, 1, 1]:  # All except thumb up
            gesture = "Volume Up"
        elif fingers_up == [1, 0, 0, 0, 0]:  # Only thumb up
            gesture = "Volume Down"
        
        # Add to history for smoothing
        self.gesture_history.append(gesture)
        
        # Return smoothed gesture
        return self._smooth_gesture(gesture)
    
    def _smooth_gesture(self, current_gesture):
        """Smooth gesture detection to prevent flickering"""
        if not self.gesture_history:
            return current_gesture
        
        # Count occurrences of each gesture in history
        gesture_counts = {}
        for g in self.gesture_history:
            if g in gesture_counts:
                gesture_counts[g] += 1
            else:
                gesture_counts[g] = 1
        
        # Find the most common gesture
        max_count = 0
        most_common = current_gesture
        
        for g, count in gesture_counts.items():
            if count > max_count:
                max_count = count
                most_common = g
        
        # Only change gesture if the new one is consistent
        if most_common != self.last_gesture:
            # Require at least 60% of frames to have the same gesture to change
            threshold = 0.6 * len(self.gesture_history)
            if max_count >= threshold:
                self.last_gesture = most_common
        
        return self.last_gesture