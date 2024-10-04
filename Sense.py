import cv2
import mediapipe as mp
import math
import numpy as np
import mediapipe as mp


# Sense Component: Detect joints using the camera
# Things you need to improve: Make the skeleton tracking smoother and robust to errors.
class Sense:

    def __init__(self):
        # Initialize the Mediapipe Pose object to track joints

        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_pose = mp.solutions.pose.Pose()
        self.mp_hands = mp.solutions.hands.Hands()

        # used later for having a moving avergage
        self.angle_window = [-1, -1, -1, -1, -1, -1, -1, -1, -1, -1]
        self.previous_angle = -1

    def detect_joints(self, frame):
        results = self.mp_pose.process(frame)
        return results if results else None

    def detect_hands(self, frame):
        results = self.mp_hands.process(frame)
        return results if results else None

    def calculate_angle(self, joint1, joint2, joint3):
        # Calculate vectors
        vector1 = [joint1[0] - joint2[0], joint1[1] - joint2[1]]
        vector2 = [joint3[0] - joint2[0], joint3[1] - joint2[1]]

        # Calculate the dot product and magnitude of the vectors
        dot_product = vector1[0] * vector2[0] + vector1[1] * vector2[1]
        magnitude1 = math.sqrt(vector1[0] ** 2 + vector1[1] ** 2)
        magnitude2 = math.sqrt(vector2[0] ** 2 + vector2[1] ** 2)

        # Calculate the angle in radians and convert to degrees
        angle = math.acos(dot_product / (magnitude1 * magnitude2))

        # get a moving average
        self.angle_window.pop(0)
        self.angle_window.append(angle)
        # Use np.convolve to calculate the moving average
        window_size = 10
        angle_mvg = np.convolve(np.asarray(self.angle_window), np.ones(window_size) / window_size, mode='valid')

        return math.degrees(angle_mvg)

    def extract_joint_coordinates(self, landmarks, joint):
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

        # Example for defining a function that extracts an angle

    def extract_hip_angle(self, landmarks):
        left_hip = [landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_HIP.value].x,
                    landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_HIP.value].y]
        left_shoulder = [landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value].x,
                         landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER.value].y]
        left_knee = [landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_KNEE.value].x,
                     landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_KNEE.value].y]
        return self.calculate_angle(left_shoulder, left_hip, left_knee)

        # Extracts the angle of the knee

    def extract_knee_angle(self, landmarks):
        left_hip = [landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_HIP.value].x,
                    landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_HIP.value].y]
        left_knee = [landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_KNEE.value].x,
                     landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_KNEE.value].y]
        left_ankle = [landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_ANKLE.value].x,
                      landmarks.landmark[mp.solutions.pose.PoseLandmark.LEFT_ANKLE.value].y]
        return self.calculate_angle(left_hip, left_knee, left_ankle)

        # Function to extract hand coordinates (including fingers)

    def extract_hand_coordinates(self, landmarks):
        hand_coords = {
            'wrist': [landmarks.landmark[mp.solutions.hands.HandLandmark.WRIST].x,
                      landmarks.landmark[mp.solutions.hands.HandLandmark.WRIST].y],
            'thumb_mcp': [landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_MCP].x,
                          landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_MCP].y],
            'thumb_tip': [landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_TIP].x,
                          landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_TIP].y],
            'index_mcp': [landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_MCP].x,
                          landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_MCP].y],
            'index_tip': [landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP].x,
                          landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP].y],
            # Add more fingers as needed
        }
        return hand_coords

    # Function to calculate the angles for hand joints/fingers
    def extract_hand_angles(self, landmarks):
        wrist = [landmarks.landmark[mp.solutions.hands.HandLandmark.WRIST].x,
                 landmarks.landmark[mp.solutions.hands.HandLandmark.WRIST].y]
        thumb_mcp = [landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_MCP].x,
                     landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_MCP].y]
        thumb_tip = [landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_TIP].x,
                     landmarks.landmark[mp.solutions.hands.HandLandmark.THUMB_TIP].y]
        index_mcp = [landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_MCP].x,
                     landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_MCP].y]
        index_tip = [landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP].x,
                     landmarks.landmark[mp.solutions.hands.HandLandmark.INDEX_FINGER_TIP].y]
        middle_mcp = [landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_MCP].x,
                      landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_MCP].y]
        middle_tip = [landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_TIP].x,
                      landmarks.landmark[mp.solutions.hands.HandLandmark.MIDDLE_FINGER_TIP].y]
        ring_mcp = [landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_MCP].x,
                    landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_MCP].y]
        ring_tip = [landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_TIP].x,
                    landmarks.landmark[mp.solutions.hands.HandLandmark.RING_FINGER_TIP].y]
        pinky_mcp = [landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_MCP].x,
                    landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_MCP].y]
        pinky_tip = [landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_TIP].x,
                    landmarks.landmark[mp.solutions.hands.HandLandmark.PINKY_TIP].y]

        thumb_angle = self.calculate_angle(wrist, thumb_mcp, thumb_tip)
        index_angle = self.calculate_angle(wrist, index_mcp, index_tip)
        middle_angle = self.calculate_angle(wrist, middle_mcp, middle_tip)
        ring_angle = self.calculate_angle(wrist, ring_mcp, ring_tip)
        pinky_angle = self.calculate_angle(wrist, pinky_mcp, pinky_tip)

        return {
            'thumb_angle': thumb_angle,
            'index_angle': index_angle,
            'middle_angle': middle_angle,
            'ring_angle': ring_angle,
            'pinky_angle': pinky_angle
        }
