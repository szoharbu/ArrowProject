
from Arrow.Tool.asm_libraries.event_trigger.event_trigger_base import EventTriggerBase
from Arrow.Tool.register_management.register import Register
from Arrow.Tool.asm_libraries.asm_logger import AsmLogger
# from Arrow.Tool.frontend.sources_API import Sources
from Arrow.Tool.state_management import get_current_state


class EventTrigger_arm(EventTriggerBase):

    def __enter__(self):
        """
        Called at the start of the 'with' block. Prepares for the loop logic.
        """

        current_state = get_current_state()
        register_manager = current_state.register_manager

        address_reg = register_manager.get_and_reserve(reg_type = "gpr")
        AsmLogger.asm(f"ldr {address_reg}, ={hex(self.memory_with_pattern.get_address())}") # Rotate bits to influence c
        AsmLogger.asm(f"ldr {self.operand}, [{address_reg}]", comment=f"load the vector from mem {hex(self.memory_with_pattern.get_address())}")
        AsmLogger.asm(f"ror {self.operand}, {self.operand}, #1", comment="rotate the vector") 
        AsmLogger.asm(f"str {self.operand}, [{address_reg}]", comment="store back the vector into the memory location")
        AsmLogger.asm(f"tbz {self.operand}, #63, {self.label}", comment="test bit 63 and branch if 0 (zero)")
        register_manager.free(address_reg)
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
