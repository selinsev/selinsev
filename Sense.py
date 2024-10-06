import cv2
import mediapipe as mp
import numpy as np


class Sense:
    
    def __init__(self):
        # Initialize the Mediapipe Hands object to track hand landmarks
        self.mp_hands = mp.solutions.hands.Hands()

    def extract_finger_touch(self, landmarks):
        """Check if each finger touches the thumb."""
        # Extract landmarks for easier reference
        thumb_tip = landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_TIP]
        index_tip = landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP]
        middle_tip = landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_TIP]
        ring_tip = landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_TIP]
        pinky_tip = landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_TIP]

        def distance(landmark1, landmark2):
            return np.sqrt((landmark1.x - landmark2.x) ** 2 + (landmark1.y - landmark2.y) ** 2)

        # Define a distance threshold for a successful touch
        threshold = 0.05
        distances = {
            "thumb_to_index": distance(thumb_tip, index_tip) < threshold,
            "thumb_to_middle": distance(thumb_tip, middle_tip) < threshold,
            "thumb_to_ring": distance(thumb_tip, ring_tip) < threshold,
            "thumb_to_pinky": distance(thumb_tip, pinky_tip) < threshold,
        }

        return distances

    def extract_finger_open_close(self, landmarks):
        """Detect if fingers are open or closed."""
        # Get tip and base (MCP) landmarks for each finger
        fingers = {
            "index": (landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP],
                      landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_MCP]),
            "middle": (landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_TIP],
                       landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_MCP]),
            "ring": (landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_TIP],
                     landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_MCP]),
            "pinky": (landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_TIP],
                      landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_MCP])
        }

        open_fingers = {}
        open_threshold = 0.15  # Adjust this threshold based on distance

        for finger, (tip, base) in fingers.items():
            dist = np.linalg.norm(np.array([tip.x - base.x, tip.y - base.y]))
            open_fingers[finger] = dist > open_threshold  # True if finger is open

        return open_fingers

    def extract_hand_movements(self, landmarks):
        """Returns a dictionary of detected hand movements (touching thumb, fingers open/closed)."""
        finger_touch = self.extract_finger_touch(landmarks)
        finger_open_close = self.extract_finger_open_close(landmarks)
        return {**finger_touch, **finger_open_close}
