from typing import Optional

from Tool.asm_libraries.loop.loop_base import LoopBase
from Tool.asm_libraries.loop.loop_x86 import Loop_x86
from Tool.asm_libraries.loop.loop_riscv import Loop_riscv
from Tool.asm_libraries.loop.loop_arm import Loop_arm
from Utils.configuration_management import Configuration

def Loop(
        counter: int,
        counter_type: Optional[str] = None,
        counter_direction: Optional[str] = None,
        label: Optional[str] = None,
        additional_param: Optional[int] = None
) -> LoopBase:
    """Configure Loop with the desired architecture (Arm, riscv, x86)."""

    if Configuration.Architecture.x86:
        loop_instance = Loop_x86
    elif Configuration.Architecture.riscv:
        loop_instance = Loop_riscv
    elif Configuration.Architecture.arm:
        loop_instance = Loop_arm
    else:
        raise ValueError(f"Unknown Architecture requested")

    return loop_instance(counter, counter_type,counter_direction,label)  # Return an instance of the loop class

