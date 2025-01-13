
from Tool.asm_libraries.event_trigger.event_trigger_base import EventTriggerBase
from Tool.register_management.register import Register
from Tool.asm_libraries.asm_logger import AsmLogger


class EventTrigger_riscv(EventTriggerBase):

    def __enter__(self):
        """
        Called at the start of the 'with' block. Prepares for the loop logic.
        """
        AsmLogger.print_comment_line(f"Setting event trigger flow with {self.frequency} frequency ")

        if isinstance(self.operand, Register):
            # TODO:: the memory operand here need to be replaced with two operands base_reg + offset
            AsmLogger.print_asm_line(f"lw {self.operand}, {self.memory_with_pattern}")  # loading the pattern from a memory operand
        AsmLogger.print_asm_line(f"ror {self.operand}, {self.operand}, 1") # Rotate bits to influence chance
        AsmLogger.print_asm_line(f"bnez {self.operand}, {self.label}") # If reg != 0 (non-zero), jump to skip_label

        return self  # Return self to be used in the 'with' block

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Called at the end of the 'with' block. Cleans up any resources or finalizes logic.
        """
        AsmLogger.print_asm_line(f"{self.label}:") # Assembly label for exiting the block

        return False  # False means exceptions are not suppressed
