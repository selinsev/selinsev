# act.py
class Act:
    def __init__(self):
        # List of possible instructions
        self.instructions = [
            "Touch Thumb to the base of pinky",
            "Touch Thumb with Index",
            "Touch Thumb with Middle",
            "Touch Thumb with Ring",
            "Touch Thumb with Pinky",
            "Open All Fingers",
            "Close All Fingers",
            "Move Wrist (Fingers to the wrist)"
        ]

    def get_instruction(self, index):
        return self.instructions[index] if index < len(self.instructions) else None

