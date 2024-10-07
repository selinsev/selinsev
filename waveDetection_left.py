# wave_detection.py
import cv2
import time
import HandTrackingModule as HTM


def detectWave(x_positions, threshold=30):
    """
    Detects hand wave based on the movement in x-axis.
    Args:
        x_positions: A list of previous x-axis positions of a landmark (index finger tip).
        threshold: Minimum distance (in pixels) between left-right movements to count as a wave.
    Returns:
        bool: True if a wave is detected, otherwise False.
    """
    if len(x_positions) < 3:
        return False

    # Count the number of direction changes (left-right or right-left)
    wave_count = 0
    for i in range(1, len(x_positions) - 1):
        if (x_positions[i - 1] - x_positions[i]) * (x_positions[i] - x_positions[i + 1]) < 0:
            if abs(x_positions[i] - x_positions[i - 1]) > threshold:
                wave_count += 1

    # Return True if at least 2 direction changes are detected (1 full wave cycle)
    return wave_count >= 2


def main():
    pTime = 0
    cTime = 0
    cap = cv2.VideoCapture(0)  # Change to correct camera index
    detector = HTM.HandDetector()

    # To store x positions of the tip of the index finger (landmark 8)
    x_positions = []

    while True:
        success, img = cap.read()
        if not success:
            print("Failed to read from camera.")
            break

        img = detector.findHands(img)
        lmList = detector.findPosition(img)

        # Detect the hand and check if it's the left hand (by analyzing handedness)
        handedness = None
        if detector.results.multi_handedness:
            handedness = detector.results.multi_handedness[0].classification[0].label
            # Check if it's the left hand
            if handedness == 'Left':
                if len(lmList) != 0:
                    # Get the x-position of the index finger tip (landmark 8)
                    x_pos = lmList[8][1]
                    x_positions.append(x_pos)

                    # Keep track of last 20 frames to detect the wave gesture
                    if len(x_positions) > 20:
                        x_positions.pop(0)

                    # Detect wave gesture
                    if detectWave(x_positions):
                        cv2.putText(img, "Left Hand Wave Detected!", (50, 150),
                                    cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 1)
                        print("Wave gesture detected!")
                    else:
                        # If no wave is detected, prompt the user to wave their hand
                        cv2.putText(img, "Please wave your left hand!", (50, 150),
                                    cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 1)
                else:
                    # If no landmarks are detected, ask the user to wave
                    cv2.putText(img, "Please wave your left hand!", (50, 150),
                                cv2.FONT_HERSHEY_COMPLEX, 2, (0, 0, 255), 3)
            else:
                cv2.putText(img, "Waiting for left hand...", (50, 150),
                            cv2.FONT_HERSHEY_COMPLEX, 2, (255, 255, 0), 3)

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, f"FPS: {int(fps)}", (10, 70), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 255), 2)
        cv2.imshow("Image", img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
