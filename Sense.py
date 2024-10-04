import cv2
import mediapipe as mp
import math
import numpy as np


class Sense:

    def __init__(self):
        # Initialize the Mediapipe Pose and Hand objects to track joints
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose.Pose()
        self.mp_hands = mp.solutions.hands.Hands()

        # For smoothing angles and distances, keep a window for moving average
        self.angle_window = [-1] * 10
        self.distance_window = [-1] * 10

    def detect_joints(self, frame):
        """Detect pose joints (skeleton tracking)."""
        results = self.mp_pose.process(frame)
        return results if results else None

    def detect_hands(self, frame):
        """Detect hand joints and landmarks."""
        results = self.mp_hands.process(frame)
        return results if results else None

    def calculate_angle(self, joint1, joint2, joint3):
        """Calculate the angle between three joints (vectors)."""
        vector1 = [joint1[0] - joint2[0], joint1[1] - joint2[1]]
        vector2 = [joint3[0] - joint2[0], joint3[1] - joint2[1]]

        dot_product = vector1[0] * vector2[0] + vector1[1] * vector2[1]
        magnitude1 = math.sqrt(vector1[0] ** 2 + vector1[1] ** 2)
        magnitude2 = math.sqrt(vector2[0] ** 2 + vector2[1] ** 2)

        angle = math.acos(dot_product / (magnitude1 * magnitude2))

        # Moving average for smoothing the angle
        self.angle_window.pop(0)
        self.angle_window.append(angle)
        window_size = 10
        angle_mvg = np.convolve(np.asarray(self.angle_window), np.ones(window_size) / window_size, mode='valid')

        return math.degrees(angle_mvg[0])

    def extract_joint_coordinates(self, landmarks, joint):
        """Extract coordinates of a specified joint."""
        joint_index_map = {
            'left_shoulder': mp.solutions.pose.PoseLandmark.LEFT_SHOULDER,
            'right_shoulder': mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER,
            'left_elbow': mp.solutions.pose.PoseLandmark.LEFT_ELBOW,
            'right_elbow': mp.solutions.pose.PoseLandmark.RIGHT_ELBOW,
            'left_wrist': mp.solutions.pose.PoseLandmark.LEFT_WRIST,
            'right_wrist': mp.solutions.pose.PoseLandmark.RIGHT_WRIST,
            'left_hip': mp.solutions.pose.PoseLandmark.LEFT_HIP,
            'right_hip': mp.solutions.pose.PoseLandmark.RIGHT_HIP,
            'left_knee': mp.solutions.pose.PoseLandmark.LEFT_KNEE,
            'right_knee': mp.solutions.pose.PoseLandmark.RIGHT_KNEE,
            'left_ankle': mp.solutions.pose.PoseLandmark.LEFT_ANKLE,
            'right_ankle': mp.solutions.pose.PoseLandmark.RIGHT_ANKLE,
        }
        joint_index = joint_index_map[joint]
        landmark = landmarks.landmark[joint_index]

        return landmark.x, landmark.y

    def extract_finger_touch(self, landmarks):
        """Check if each finger touches the thumb."""
        thumb_tip = landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_TIP]
        index_tip = landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP]
        middle_tip = landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_TIP]
        ring_tip = landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_TIP]
        pinky_tip = landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_TIP]
        pinky_base = landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_MCP]

        def distance(landmark1, landmark2):
            return np.sqrt((landmark1.x - landmark2.x) ** 2 + (landmark1.y - landmark2.y) ** 2)

        # Smoothed distance using moving average
        threshold = 0.05
        dist_index = distance(thumb_tip, index_tip)
        dist_middle = distance(thumb_tip, middle_tip)
        dist_ring = distance(thumb_tip, ring_tip)
        dist_pinky = distance(thumb_tip, pinky_tip)
        dist_pinky = distance(thumb_tip, pinky_tip)
        dist_pinky_mcp = distance(thumb_tip, pinky_base)

        # Check if each finger is touching the thumb
        touch_index = dist_index < threshold
        touch_middle = dist_middle < threshold
        touch_ring = dist_ring < threshold
        touch_pinky = dist_pinky < threshold
        touch_pinky_mcp = dist_pinky_mcp < threshold

        return {
            "thumb_to_index": touch_index,
            "thumb_to_middle": touch_middle,
            "thumb_to_ring": touch_ring,
            "thumb_to_pinky": touch_pinky,
            "thumb_to_pinky_mcp": touch_pinky_mcp   
        }

    def extract_finger_open_close(self, landmarks):
        """Detect if fingers are open or closed by comparing distances."""

        def distance(landmark1, landmark2):
            return np.sqrt((landmark1.x - landmark2.x) ** 2 + (landmark1.y - landmark2.y) ** 2)

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
        close_threshold = 0.05  # Adjust this threshold based on distance
        open_threshold = 0.15

        for finger, (tip, base) in fingers.items():
            dist = distance(tip, base)
            open_fingers[finger] = dist > open_threshold  # True if finger is open

        return open_fingers
    
    def extract_finger_to_wrist(self, landmarks):
        wrist = landmarks.landmark[mp.solutions.hands.HandLandmark.WRIST]
        thumb_tip = landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_TIP]
        index_tip = landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP]
        middle_tip = landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_TIP]
        ring_tip = landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_TIP]
        pinky_tip = landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_TIP]

        def distance(landmark1, landmark2):
            return np.sqrt((landmark1.x - landmark2.x) ** 2 + (landmark1.y - landmark2.y) ** 2)
        
        wrist_threshold = 0.15

        fingers_to_wrist = distance(thumb_tip, wrist) < wrist_threshold and distance(index_tip, wrist) < wrist_threshold and distance(middle_tip, wrist) < wrist_threshold and distance(ring_tip, wrist) < wrist_threshold and distance(pinky_tip, wrist) < wrist_threshold
        return fingers_to_wrist

    def extract_hand_movements(self, landmarks):
        """Returns a dictionary of detected hand movements (touching thumb, fingers open/closed)."""
        finger_touch = self.extract_finger_touch(landmarks)
        finger_open_close = self.extract_finger_open_close(landmarks)
        fingers_to_wrist = self.extract_finger_to_wrist(landmarks)
        return {**finger_touch, **finger_open_close, "fingers_to_wrist": fingers_to_wrist}
  
