class Think:
    def __init__(self, act):
        self.act = act
        self.state = None
        self.current_instruction = None  # Stores the current movement instruction

        # Define movement expectations
        self.movement_expectations = {
            "Touch Thumb with Index": lambda movements: movements['thumb_to_index'],
            "Touch Thumb with Middle": lambda movements: movements['thumb_to_middle'],
            "Touch Thumb with Ring": lambda movements: movements['thumb_to_ring'],
            "Touch Thumb with Pinky": lambda movements: movements['thumb_to_pinky'],
            "Open All Fingers": lambda movements: all(movements[finger] for finger in ['index', 'middle', 'ring', 'pinky']),
            "Close All Fingers": lambda movements: not any(movements[finger] for finger in ['index', 'middle', 'ring', 'pinky']),
            "Move Wrist (Fingers to the wrist)": lambda movements: movements['fingers_to_wrist']
        }

    def set_instruction(self, instruction):
        """Set the current instruction (movement type)."""
        self.current_instruction = instruction

    def update_state(self, hand_movements):
        """Update the state based on the detected hand movements."""
        if self.current_instruction in self.movement_expectations:
            is_correct = self.movement_expectations[self.current_instruction](hand_movements)
            self.state = "Correct" if is_correct else "Incorrect"
        else:
            self.state = "No Movement Instruction Given"

    def decide_movement(self, movements):
        """Make a decision about the movement based on expectations."""
        if self.current_instruction in self.movement_expectations:
            return self.movement_expectations[self.current_instruction](movements)
        return False

    def get_state(self):
        return self.state
