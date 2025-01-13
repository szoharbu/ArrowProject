
from Tool.asm_libraries.event_trigger.event_trigger_base import EventTriggerBase
from Tool.register_management.register import Register
from Tool.asm_libraries.asm_logger import AsmLogger


class EventTrigger_arm(EventTriggerBase):

    def __enter__(self):
        """
        Called at the start of the 'with' block. Prepares for the loop logic.
        """

        AsmLogger.print_comment_line(f"Setting event trigger flow with {self.frequency} frequency ")

        #if isinstance(self.operand, Register):
        #    AsmLogger.print_asm_line(f"ldr {self.operand}, {self.memory_with_pattern} // Load the value from memory location into register {self.operand}")
        AsmLogger.print_asm_line(f"ror {self.operand}, {self.operand}, #1") # Rotate bits to influence chance
        AsmLogger.print_asm_line(f"cmp {self.operand}, #0")  # Rotate bits to influence chance
        AsmLogger.print_asm_line(f"bne {self.label} // If {self.operand} is not zero, branch to 'skip_label'") # Skip inner code if mem is non-zero

        return self  # Return self to be used in the 'with' block

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Called at the end of the 'with' block. Cleans up any resources or finalizes logic.
        """
        AsmLogger.print_asm_line(f"{self.label}:") # Assembly label for exiting the block

        if isinstance(self.operand, Register):
            # freeing the reserved register
            Sources.RegisterManager.free(self.operand)

        return False  # False means exceptions are not suppressed
