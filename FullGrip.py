import cv2
import time
import math
from coach import HandTrackingModule as HTM

class GripDetector:
    def __init__(self, thresholds=None):
        """
        Initialize the GripDetector class with optional thresholds for grip detection.
        Args:
            thresholds: List of distance thresholds for each finger to detect full grip.
        """
        self.pTime = 0  # Previous time for FPS calculation
        self.thresholds = thresholds if thresholds is not None else [30, 30, 40, 40, 40]  # Default thresholds
        self.detector = HTM.HandDetector()  # Initialize the hand detector

    def calculateDistance(self, p1, p2):
        """
        Calculate the Euclidean distance between two points p1 and p2.
        Args:
            p1, p2: Tuples or lists representing points (x, y).
        Returns:
            float: Euclidean distance between p1 and p2.
        """
        # Ensure p1 and p2 are tuples or lists with at least two elements (x, y)
        if len(p1) < 2 or len(p2) < 2:
            raise ValueError("Both points must have at least two coordinates (x, y).")

        # Ensure points are converted to floats if they are not already
        p1 = [float(coord) for coord in p1]
        p2 = [float(coord) for coord in p2]

        return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)

    def detectFullGrip(self, lmList):
        """
        Detects if the hand is making a full grip (closed fist).
        Args:
            lmList: List of landmark positions for the hand.
        Returns:
            bool: True if a full grip is detected, otherwise False.
        """
        if len(lmList) == 0:
            return False

        # Fingertip landmarks (4, 8, 12, 16, 20)
        fingertips = [lmList[4], lmList[8], lmList[12], lmList[16], lmList[20]]

        # Corresponding base joint landmarks (2, 5, 9, 13, 17)
        base_joints = [lmList[6], lmList[5], lmList[9], lmList[13], lmList[17]]  # Ensure thumb is at index 2

        # Check the distance between each fingertip and its corresponding base joint
        for i in range(5):
            # Ensure we're accessing valid 2D coordinates (x, y)
            if len(fingertips[i]) < 3 or len(base_joints[i]) < 3:
                return False  # Skip if we don't have the necessary data

            fingertip_x, fingertip_y = fingertips[i][1], fingertips[i][2]  # assuming lmList[i] is in form (id, x, y)
            base_joint_x, base_joint_y = base_joints[i][1], base_joints[i][2]

            # Calculate the distance between the fingertip and the base joint
            distance = self.calculateDistance((fingertip_x, fingertip_y), (base_joint_x, base_joint_y))

            # Check if the distance exceeds the threshold for a closed fist
            if distance > self.thresholds[i]:
                return False  # If any finger isn't bent enough, it's not a full grip

        # If all distances are below the thresholds, it's a full grip
        return True
    def lmlist(self, img):
        img = self.detector.findHands(img)
        lmList = self.detector.findPosition(img, draw=False)
        return lmList

    def detectPartialGrip(self, lmList):
        """
        Detects if the hand is making a partial grip (some fingers bent, some open).
        Args:
            lmList: List of landmark positions for the hand.
        Returns:
            bool: True if a partial grip is detected, otherwise False.
        """
        if len(lmList) == 0:
            return False

        # Fingertip landmarks (4, 8, 12, 16, 20)
        fingertips = [lmList[4], lmList[8], lmList[12], lmList[16], lmList[20]]

        # Corresponding base joint landmarks (2, 5, 9, 13, 17)
        base_joints = [lmList[2], lmList[5], lmList[9], lmList[13], lmList[17]]  # Ensure thumb is at index 2

        bent_fingers = 0
        straight_fingers = 0

        # Check the distance between each fingertip and its corresponding base joint
        for i in range(5):
            distance = self.calculateDistance(fingertips[i][1:], base_joints[i][1:])
            if distance < self.thresholds[i]:
                bent_fingers += 1  # Finger is bent
            else:
                straight_fingers += 1  # Finger is straight

        # If some fingers are bent but not all, it's a partial grip
        return 1 <= bent_fingers < 5

    def run(self):
        """
        Main loop for the grip detection.
        Captures video feed, detects hand landmarks, and identifies grip status.
        """
        cap = cv2.VideoCapture(0)

        while True:
            success, img = cap.read()
            if not success:
                print("Failed to read from camera.")
                break

            img = self.detector.findHands(img)
            lmList = self.detector.findPosition(img, draw=False)

            if not lmList:  # Check if lmList is empty
                cv2.putText(img, "No Hand Detected", (50, 150), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 1)
            else:
                # Detect full grip
                if self.detectFullGrip(lmList):
                    cv2.putText(img, "Full Grip Detected!", (50, 150), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 1)
                    print("Full grip detected!")
                # Detect partial grip
                elif self.detectPartialGrip(lmList):
                    cv2.putText(img, "Partial Grip Detected!", (50, 150), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 0), 1)
                    print("Partial grip detected!")
                else:
                    cv2.putText(img, "Open Hand", (50, 150), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 1)

            # FPS Calculation
            cTime = time.time()
            fps = 1 / (cTime - self.pTime) if self.pTime != 0 else 0
            self.pTime = cTime
            cv2.putText(img, f"FPS: {int(fps)}", (10, 70), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 255), 1)

            cv2.imshow("Image", img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    # Create an instance of the GripDetector class and run the detection
    grip_detector = GripDetector()
    grip_detector.run()
