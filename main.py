import cv2
import mediapipe as mp
from coach import Sense
from coach import Think
from coach import Act
import numpy as np

# Main Program Loop
def main():
    # Initialize the components: Sense for input, Think for decision-making, Act for output
    sense = Sense.Sense()
    act = Act.Act()
    think = Think.Think(act)

    # Initialize the webcam capture
    cap = cv2.VideoCapture(0)  # Use the default camera (0)
    mp_hands = mp.solutions.hands
    hands = mp_hands.Hands()
    mp_drawing = mp.solutions.drawing_utils

    # Main loop to process video frames
    for i in range(len(act.instructions)):
        instruction = act.get_instruction(i)
        print(f"Instruction: {instruction}")
        think.set_instruction(instruction)  # Set the current instruction for decision-making

        movement_completed = False  # Flag to check if the movement is completed

        while not movement_completed:
            # Capture frame-by-frame from the webcam
            ret, frame = cap.read()
            if not ret:
                print("Failed to grab frame")
                break

            # Sense: Detect joints
            results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            # Draw the hand annotations on the image.
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(
                        frame,
                        hand_landmarks,
                        mp_hands.HAND_CONNECTIONS)

                    # Extract hand movements
                    movements = sense.extract_hand_movements(hand_landmarks)
                    think.update_state(movements)  # Update the state based on detected movements

                    # Use the decision function to check if the movement is correct
                    if think.decide_movement(movements):
                        cv2.putText(frame, "Correct Movement!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                        movement_completed = True  # Mark as completed
                    else:
                        cv2.putText(frame, "Try Again!", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            # Create a tinted background for the instruction text
            background_height = 100
            background_width = 400
            # White background rectangle on the left side
            cv2.rectangle(frame, (0, 0), (background_width, background_height), (255, 255, 255), -1)

            # Draw the instruction text on the tinted background
            cv2.putText(frame, instruction, (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2)

            # Flip the image horizontally for a selfie-view display.
            cv2.imshow('MediaPipe Hands', frame)  # No need to flip, as the text is on the left now

            # Exit if the 'q' key is pressed
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

    # Release the webcam and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()


