# think.py
class Think:
    def __init__(self, act):
        self.act = act
        self.state = None
        self.current_instruction = None  # Stores the current movement instruction

        # Define movement expectations
        self.movement_expectations = {
            "Touch Thumb to the base of pinky": lambda movements: movements['thumb_to_pinky_mcp'],
            "Touch Thumb with Index": lambda movements: movements['thumb_to_index'],
            "Touch Thumb with Middle": lambda movements: movements['thumb_to_middle'],
            "Touch Thumb with Ring": lambda movements: movements['thumb_to_ring'],
            "Touch Thumb with Pinky": lambda movements: movements['thumb_to_pinky'],
            "Open All Fingers": lambda movements: all(movements[finger] for finger in ['index', 'middle', 'ring', 'pinky']),
            "Close All Fingers": lambda movements: not any(movements[finger] for finger in ['index', 'middle', 'ring', 'pinky']),
            "Move Wrist (Fingers to the wrist)": lambda movements: movements['fingers_to_wrist'] 
        }

    def set_instruction(self, instruction):
        """
        Set the current instruction (movement type).
        """
        self.current_instruction = instruction

    def update_state(self, hand_movements):
        """
        Update the state based on the detected hand movements.
        """
        if self.current_instruction == "Touch Thumb to the base of pinky":
            if hand_movements["thumb_to_pinky_mcp"]:
                self.state = "Correct: Touching Pinky Base"
            else:
                self.state = "Incorrect: Not Touching Pinky Base"
        
        elif self.current_instruction == "Touch Index":
            if hand_movements["thumb_to_index"]:
                self.state = "Correct: Touching Index"
            else:
                self.state = "Incorrect: Not Touching Index"

        elif self.current_instruction == "Touch Middle":
            if hand_movements["thumb_to_middle"]:
                self.state = "Correct: Touching Middle"
            else:
                self.state = "Incorrect: Not Touching Middle"

        elif self.current_instruction == "Touch Ring":
            if hand_movements["thumb_to_ring"]:
                self.state = "Correct: Touching Ring"
            else:
                self.state = "Incorrect: Not Touching Ring"

        elif self.current_instruction == "Touch Pinky":
            if hand_movements["thumb_to_pinky"]:
                self.state = "Correct: Touching Pinky"
            else:
                self.state = "Incorrect: Not Touching Pinky"

        elif self.current_instruction == "Open Fingers":
            if all(hand_movements[finger] for finger in ["index", "middle", "ring", "pinky"]):
                self.state = "Correct: Fingers Open"
            else:
                self.state = "Incorrect: Fingers Not Open"

        elif self.current_instruction == "Close Fingers":
            if not any(hand_movements[finger] for finger in ["index", "middle", "ring", "pinky"]):
                self.state = "Correct: Fingers Closed"
            else:
                self.state = "Incorrect: Fingers Not Closed"

        elif self.current_instruction == "Move Wrist (Fingers to the wrist)":
            if hand_movements["fingers_to_wrist"]:
                self.state = "Correct: Fingers to Wrist"
            else:
                self.state = "Incorrect: Fingers Not to Wrist"

        else:
            self.state = "No Movement Instruction Given"

    def decide_movement(self, movements):
        """
        Make a decision about the movement based on expectations.
        Returns True if the movement is correct, else False.
        """
        if self.current_instruction in self.movement_expectations:
            return self.movement_expectations[self.current_instruction](movements)
        return False

    def get_state(self):
        return self.state
