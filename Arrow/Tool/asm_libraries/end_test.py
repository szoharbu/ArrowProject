from Arrow.Utils.configuration_management import Configuration
from Arrow.Tool.memory_management.memory import Memory
from Arrow.Tool.asm_libraries.asm_logger import AsmLogger
from Arrow.Tool.asm_libraries.label import Label

def end_test_asm_convention(test_pass:bool=True, status_code=0) -> None:
    """
    Generate assembly code to end a test with agreed status.

    in X86, the flow will use EBX ACED or DEAD
    in RISC-V, the flow will use 'tohost' memory convention
    in ARM, ???

    :param status_code: Status code for the test result.
                        - 0 indicates a pass.
                        - Any non-zero value indicates a failure.
    """

    if test_pass:
        AsmLogger.comment("Test ended successfully")
    else:
        AsmLogger.comment(f"Test failed with error code of {hex(status_code)}")
    AsmLogger.comment("End test logic:")

    if Configuration.Architecture.x86:
        data_value = 0xACED if test_pass else 0xDEAD
        AsmLogger.asm(f"mov ebx, {data_value}", comment=f"Setting {data_value} into EBX register")
        AsmLogger.asm(f"hlt", comment="Halt the processor")
    elif Configuration.Architecture.riscv:
        # Calculate the value to write to `tohost`
        zero_bit = 1
        data_value = (status_code << 1) | zero_bit  # Data[31:1] = status_code, Data[0] = 1 or 0

        # Generate the assembly code
        tohost_memory = Memory(name='tohost')
        end_label = Label(postfix="end_test_label")
        AsmLogger.asm(f"j {end_label}", comment="Jump to end label")

        AsmLogger.asm(f"{end_label}:")
        AsmLogger.asm(f"li t0, {data_value}", comment="Load the value to write to tohost")
        AsmLogger.asm(f"la t1, {tohost_memory.unique_label}", comment="Load address of tohost")
        AsmLogger.asm(f"1: sw t0, 0(t1)", comment="Store the value to tohost")
        AsmLogger.asm(f"j 1b", comment="Halt the processor")
    elif Configuration.Architecture.arm:
        AsmLogger.asm(f"wfi", comment="Wait for interrupt (halts until an interrupt occurs)")
    else:
        raise ValueError(f"Unsupported architecture")