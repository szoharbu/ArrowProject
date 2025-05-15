from Arrow.Tool.asm_libraries.asm_logger import AsmLogger
from Arrow.Utils.configuration_management import Configuration
from Arrow.Tool.register_management.register import Register
from Arrow.Tool.memory_management.memory import Memory
from Arrow.Tool.state_management import get_state_manager


def load_value(memory: Memory, register: Register) -> None:
    """
    Generates assembly code to load a value from a memory label into a register for a given architecture.

    :param memory: The memory to load the value from.
    :param register: The name of the register to load the value into.
    """
    state_manager = get_state_manager()
    current_state = state_manager.get_active_state()

    if Configuration.Architecture.x86:
        AsmLogger.asm(f"mov {register}, [{memory.unique_label}]", comment=f"Load value from {memory.name} into {register}")
    elif Configuration.Architecture.arm:
        tmp_reg = current_state.register_manager.get_and_reserve()
        AsmLogger.asm(f"ldr {tmp_reg}, ={memory.unique_label}", comment=f"Load address from {memory.name} into {register}")
        AsmLogger.asm(f"ldr {register}, [{tmp_reg}]", comment=f"Dereference to load value")
        current_state.register_manager.free(tmp_reg)
    elif Configuration.Architecture.riscv:
        tmp_reg = current_state.register_manager.get_and_reserve()
        AsmLogger.asm(f"la {tmp_reg}, {memory.unique_label}", comment=f"Load address from {memory.name} into {register}")
        AsmLogger.asm(f"lw {register}, 0({tmp_reg})", comment=f"Dereference to load value")
        current_state.register_manager.free(tmp_reg)
    else:
        raise ValueError(f"Unsupported architecture")


def store_value(memory: Memory, register: str) -> None:
    """
    Generates assembly code to store a value from a register into a memory label for a given architecture.

    :param memory: The memory to store the value into.
    :param register: The name of the register containing the value to store.
    """
    state_manager = get_state_manager()
    current_state = state_manager.get_active_state()

    if Configuration.Architecture.x86:
        AsmLogger.asm(f"mov [{memory.unique_label}], {register}", comment=f"Store value from {register} into {memory.name}")
    elif Configuration.Architecture.arm:
        tmp_reg = current_state.register_manager.get_and_reserve()
        AsmLogger.asm(f"ldr {tmp_reg}, ={memory.unique_label}", comment=f"Load address of {memory.name} into temporary register {tmp_reg} ")
        AsmLogger.asm(f"str {register}, [{tmp_reg}]", comment=f"Store value from {register} into memory")
        current_state.register_manager.free(tmp_reg)
    elif Configuration.Architecture.riscv:
        tmp_reg = current_state.register_manager.get_and_reserve()
        AsmLogger.asm(f"la {tmp_reg}, {memory.unique_label}", comment=f"Load address from {memory.name} into temporary {tmp_reg}")
        AsmLogger.asm(f"sw {register}, 0({tmp_reg})", comment=f"Store value from {register} into memory")
        current_state.register_manager.free(tmp_reg)
    else:
        raise ValueError(f"Unsupported architecture")

