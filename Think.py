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
        }

    def set_instruction(self, instruction):
        """Set the current movement instruction."""
        self.current_instruction = instruction

    def update_state(self, hand_movements):
        """Update the internal state based on the detected hand movements."""
        self.state = "Correct" if self.decide_movement(hand_movements) else "Incorrect"

    def decide_movement(self, movements):
        """Check if the detected movement matches the current instruction."""
        if self.current_instruction and self.current_instruction in self.movement_expectations:
            return self.movement_expectations[self.current_instruction](movements)
        return False

    def get_state(self):
        """Retrieve the current state ('Correct' or 'Incorrect')."""
        return self.state
