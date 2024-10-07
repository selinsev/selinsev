import pygame
import random

class Act:
    def __init__(self):
        # Initialize pygame mixer for sound playback
        pygame.mixer.init()

        # Load sound files
        self.correct_sound = pygame.mixer.Sound("E:\selinsev\correct_sound.mp3")  # Path to correct sound
        self.incorrect_sound = pygame.mixer.Sound("E:\selinsev\wrong_sound.mp3")  # Path to incorrect sound

        self.instructions = [
            "Touch Thumb with Index",
            "Touch Thumb with Middle",
            "Touch Thumb with Ring",
            "Touch Thumb with Pinky",
            "Open All Fingers",
            "Close All Fingers",
        ]

        # Lists of feedback for correct and incorrect actions
        self.positive_feedback = [
            "Fantastic! You're doing great!",
            "Excellent work, keep it up!",
            "Well done! You've got this!",
            "Perfect! Keep up the awesome effort!"
        ]

        self.negative_feedback = [
            "Oops! Make sure your thumb touches your index finger.",
            "Try again! Ensure your fingers are fully open.",
            "Not quite! Try closing your fingers all the way.",
            "Almost there! Ensure your middle finger is touching your thumb."
        ]

    def get_instruction(self, index):
        """Retrieve instruction by index."""
        return self.instructions[index]

    def get_feedback(self, correct, action_index):
        """
        Provide feedback based on movement correctness.
        :param correct: Boolean, True if the action was correct, False otherwise.
        :param action_index: The index of the current action to provide specific feedback.
        :return: A motivational feedback message.
        """
        # Play sound based on correctness
        if correct:
            self.correct_sound.play()
            # Random motivational message for correct actions
            feedback_message = random.choice(self.positive_feedback)
        else:
            self.incorrect_sound.play()
            # Specific feedback for the action, combined with a motivational tip
            feedback_message = self.negative_feedback[action_index]

        return feedback_message

# Example of usage
if __name__ == "__main__":
    act = Act()
    instruction_index = 0  # Example instruction index

    print(act.get_instruction(instruction_index))  # Get first instruction
    print(act.get_feedback(True, instruction_index))  # Simulate correct action
    print(act.get_feedback(False, instruction_index))  # Simulate incorrect action
