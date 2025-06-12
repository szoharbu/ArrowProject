
from Tool.asm_libraries.event_trigger.event_trigger_base import EventTriggerBase
from Tool.register_management.register import Register
from Tool.asm_libraries.asm_logger import AsmLogger
from Tool.state_management import get_current_state


class EventTrigger_x86(EventTriggerBase):

    def __enter__(self):
        """
        Called at the start of the 'with' block. Prepares for the loop logic.
        """

        if isinstance(self.operand, Register):
            AsmLogger.asm(f"mov {self.operand}, {self.memory_with_pattern}")  # loading the pattern from a memory operand
        AsmLogger.asm(f"ror {self.operand}, 1") # Rotate bits to influence chance
        AsmLogger.asm(f"jnz {self.label}") # Skip inner code if mem is non-zero

        return self  # Return self to be used in the 'with' block

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Called at the end of the 'with' block. Cleans up any resources or finalizes logic.
        """
        current_state = get_current_state()

        AsmLogger.asm(f"{self.label}:") # Assembly label for exiting the block

        if isinstance(self.operand, Register):
            # freeing the reserved register
            current_state.register_manager.free(self.operand)

        return False  # False means exceptions are not suppressed
