import tkinter as tk
import time
import random

class TypingPractice:
    def __init__(self, root):
        self.root = root
        self.root.title("Typing Practice for Stroke Rehabilitation")

        # List of sentences for practice
        self.sentences = [
            "The quick brown fox jumps over the lazy dog",
            "A journey of a thousand miles begins with a single step",
            "To be or not to be, that is the question",
            "Practice makes perfect",
            "Better late than never",
            "Actions speak louder than words",
            "Every cloud has a silver lining",
        ]
        self.current_sentence = ""
        self.start_time = None
        self.user_input = tk.StringVar()

        # Display the target text
        self.label = tk.Label(root, text="", font=("Helvetica", 14))
        self.label.pack(pady=20)

        # Input field where the user will type
        self.entry = tk.Entry(root, textvariable=self.user_input, font=("Helvetica", 14), width=50)
        self.entry.pack(pady=10)
        self.entry.bind("<KeyRelease>", self.check_typing)

        # Label to show feedback and speed
        self.feedback_label = tk.Label(root, text="", font=("Helvetica", 12))
        self.feedback_label.pack(pady=20)

        # Start button
        self.start_button = tk.Button(root, text="Start Typing", command=self.start_typing)
        self.start_button.pack(pady=10)

    def start_typing(self):
        """Start the typing exercise"""
        self.user_input.set("")
        self.start_time = time.time()

        # Select a new sentence randomly
        self.current_sentence = random.choice(self.sentences)
        self.label.config(text=self.current_sentence)
        self.feedback_label.config(text="Start typing now...")

    def check_typing(self, event):
        """Check user typing and provide feedback"""
        if self.start_time is None:
            return  # Ignore key presses until the user starts the exercise

        typed_text = self.user_input.get()

        # Check if typing is complete
        if typed_text == self.current_sentence:
            elapsed_time = time.time() - self.start_time
            speed = len(self.current_sentence) / elapsed_time * 60  # characters per minute (CPM)
            self.feedback_label.config(
                text=f"Great! You completed in {elapsed_time:.2f} seconds at {speed:.2f} CPM."
            )
            # Show a button to allow retrying with a new sentence
            self.start_button.config(text="Type Another Sentence", command=self.start_typing)
        elif not self.current_sentence.startswith(typed_text):
            self.feedback_label.config(text="Error: Typing does not match the target text.")
        else:
            self.feedback_label.config(text="Keep going...")

if __name__ == "__main__":
    root = tk.Tk()
    app = TypingPractice(root)
    root.mainloop()
