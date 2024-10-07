import cv2
import mediapipe as mp
import numpy as np


class Sense:

    def __init__(self):
        # Initialize the Mediapipe Hands object to track hand landmarks
        self.mp_hands = mp.solutions.hands.Hands()

    def _get_landmarks(self, landmarks):
        """Helper function to retrieve relevant landmarks for fingers and thumb."""
        return {
            "thumb_tip": landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_TIP],
            "index_tip": landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP],
            "middle_tip": landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_TIP],
            "ring_tip": landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_TIP],
            "pinky_tip": landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_TIP],
            "index_mcp": landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_MCP],
            "middle_mcp": landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_MCP],
            "ring_mcp": landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_MCP],
            "pinky_mcp": landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_MCP]
        }

    def _calculate_distance(self, point1, point2):
        """Helper function to compute the Euclidean distance between two points."""
        return np.linalg.norm(np.array([point1.x - point2.x, point1.y - point2.y]))

    def extract_finger_touch(self, landmarks):
        """Check if each finger touches the thumb."""
        points = self._get_landmarks(landmarks)
        threshold = 0.05  # Threshold for determining whether fingers are touching

        return {
            "thumb_to_index": self._calculate_distance(points["thumb_tip"], points["index_tip"]) < threshold,
            "thumb_to_middle": self._calculate_distance(points["thumb_tip"], points["middle_tip"]) < threshold,
            "thumb_to_ring": self._calculate_distance(points["thumb_tip"], points["ring_tip"]) < threshold,
            "thumb_to_pinky": self._calculate_distance(points["thumb_tip"], points["pinky_tip"]) < threshold
        }

    def extract_finger_open_close(self, landmarks):
        """Detect if fingers are open or closed."""
        points = self._get_landmarks(landmarks)
        open_threshold = 0.15  # Distance threshold for determining if a finger is open

        # Check for each finger if the distance between the tip and MCP is greater than the threshold
        return {
            "index": self._calculate_distance(points["index_tip"], points["index_mcp"]) > open_threshold,
            "middle": self._calculate_distance(points["middle_tip"], points["middle_mcp"]) > open_threshold,
            "ring": self._calculate_distance(points["ring_tip"], points["ring_mcp"]) > open_threshold,
            "pinky": self._calculate_distance(points["pinky_tip"], points["pinky_mcp"]) > open_threshold
        }

    def extract_hand_movements(self, landmarks):
        """Returns a dictionary of detected hand movements (touching thumb, fingers open/closed)."""
        finger_touch = self.extract_finger_touch(landmarks)
        finger_open_close = self.extract_finger_open_close(landmarks)
        return {**finger_touch, **finger_open_close}
