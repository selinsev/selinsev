import os
import tkinter as tk
import cv2
import mediapipe as mp
import Act, Sense, Think
from FingerCounting import FingerCounter
from WaveDetection_Right import WaveDetector
from FullGrip import GripDetector
import time

# Suppress TensorFlow Lite warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Initialize MediaPipe hands and drawing utils
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Initialize components
sense = Sense.Sense()
act = Act.Act()
think = Think.Think(act)
wave_detector = WaveDetector()
full_grip_detector = GripDetector()
finger_counter = FingerCounter()

# Flags to track exercise state
current_exercise = 0
current_level = 1
cap = None
required_repetitions = 3
repetitions_completed = 0
draw_interval = 5
finger_sequence = [0, 1, 2, 3, 4, 5]


def start_exercise():
    global current_exercise, repetitions_completed, current_level, finger_sequence
    current_exercise = 0
    repetitions_completed = 0
    current_level = 1
    finger_sequence = [0, 1, 2, 3, 4, 5]  # Reset the finger sequence
    message_label.config(text="Starting Level 1")
    start_button.pack_forget()
    root.after(500, run_exercise)


def next_exercise():
    global current_exercise, repetitions_completed, current_level
    current_exercise += 1
    repetitions_completed = 0

    if current_level == 1:
        if current_exercise < 6:
            message_label.config(text=f"Starting Level 1 Exercise {current_exercise + 1}...")
            root.after(500, run_exercise)
        else:
            current_level = 2
            current_exercise = 0
            message_label.config(text="Level 1 complete! Moving to Level 2: Wave, Grip, Finger Counting...")
            root.after(500, run_exercise)
    else:
        if current_exercise < 3:
            message_label.config(text=f"Starting Level 2 Exercise {current_exercise + 1}...")
            root.after(500, run_exercise)
        else:
            message_label.config(text="All exercises are complete!")
            next_button.pack_forget()


def run_exercise():
    global cap, repetitions_completed, current_level, current_exercise

    if current_level == 1 and current_exercise >= 6 or current_level == 2 and current_exercise >= 3:
        message_label.config(text="All exercises are complete!")
        return

    if cap is None or not cap.isOpened():
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
        cap.set(cv2.CAP_PROP_FPS, 15)

    if not cap.isOpened():
        message_label.config(text="Error: Camera not detected.")
        return

    movement_completed = False
    feedback_message = ""

    with mp_hands.Hands(max_num_hands=1) as hands:
        while cap.isOpened() and not movement_completed:
            ret, frame = cap.read()
            if not ret:
                message_label.config(text="Failed to grab frame")
                break

            results = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            if current_level == 1:
                movement_completed, feedback_message = run_level1_exercise(frame, results)
            elif current_level == 2:
                movement_completed, feedback_message = run_level2_exercise(frame)

            cv2.putText(frame, f"Level {current_level} Exercise {current_exercise + 1}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(frame, f"Repetitions left: {len(finger_sequence) - repetitions_completed}", (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.putText(frame, feedback_message, (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2,
                        cv2.LINE_AA)

            cv2.imshow('Exercise', frame)

            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

    if movement_completed:
        message_label.config(text="Exercise completed! Click 'Next Exercise'.")
        next_button.pack()
    else:
        root.after(10, run_exercise)


def run_level1_exercise(frame, results):
    global repetitions_completed
    current_instruction = act.get_instruction(current_exercise)

    if results.multi_hand_landmarks:
        movements = sense.extract_hand_movements(results.multi_hand_landmarks[0])
        think.set_instruction(current_instruction)
        think.update_state(movements)
        feedback_message = act.get_feedback(think.get_state() == "Correct")

        if think.get_state() == "Correct":
            repetitions_completed += 1

    return repetitions_completed >= required_repetitions, current_instruction


def run_level2_exercise(frame):
    global repetitions_completed, finger_sequence

    feedback_message = ""

    if current_exercise == 0:
        # Wave Detection
        wave_detected = wave_detector.detectWave(frame)
        feedback_message = "Wave detected!" if wave_detected else "Keep waving..."
        if wave_detected:
            repetitions_completed += 1
    elif current_exercise == 1:
        # Full Grip Detection
        lmList = full_grip_detector.lmlist(frame)
        if lmList:
            grip_detected = full_grip_detector.detectFullGrip(lmList)
            feedback_message = "Grip detected!" if grip_detected else "Try to make a full grip..."
            if grip_detected:
                repetitions_completed += 1
    elif current_exercise == 2:
        # Finger Counting
        FingerCounter.run()


# GUI Setup
root = tk.Tk()
root.title("Exercise Coach")
root.geometry("400x300")
root.configure(bg="#f0f0f0")

message_label = tk.Label(root, text="Welcome to the Exercise Coach!", font=("Arial", 14, "bold"), bg="#f0f0f0")
message_label.pack(pady=20)

start_button = tk.Button(root, text="Start Exercise", font=("Arial", 12), command=start_exercise, bg="#4CAF50",
                         fg="white")
start_button.pack(pady=10)

next_button = tk.Button(root, text="Next Exercise", font=("Arial", 12), command=next_exercise, bg="#008CBA", fg="white")
next_button.pack_forget()


def on_closing():
    if cap and cap.isOpened():
        cap.release()
    cv2.destroyAllWindows()
    root.quit()


root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()