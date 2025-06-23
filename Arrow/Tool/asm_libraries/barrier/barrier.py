from typing import Optional

#from Arrow.Tool.asm_libraries.barrier.barrier_base import BarrierBase
#from Arrow.Tool.asm_libraries.barrier.barrier_x86 import Barrier_x86
#from Arrow.Tool.asm_libraries.barrier.barrier_riscv import Barrier_riscv
from Arrow.Tool.asm_libraries.barrier.barrier_arm import barrier_arm
from Arrow.Utils.configuration_management import Configuration

def Barrier(
        barrier_name: str,
):
    """Configure Barrier with the desired architecture (Arm, riscv, x86)."""

    if Configuration.Architecture.x86:
        raise ValueError(f"x86 architecture barrier is currently not implemented")
        # barrier_instance = Barrier_x86
    elif Configuration.Architecture.riscv:
        raise ValueError(f"riscv architecture barrier is currently not implemented")
        # barrier_instance = Barrier_riscv
    elif Configuration.Architecture.arm:
        barrier_arm(barrier_name)
        #barrier_instance = Barrier_arm
    else:
        raise ValueError(f"Unknown Architecture requested")

    #return barrier_instance(barrier_name)  # Return an instance of the barrier class

