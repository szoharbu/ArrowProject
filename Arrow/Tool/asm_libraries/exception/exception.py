from typing import Optional

from Arrow.Tool.exception_management import get_exception_manager, AArch64ExceptionVector, AArch64ExceptionSyndrome
from Arrow.Tool.asm_libraries.exception.exception_base import ExceptionBase
#from Arrow.Tool.asm_libraries.exception.exception_x86 import Exception_x86
#from Arrow.Tool.asm_libraries.exception.exception_riscv import Exception_riscv
from Arrow.Tool.asm_libraries.exception.exception_arm import Exception_arm
from Arrow.Utils.configuration_management import Configuration

def Exception(
        exception_type: AArch64ExceptionVector,
        exception_syndrome: Optional[AArch64ExceptionSyndrome] = None,
        handler: Optional[str] = None,
        callback: Optional[str] = None,
) -> ExceptionBase:
    """Configure Exception with the desired architecture (Arm, riscv, x86)."""

    if Configuration.Architecture.x86:
        raise ValueError(f"x86 is not supported yet")
        #exception_instance = Exception_x86
    elif Configuration.Architecture.riscv:
        raise ValueError(f"riscv is not supported yet")
        #exception_instance = Exception_riscv
    elif Configuration.Architecture.arm:
        exception_instance = Exception_arm
    else:
        raise ValueError(f"Unknown Architecture requested")

    return exception_instance(exception_type, exception_syndrome, handler, callback)  # Return an instance of the exception class

