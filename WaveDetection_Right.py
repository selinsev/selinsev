import cv2
import time
from coach import HandTrackingModule as HTM

class WaveDetector:
    def __init__(self, max_positions=30, threshold=15):
        """
        Initialize the WaveDetector class.
        Args:
            max_positions: Number of previous frames to store for x-axis movement tracking.
            threshold: Minimum distance (in pixels) between left-right movements to count as a wave.
        """
        self.max_positions = max_positions  # Maximum number of frames to track
        self.threshold = threshold  # Movement threshold for detecting direction change
        self.x_positions = []  # List to store x-axis positions of the index finger tip
        self.detector = HTM.HandDetector()  # Hand tracking module instance
        self.pTime = 0  # Initialize pTime for FPS calculation

    def detectWave(self, img):
        """
        Detects hand wave based on the movement in x-axis.
        Args:
            img: The current frame from the video feed.
        Returns:
            bool: True if a wave is detected, otherwise False.
        """
        # Process the frame to detect the hand and find positions
        img = self.detector.findHands(img)
        lmList = self.detector.findPosition(img, draw=False)

        if len(lmList) != 0:
            # Get the x-position of the index finger tip (landmark 8)
            x_pos = lmList[8][1]
            self.x_positions.append(x_pos)

            # Keep track of the last max_positions frames to detect the wave gesture
            if len(self.x_positions) > self.max_positions:
                self.x_positions.pop(0)

            # Detect wave gesture by checking direction changes
            if self.detectDirectionChanges():
                return True

        return False

    def detectDirectionChanges(self):
        """
        Helper function to detect direction changes in the x_positions list.
        Returns:
            bool: True if sufficient direction changes are detected.
        """
        if len(self.x_positions) < 5:
            return False

        # Count the number of significant direction changes
        wave_count = 0
        for i in range(1, len(self.x_positions) - 1):
            if (self.x_positions[i - 1] - self.x_positions[i]) * (self.x_positions[i] - self.x_positions[i + 1]) < 0:
                if abs(self.x_positions[i] - self.x_positions[i - 1]) > self.threshold:
                    wave_count += 1

        # Return True if at least 2 direction changes are detected
        return wave_count >= 2

    def processFrame(self, img):
        """
        Process the current frame to detect a wave gesture.
        Args:
            img: The current frame from the video feed.
        Returns:
            img: The annotated frame with detection results.
        """
        img = self.detector.findHands(img)
        lmList = self.detector.findPosition(img, draw=False)

        # Detect the hand and check if it's the right hand (by analyzing handedness)
        handedness = None
        if self.detector.results.multi_handedness:
            handedness = self.detector.results.multi_handedness[0].classification[0].label
            # Check if it's the right hand
            if handedness == 'Right' and len(lmList) != 0:
                # Get the x-position of the index finger tip (landmark 8)
                x_pos = lmList[8][1]
                self.x_positions.append(x_pos)

                # Keep track of the last max_positions frames to detect the wave gesture
                if len(self.x_positions) > self.max_positions:
                    self.x_positions.pop(0)

                # Detect wave gesture
                if self.detectDirectionChanges():
                    cv2.putText(img, "Right Hand Wave Detected!", (50, 150),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
                    print("Wave gesture detected!")
                else:
                    # If no wave is detected, prompt the user to wave their hand
                    cv2.putText(img, "Please wave your right hand!", (50, 150),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
            else:
                cv2.putText(img, "Waiting for right hand...", (50, 150),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 0), 2)

        return img

    def run(self):
        """
        Main loop to run the wave detection.
        Captures video feed, processes frames, and displays results.
        """
        cap = cv2.VideoCapture(0)

        while True:
            success, img = cap.read()
            if not success:
                print("Failed to read from camera.")
                break

            img = self.processFrame(img)

            # FPS Calculation
            cTime = time.time()
            fps = 1 / (cTime - self.pTime) if self.pTime != 0 else 0
            self.pTime = cTime
            cv2.putText(img, f"FPS: {int(fps)}", (10, 70), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 255), 2)

            # Show the frame with annotations
            cv2.imshow("Wave Detection", img)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    # Create an instance of WaveDetector and run it
    wave_detector = WaveDetector()
    wave_detector.run()
