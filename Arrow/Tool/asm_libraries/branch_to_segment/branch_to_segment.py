
from ....Tool.memory_management.memory_segments import CodeSegment
from ....Tool.asm_libraries.branch_to_segment.branch_to_segment_base import BranchToSegmentBase
from ....Tool.asm_libraries.branch_to_segment.branch_to_segment_x86 import BranchToSegment_x86
from ....Tool.asm_libraries.branch_to_segment.branch_to_segment_riscv import BranchToSegment_riscv
from ....Tool.asm_libraries.branch_to_segment.branch_to_segment_arm import BranchToSegment_arm
from ....Utils.configuration_management import Configuration


def BranchToSegment(code_block: CodeSegment) -> BranchToSegmentBase:
    """Configure BranchToSegment with the desired architecture (Arm, riscv, x86)."""
    if Configuration.Architecture.x86:
        branch_instance = BranchToSegment_x86
    elif Configuration.Architecture.riscv:
        branch_instance = BranchToSegment_riscv
    elif Configuration.Architecture.arm:
        branch_instance = BranchToSegment_arm
    else:
        raise ValueError(f"Unknown Architecture requested")

    return branch_instance(code_block)  # Return an instance of the branch_to_segment class

