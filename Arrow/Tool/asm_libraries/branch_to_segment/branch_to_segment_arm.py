
from ....Tool.asm_libraries.branch_to_segment.branch_to_segment import BranchToSegmentBase
from ....Tool.state_management.switch_state import switch_code
from ....Tool.asm_libraries.asm_logger import AsmLogger


class BranchToSegment_arm(BranchToSegmentBase):
    def __enter__(self):
        """
        Called at the start of the 'with' block. setting the code block and jump there.
        """

        AsmLogger.comment(f"branch with link `label` by jumping to code segment {self.code_block.name} and storing the return address in `LR` (Link Register) register")
        AsmLogger.asm(f"bl {self.code_label}", comment="Branch with Link to target address")
        switch_code(self.code_block)
        AsmLogger.asm(f"{self.code_label}:")

        return self  # Return self to be used in the 'with' block

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Called at the end of the 'with' block. Jumping back to previous code block.
        """
        AsmLogger.comment(f"Return to the previous code segment {self.prev_code_block.name} using the address in `LR` (similar to `ret stack` in x86)")
        AsmLogger.asm(f"RET", comment ="Returns from a function using the LR (x30) register.")
        switch_code(self.prev_code_block)

        return False  # False means exceptions are not suppressed

    def one_way_branch(self):
        """
        Called as a standalone without a 'with' scope, will do a one-way jump.
        """

        AsmLogger.comment(f"using 'B' (branch) for unconditional 'one-way' branch (similar to jmp) to code segment {self.code_block.name}")
        AsmLogger.asm(f"B {self.code_label}", comment="Jump to code_label ")
        switch_code(self.code_block)
        AsmLogger.asm(f"{self.code_label}:")

        return self  # Return self to be used in the 'with' block
