import cv2
import mediapipe as mp
from coach import Sense
from coach import Think
from coach import Act

import numpy as np


# Main Program Loop
def main():
    """
    Main function to initialize the exercise tracking application.

    This function sets up the webcam feed, initializes the Sense, Think, and Act components,
    and starts the main loop to continuously process frames from the webcam.
    """

    # Initialize the components: Sense for input, Think for decision-making, Act for output
    sense = Sense.Sense()
    act = Act.Act()
    think = Think.Think(act)

    # Initialize the webcam capture
    cap = cv2.VideoCapture(0)  # Use the default camera (0)

    # Main loop to process video frames
    while cap.isOpened():

        # Capture frame-by-frame from the webcam
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame")
            break

        mp_drawing = mp.solutions.drawing_utils
        mp_drawing_styles = mp.solutions.drawing_styles
        mp_hands = mp.solutions.hands
        hands = mp_hands.Hands()
        # Sense: Detect joints
        joints = sense.detect_joints(frame)
        results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        # landmarks = joints.pose_landmarks
        #
        # # If landmarks are detected, calculate the elbow angle
        # if landmarks:
        #     # Extract joint coordinates for the left arm
        #     # For this example, we will use specific landmark indexes for shoulder, elbow, and wrist
        #     # shoulder = sense.extract_joint_coordinates(landmarks, 'left_shoulder')
        #     elbow = sense.extract_joint_coordinates(landmarks, 'right_elbow')
        #     index = sense.extract_joint_coordinates(landmarks, 'right_index')
        #     wrist = sense.extract_joint_coordinates(landmarks, 'right_wrist')
        #
        #
        #     # Calculate the hand angle
        #     hand_angle_mvg = sense.calculate_angle(elbow, wrist, index)
        #
        #     # Think: Next, give the angles to the decision-making component and make decisions based on joint data
        #     think.update_state(hand_angle_mvg, sense.previous_angle)
        #
        #     # We'll save the previous angle for later comparison
        #     sense.previous_angle = hand_angle_mvg
        #
        #     decision = think.state
        #
        #     # Act: Provide feedback to the user.
        #     act.provide_feedback(decision, frame=frame, joints=joints, elbow_angle_mvg=hand_angle_mvg)
        #     # Render the balloon visualization
        #     # act.visualize_balloon()
        #
        #     # think.check_for_timeout()



        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        frame.flags.writeable = False
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(frame)

        # Draw the hand annotations on the image.
        frame.flags.writeable = True
        frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(
                    frame,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())
        # Flip the image horizontally for a selfie-view display.
        cv2.imshow('MediaPipe Hands', cv2.flip(frame, 1))

        # Exit if the 'q' key is pressed
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break


    # Release the webcam and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()



if __name__ == "__main__":
    main()
