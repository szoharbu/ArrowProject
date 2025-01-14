
from Tool.asm_libraries.loop.loop_base import LoopBase
from Tool.asm_libraries.asm_logger import AsmLogger
# from Tool.frontend.sources_API import Sources
from Tool.state_management import get_state_manager


class Loop_riscv(LoopBase):

    def __enter__(self):
        """
        Called at the start of the 'with' block. Prepares for the loop logic.
        """
        state_manager = get_state_manager()
        current_state = state_manager.get_active_state()

        self.counter_operand = current_state.register_manager.get_and_reserve()

        AsmLogger.comment(f"Starting loop with {self.counter} iterations. using a {self.counter_operand} operand and a {self.label} label")
        if self.counter_direction == 'increment':
            AsmLogger.asm(f"li {self.counter_operand}, 0x0  # Load immediate value 0x0 into {self.counter_operand} (counter)")
        else: # counter_direction == 'decrement':
            AsmLogger.asm(f"li {self.counter_operand}, {self.counter}  # Load immediate value {self.counter} into {self.counter_operand} (counter)")
        AsmLogger.asm(f"{self.label}:")

        return self  # Return self to be used in the 'with' block

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Called at the end of the 'with' block. Cleans up any resources or finalizes logic.
        """
        state_manager = get_state_manager()
        current_state = state_manager.get_active_state()

        if self.counter_direction == 'increment':
            limit_register = current_state.register_manager.get_and_reserve()
            AsmLogger.asm(f"addi {self.counter_operand}, {self.counter_operand}, 1", comment="increment the counter by 1")
            AsmLogger.asm(f"li {limit_register}, {self.counter + 1}", comment=f"Load immediate value {self.counter + 1} as loop limit")
            AsmLogger.asm(f"blt {self.counter_operand}, {limit_register}, {self.label}  # Branch back if {self.counter_operand} < {self.counter + 1}")
            # AsmLogger.print_asm_line(f"blt {tmp_counter_operand}, {self.counter+1}, {self.label}  # Branch back if {tmp_counter_operand} < {self.counter}+1 (meaning {tmp_counter_operand} <= 10)")
        else:  # counter_direction == 'decrement':
            AsmLogger.asm(f"addi {self.counter_operand}, {self.counter_operand}, -1  # Decrement the counter by 1")
            AsmLogger.asm(f"bgtz {self.counter_operand}, {self.label}  # Branch back to loop if {self.counter_operand} > 0")
        AsmLogger.comment(f"Ending loop")

        if self.counter_type == 'register':
            current_state.register_manager.free(self.counter_operand)

        return False  # False means exceptions are not suppressed
