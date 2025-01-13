from Tool.asm_libraries.loop.loop_base import LoopBase
from Tool.asm_libraries.asm_logger import AsmLogger

import Tool


class Loop_x86(LoopBase):

    def __enter__(self):
        """
        Called at the start of the 'with' block. Prepares for the loop logic.
        """

        AsmLogger.print_comment_line(f"Starting loop with {self.counter} iterations. using a {self.counter_operand} operand and a {self.label} label")
        if self.counter_direction == 'increment':
            AsmLogger.print_asm_line(f"mov {self.counter_operand}, 0")
        else: # counter_direction == 'decrement':
            AsmLogger.print_asm_line(f"mov {self.counter_operand}, {self.counter}")
        AsmLogger.print_asm_line(f"{self.label}:")
        return self  # Return self to be used in the 'with' block

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Called at the end of the 'with' block. Cleans up any resources or finalizes logic.
        """
        if self.counter_direction == 'increment':
            AsmLogger.print_asm_line(f"inc {self.counter_operand}")
            AsmLogger.print_asm_line(f"cmp {self.counter_operand}, {self.counter}")
            AsmLogger.print_asm_line(f"jl {self.label}")
        else:  # counter_direction == 'decrement':
            AsmLogger.print_asm_line(f"dec {self.counter_operand}")
            AsmLogger.print_asm_line(f"jnz {self.label}")
        AsmLogger.print_comment_line(f"Ending loop")

        if self.counter_type == 'register':
            Tool.RegisterManager.free(self.counter_operand)

        return False  # False means exceptions are not suppressed
