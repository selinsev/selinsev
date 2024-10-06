import os
import tkinter as tk
import cv2
import mediapipe as mp
from coach import Act, Sense, Think

# Suppress TensorFlow Lite warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Initialize MediaPipe hands and drawing utils
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Initialize components
sense = Sense.Sense()
act = Act.Act()
think = Think.Think(act)

# Flag to track exercise state
current_exercise = 0
cap = None  # Initialize the camera capture variable
required_repetitions = 3  # Number of repetitions needed for each exercise
repetitions_completed = 0  # Counter for completed repetitions
current_hand = 'left'  # Can be 'left' or 'right'


def start_exercise():
    """Start the first exercise and open the camera."""
    global current_exercise, repetitions_completed, current_hand
    current_exercise = 0
    repetitions_completed = required_repetitions
    current_hand = 'left'  # Start with the left hand
    message_label.config(text="Starting exercises with the left hand...")

    start_button.pack_forget()  # Hide the start button for subsequent exercises
    root.after(500, run_exercise)  # Delay to let message update before starting


def next_exercise():
    """Move to the next exercise, close the camera, and re-open it."""
    global current_exercise, repetitions_completed, current_hand
    current_exercise += 1
    
    # Reset for the left hand
    if current_hand == 'left':
        if current_exercise < len(act.instructions):
            repetitions_completed = required_repetitions  # Reset repetitions here
            repetition_label.config(text=f"Repetitions left: {repetitions_completed}")  # Update the label
            message_label.config(text="Starting the next exercise with the left hand...")
            root.after(500, run_exercise)  # Delay to let message update before starting
        else:
            # Move to the right hand after completing left-hand exercises
            current_hand = 'right'
            current_exercise = 0  # Reset exercises for the right hand
            repetitions_completed = required_repetitions  # Reset repetitions for right hand
            repetition_label.config(text=f"Repetitions left: {repetitions_completed}")  # Update the label
            message_label.config(text="Starting exercises with the right hand...")
            root.after(500, run_exercise)  # Delay to let message update before starting
    else:  # Right hand logic
        if current_exercise < len(act.instructions):
            repetitions_completed = required_repetitions  # Reset repetitions for the right hand
            repetition_label.config(text=f"Repetitions left: {repetitions_completed}")  # Update the label
            message_label.config(text="Starting the next exercise with the right hand...")
            root.after(500, run_exercise)  # Delay to let message update before starting
        else:
            message_label.config(text="All exercises are complete!")
            next_button.pack_forget()  # Hide the next button when all exercises are complete


def run_exercise():
    """Handles the main exercise loop, displaying instructions and processing movements."""
    global cap, repetitions_completed

    if current_exercise >= len(act.instructions):
        message_label.config(text="All exercises are complete!")
        return

    # Open the camera
    cap = cv2.VideoCapture(0)
    instruction = act.get_instruction(current_exercise)
    think.set_instruction(instruction)
    message_label.config(text=instruction)

    # Main loop to process camera frames
    movement_completed = False
    movement_detected = False  # Flag to prevent multiple counts in a single frame
    feedback_message = ""  # Variable to hold feedback message

    with mp_hands.Hands() as hands:
        while cap.isOpened() and not movement_completed:
            ret, frame = cap.read()
            if not ret:
                message_label.config(text="Failed to grab frame")
                break

            # Process hand landmarks
            results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            # Draw landmarks if hand is detected
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    movements = sense.extract_hand_movements(hand_landmarks)
                    think.update_state(movements)

                    # Check if movement is correct
                    if think.decide_movement(movements) and not movement_detected:
                        repetitions_completed -= 1
                        movement_detected = True  # Set the flag to true to indicate a movement has been counted
                        repetition_label.config(text=f"Repetitions left: {repetitions_completed}")
                        feedback_message = act.get_feedback(True)  # Get feedback for correct movement

                        # Check if all repetitions are completed
                        if repetitions_completed <= 0:
                            movement_completed = True
                            message_label.config(text="Exercise completed! Click 'Next Exercise'.")
                            next_button.pack()  # Show the next button when the exercise is completed
                    elif not think.decide_movement(movements):
                        movement_detected = False  # Reset flag if movement was incorrect
                        feedback_message = act.get_feedback(False)  # Get feedback for incorrect movement

            # Create a white banner with 40% opacity
            banner_height = 100
            overlay = frame.copy()
            cv2.rectangle(overlay, (0, 0), (frame.shape[1], banner_height), (255, 255, 255), -1)
            cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)  # Blend the banner with the frame

            # Draw instructions and repetitions on the frame
            cv2.putText(frame, instruction, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(frame, f"Repetitions left: {repetitions_completed}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)

            # Draw feedback message on the right side of the screen
            cv2.putText(frame, feedback_message, (frame.shape[1] - 300, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 0), 2, cv2.LINE_AA)

            # Show camera feed with instruction text
            cv2.imshow('Exercise', frame)

            # Press 'q' to quit the exercise
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

        # Release camera resources and close window for each exercise
        cap.release()
        cv2.destroyAllWindows()


# GUI Setup
root = tk.Tk()
root.title("Exercise Coach")
root.geometry("400x300")
root.configure(bg="white")

# Label to display exercise instructions
message_label = tk.Label(root, text="Welcome to the Exercise Coach!", font=("Arial", 14), bg="white")
message_label.pack(pady=20)

# Repetition counter label
repetition_label = tk.Label(root, text=f"Repetitions left: {required_repetitions}", font=("Arial", 12), bg="white")
repetition_label.pack(pady=10)

# Start Button
start_button = tk.Button(root, text="Start Exercise", font=("Arial", 12), command=start_exercise)
start_button.pack(pady=10)

# Next Button
next_button = tk.Button(root, text="Next Exercise", font=("Arial", 12), command=next_exercise)
next_button.pack_forget()  # Initially hidden

# Clean up on window close
def on_closing():
    if cap and cap.isOpened():
        cap.release()
    cv2.destroyAllWindows()
    root.quit()

root.protocol("WM_DELETE_WINDOW", on_closing)
message_label.config(text="Starting GUI...")  # Initial confirmation message
root.mainloop()
