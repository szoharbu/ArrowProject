
from ....Tool.asm_libraries.asm_logger import AsmLogger
from ....Tool.asm_libraries.branch_to_segment.branch_to_segment import BranchToSegmentBase
from ....Tool.state_management import get_state_manager
from ....Tool.state_management.switch_state import switch_code

class BranchToSegment_riscv(BranchToSegmentBase):
    def __enter__(self):
        """
        Called at the start of the 'with' block. setting the code block and jump there.
        """
        state_manager = get_state_manager()
        curr_state = state_manager.get_active_state()
        current_code_block = curr_state.current_code_block

        AsmLogger.comment(f"Call `label` by jumping from '{current_code_block.name}' to '{self.code_block.name}' code segment and storing the return address in `ra` (return_address) register")
        AsmLogger.asm(f"jal ra, {self.code_label}")
        switch_code(self.code_block)
        AsmLogger.asm(f"{self.code_label}:")

        return self  # Return self to be used in the 'with' block

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Called at the end of the 'with' block. Jumping back to previous code block.
        """
        AsmLogger.comment(f"Return to the previous code segment {self.prev_code_block.name} using the address in `ra` (similar to `ret` in x86)")
        AsmLogger.asm(f"jr ra")
        switch_code(self.prev_code_block)

        return False  # False means exceptions are not suppressed

    def one_way_branch(self):
        """
        Called as a standalone without a 'with' scope, will do a one-way jump.
        """

        '''
        use the jal (Jump and Link) instruction with the x0 register as the destination. 
        The x0 register in RISC-V is the zero register, which discards any value written to it, 
        making jal x0, target_label effectively a one-way jump.
        '''
        AsmLogger.comment(f"using 'jal' with x0 to branch 'one-way' (similar to jmp) to code segment {self.code_block.name}")
        AsmLogger.asm(f"jal x0, {self.code_label}   # Unconditional jump to target_label")
        switch_code(self.code_block)
        AsmLogger.asm(f"{self.code_label}:")

        return self  # Return self to be used in the 'with' block
