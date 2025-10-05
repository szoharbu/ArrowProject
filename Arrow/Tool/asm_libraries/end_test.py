from Arrow.Utils.configuration_management import Configuration
from Arrow.Tool.memory_management.memory_operand import Memory
from Arrow.Tool.state_management import get_current_state
from Arrow.Tool.asm_libraries.asm_logger import AsmLogger
from Arrow.Tool.asm_libraries.label import Label
from Arrow.Tool.asm_libraries.barrier.barrier import Barrier
from Arrow.Utils.logger_management import get_logger
from Arrow.Tool.state_management import get_state_manager

# Singleton/static variable for tohost memory
_tohost_memory_instance = None
end_test_barrier_label = None

def get_tohost_memory():
    """
    Get the singleton tohost memory instance.
    Creates it only once and returns the same instance on subsequent calls.
    """
    global _tohost_memory_instance
    if _tohost_memory_instance is None:
        # TODO control which state this gets associated with, doesn't matter for now
        _tohost_memory_instance = Memory(name='tohost', _use_name_as_unique_label=True)
    return _tohost_memory_instance

def end_test_asm_convention(test_pass: bool = True, status_code=0) -> None:
    """
    Generate assembly code to end a test with agreed status.

    in X86, the flow will use EBX ACED or DEAD
    in RISC-V, the flow will use 'tohost' memory convention
    in ARM, ???

    :param status_code: Status code for the test result.
                        - 0 indicates a pass.
                        - Any non-zero value indicates a failure.
    """

    current_state = get_current_state()
    register_manager = current_state.register_manager

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
        data_value = 1 if test_pass else -1

        # Generate the assembly code
        tohost_memory = get_tohost_memory()
        end_label = Label(postfix="end_test_label")
        AsmLogger.asm(f"j {end_label}", comment="Jump to end label")

        AsmLogger.asm(f"{end_label}:")
        AsmLogger.asm(f"li t0, {data_value}", comment="Load the value to write to tohost")
        AsmLogger.asm(f"la t1, {tohost_memory.unique_label}", comment="Load address of tohost")
        AsmLogger.asm(f"1: sw t0, 0(t1)", comment="Store the value to tohost")
        AsmLogger.asm(f"j 1b", comment="Halt the processor")

    elif Configuration.Architecture.arm:

        logger = get_logger()
        logger.debug("============ Test end barrier")
        global end_test_barrier_label
        if end_test_barrier_label is None:
            end_test_barrier_label = Label("end_test_barrier")
        Barrier(end_test_barrier_label)

        current_el_level = current_state.current_el_level
        current_page_table = current_state.current_el_page_table
        if current_el_level != 3:
            from Arrow.Tool.asm_libraries.switch_el import switch_EL
            logger.info(f"================ Switching to EL3")
            switch_EL(target_el_level=3)


        label = Label(postfix=f"{current_state.state_name}_end_of_test")
        print_str_loop_label = Label(postfix=f"{current_state.state_name}_print_str_loop")
        print_str_end_label = Label(postfix=f"{current_state.state_name}_print_str_end")

        if current_state.state_name != "core0_thread0":
            AsmLogger.comment(f"{current_state.state_name} reached end of test, waiting for Trickbox to be closed")
            AsmLogger.asm(f"{label}:")
            AsmLogger.asm(f"wfi")
            AsmLogger.asm(f"b {label}")
        else:
            if test_pass:
                AsmLogger.comment(f"Core0 reached end of test, write 'TEST PASSED' to Trickbox")
            else:
                AsmLogger.comment(f"Core0 reached end of test, write 'TEST FAILED' to Trickbox")

            tmp_reg1 = register_manager.get_and_reserve(reg_type="gpr")
            tmp_reg2 = register_manager.get_and_reserve(reg_type="gpr")
            tmp_reg3 = register_manager.get_and_reserve(reg_type="gpr")
            sp_reg = register_manager.get(reg_name="sp")
            register_manager.reserve(sp_reg)

            # load the stack pointer
            stack_data_start_address = current_page_table.segment_manager.get_stack_data_start_address()
            AsmLogger.comment("Load the stack pointer")
            #AsmLogger.asm(f"ldr {tmp_reg1}, =_stack_top")
            AsmLogger.asm(f"ldr {tmp_reg1}, ={hex(stack_data_start_address)}")
            AsmLogger.asm(f"mov {sp_reg}, {tmp_reg1}")

            from Arrow.Tool.memory_management.memory_block import MemoryBlock
            # Convert the string to a list of byte values
            if test_pass:
                # the test_pass string has to be exactly that "TEST PASSED"
                byte_list = list(b"TEST PASSED\n")  # Include null terminator
            else:
                byte_list = list(b"TEST FAILED\n")  # Include null terminator

            # Create MemoryBlock with byte representation
            test_end_str_block = MemoryBlock(
                name="test_end_str_block", 
                byte_size=len(byte_list), 
                init_value_byte_representation=byte_list,
                alignment=4,
            )
            
            # Print a string to the trickbox tube
            AsmLogger.comment("Print a string to the trickbox tube")

            print("TODO:: Please provide Trickbox writing code to indicate test ended - dont write anything for now")

            AsmLogger.asm(f"{label}:")
            AsmLogger.asm(f"wfi", comment="End of test convention. not expecting to be waked")
            AsmLogger.asm(f"b {label}")

            register_manager.free(tmp_reg1)
            register_manager.free(tmp_reg2)
            register_manager.free(tmp_reg3)
            register_manager.free(sp_reg)
    else:
        raise ValueError(f"Unsupported architecture")
