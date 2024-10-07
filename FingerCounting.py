import cv2
import time
import os
import HandTrackingModule as HTM

class FingerCounter:

    def __init__(self, wCam=640, hCam=480, detectionCon=0.8, folderPath="FingerImages"):
        """
        Initialize the FingerCounter class.
        Args:
            wCam: Width of the camera feed.
            hCam: Height of the camera feed.
            detectionCon: Confidence level for hand detection.
            folderPath: Path to the folder containing finger images.
        """
        self.wCam = wCam
        self.hCam = hCam
        self.detectionCon = detectionCon
        self.folderPath = r'E:\Week3_code_example\coach\FingerImages'  # Absolute path
        self.tipIds = [8, 12, 16, 20]
        self.pTime = 0

        # Initialize camera
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, self.wCam)  # Set width
        self.cap.set(4, self.hCam)  # Set height

        # Load images for overlays
        self.overlayList = self.loadImages()

        # Initialize hand detector
        self.detector = HTM.HandDetector(detectionCon=self.detectionCon)

    def loadImages(self):
        """
        Load images from the specified folder for overlay purposes.
        Returns:
            List of overlay images.
        """
        myList = os.listdir(self.folderPath)  # Check if this path is valid
        overlayList = []
        for imPath in myList:
            image = cv2.imread(f'{self.folderPath}/{imPath}')
            overlayList.append(image)
        return overlayList

    def lmlist(self, img):
        img = self.detector.findHands(img)
        lmList = self.detector.findPosition(img, draw=False)
        return lmList

    def countFingers(self, lmList):
        """
        Count the number of fingers that are open.
        Args:
            lmList: List of hand landmarks.
        Returns:
            Integer value representing the number of fingers open.
        """
        fingers = []

        # Thumb
        if lmList[4][1] < lmList[3][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        # Other fingers
        for id in range(4):
            if lmList[self.tipIds[id]][2] < lmList[self.tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        return fingers.count(1)

    def displayOverlay(self, value, frame):
        """
        Display the corresponding overlay image based on the number of fingers counted.
        Args:
            value: The number of fingers open.
            frame: The current video frame.
        """
        h, w, c = self.overlayList[value-1].shape
        frame[0:h, 0:w] = self.overlayList[value-1]

    def run(self):
        """
        Main loop to run the finger counter. Captures video feed, processes frames, and displays results.
        """
        while True:
            success, frame = self.cap.read()
            if not success:
                print("Failed to read from camera.")
                break

            # Detect hand landmarks
            frame = self.detector.findHands(frame)
            lmList = self.detector.findPosition(frame, draw=False)

            if len(lmList) > 0:
                # Count the number of open fingers
                value = self.countFingers(lmList)

                # Display the corresponding overlay image
                self.displayOverlay(value, frame)

                # Display the number of open fingers on the frame
                cv2.putText(frame, str(value), (45, 275), cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 0), 5)

            # Calculate and display FPS
            cTime = time.time()
            fps = 1 / (cTime - self.pTime)
            self.pTime = cTime
            cv2.putText(frame, f'FPS: {int(fps)}', (480, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)

            # Display the frame
            cv2.imshow('frame', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        self.cap.release()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    # Create an instance of FingerCounter and run it
    finger_counter = FingerCounter()
    finger_counter.run()