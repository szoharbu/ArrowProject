from abc import ABC, abstractmethod
from Arrow.Tool.memory_management.memory_segments import CodeSegment
from Arrow.Tool.state_management import get_state_manager
from Arrow.Tool.asm_libraries.label import Label
class BranchToSegmentBase(ABC):
    def __init__(
            self,
            code_segment: CodeSegment,
    ):
        """
        Constructor for the BranchToSegment class.

        Parameters:
        - code_segment (CodeSegment): Defines the code segment to jump to

        Initializes and validates the input parameters.
        """
        state_manager = get_state_manager()
        # Validation for the inputs
        if not isinstance(code_segment, CodeSegment):
            raise ValueError("code_block must be of CodeSegment type.")

        self.code_block = code_segment
        self.prev_code_block = state_manager.get_active_state().current_code_block

        # need to create new label on every such branch
        self.code_label = Label(postfix=f"{self.code_block.name}_branchToSegment_target")

    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

    @abstractmethod
    def one_way_branch(self):
        pass