
from Tool.asm_libraries.loop.loop_base import LoopBase
from Tool.asm_libraries.asm_logger import AsmLogger
from Tool.state_management import get_current_state


class Loop_arm(LoopBase):

    def __enter__(self):
        """
        Called at the start of the 'with' block. Prepares for the loop logic.
        """

        AsmLogger.comment(f"Starting loop with {self.counter} iterations. using a {self.counter_operand} operand and a {self.label} label")
        if self.counter_direction == 'increment':
            AsmLogger.asm(f"mov {self.counter_operand}, #0")
        else: # counter_direction == 'decrement':
            AsmLogger.asm(f"mov {self.counter_operand}, #{self.counter}")
        AsmLogger.asm(f"{self.label}:")
        return self  # Return self to be used in the 'with' block

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Called at the end of the 'with' block. Cleans up any resources or finalizes logic.
        """
        current_state = get_current_state()

        if self.counter_direction == 'increment':
            AsmLogger.asm(f"add {self.counter_operand}, {self.counter_operand}, #1 // Increment the loop counter ({self.counter_operand} += 1)")
            AsmLogger.asm(f"cmp {self.counter_operand}, #{self.counter} //  Compare {self.counter_operand} with {self.counter}")
            AsmLogger.asm(f"bne {self.label}")
        else:  # counter_direction == 'decrement':
            AsmLogger.asm(f"sub {self.counter_operand}, {self.counter_operand}, #1 // Decrement the loop counter ({self.counter_operand} -= 1)")
            AsmLogger.asm(f"cmp {self.counter_operand}, #0 //  Compare {self.counter_operand} with 0")
            AsmLogger.asm(f"bne {self.label}")
        AsmLogger.comment(f"Ending loop")

        if self.counter_type == 'register':
            current_state.register_manager.free(self.counter_operand)

        return False  # False means exceptions are not suppressed
