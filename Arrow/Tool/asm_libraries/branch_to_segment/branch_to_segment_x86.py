
from Tool.asm_libraries.branch_to_segment.branch_to_segment import BranchToSegmentBase
from Tool.state_management.switch_state import switch_code
from Tool.asm_libraries.asm_logger import AsmLogger

class BranchToSegment_x86(BranchToSegmentBase):
    def __enter__(self):
        """
        Called at the start of the 'with' block. setting the code block and jump there.
        """

        AsmLogger.comment(f"using 'call' to branch to code segment {self.code_block.name}")

        AsmLogger.asm(f"call {self.code_label}")
        switch_code(self.code_block)
        AsmLogger.asm(f"{self.code_label}:")

        return self  # Return self to be used in the 'with' block

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Called at the end of the 'with' block. Jumping back to previous code block.
        """
        AsmLogger.comment(f"using 'ret' to return back to code segment {self.prev_code_block.name}")

        AsmLogger.asm(f"ret")
        switch_code(self.prev_code_block)

        return False  # False means exceptions are not suppressed

    def one_way_branch(self):
        # Code for standalone function execution

        AsmLogger.comment(f"using 'jmp' to branch to code segment {self.code_block.name}")
        AsmLogger.asm(f"jmp {self.code_label}")
        switch_code(self.code_block)
        AsmLogger.asm(f"{self.code_label}:")

        return self  # Return self to be used in the 'with' block
