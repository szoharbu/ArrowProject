from Utils.configuration_management import Configuration
from Tool.memory_management.memory import Memory
from Tool.asm_libraries.asm_logger import AsmLogger
from Tool.asm_libraries.label import Label

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
        AsmLogger.print_comment_line("Test ended successfully")
    else:
        AsmLogger.print_comment_line(f"Test failed with error code of {hex(status_code)}")
    AsmLogger.print_comment_line("End test logic:")

    if Configuration.Architecture.x86:
        data_value = 0xACED if test_pass else 0xDEAD
        AsmLogger.print_asm_line(f"mov ebx, {data_value}", comment=f"Setting {data_value} into EBX register")
        AsmLogger.print_asm_line(f"hlt", comment="Halt the processor")
    elif Configuration.Architecture.riscv:
        # Calculate the value to write to `tohost`
        zero_bit = 0 if test_pass else 1
        data_value = (status_code << 1) | zero_bit  # Data[31:1] = status_code, Data[0] = 1 or 0

        # Generate the assembly code
        tohost_memory = Memory(name='tohost')
        end_label = Label(postfix="end_test_label")
        AsmLogger.print_asm_line(f"li t0, {data_value}", comment="Load the value to write to tohost")
        AsmLogger.print_asm_line(f"la t1, {tohost_memory.unique_label}", comment="Load address of tohost")
        AsmLogger.print_asm_line(f"sw t0, 0(t1)", comment="Store the value to tohost")
        AsmLogger.print_asm_line(f"j {end_label}", comment="Jump to end label")

        AsmLogger.print_asm_line(f"{end_label}:")
        AsmLogger.print_asm_line(f"ebreak", comment="Halt the processor")
    elif Configuration.Architecture.arm:
        AsmLogger.print_asm_line(f"wfi", comment="Wait for interrupt (halts until an interrupt occurs)")
    else:
        raise ValueError(f"Unsupported architecture")