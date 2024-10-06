class Act:
    def __init__(self):
        self.instructions = [
            "Touch Thumb with Index",  # Updated exercise instructions
            "Touch Thumb with Middle",
            "Touch Thumb with Ring",
            "Touch Thumb with Pinky",
            "Open All Fingers",
            "Close All Fingers",
            "Move Wrist (Fingers to the wrist)"
        ]
        
    def get_instruction(self, index):
        """Retrieve instruction by index."""
        return self.instructions[index]
    
    def get_feedback(self, correct):
        """Provide feedback based on movement correctness."""
        return "Good job!" if correct else "Try again!"
