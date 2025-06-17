from Arrow.Utils.configuration_management import Configuration
from Arrow.Tool.memory_management.memory_operand import Memory
from Arrow.Tool.state_management import get_current_state
from Arrow.Tool.asm_libraries.asm_logger import AsmLogger
from Arrow.Tool.asm_libraries.label import Label
from Arrow.Tool.asm_libraries.barrier.barrier import Barrier

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
    current_page_table = current_state.current_el_page_table
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
        zero_bit = 0 if test_pass else 1
        data_value = (status_code << 1) | zero_bit  # Data[31:1] = status_code, Data[0] = 1 or 0

        # Generate the assembly code
        tohost_memory = Memory(name='tohost')
        end_label = Label(postfix="end_test_label")
        AsmLogger.asm(f"li t0, {data_value}", comment="Load the value to write to tohost")
        AsmLogger.asm(f"la t1, {tohost_memory.unique_label}", comment="Load address of tohost")
        AsmLogger.asm(f"sw t0, 0(t1)", comment="Store the value to tohost")
        AsmLogger.asm(f"j {end_label}", comment="Jump to end label")

        AsmLogger.asm(f"{end_label}:")
        AsmLogger.asm(f"ebreak", comment="Halt the processor")

    elif Configuration.Architecture.arm:

        #TODO:: add barrier here, to ensure all cores are at the same point, and then only one core will write test pass
        #Barrier("test_final")

        label = Label(postfix=f"{current_state.state_name}_end_of_test")
        print_str_loop_label = Label(postfix=f"{current_state.state_name}_print_str_loop")
        print_str_end_label = Label(postfix=f"{current_state.state_name}_print_str_end")

        if current_state.state_name != "core_0":
            AsmLogger.comment(f"{current_state.state_name} reached end of test, waiting for Trickbox to be closed")
            AsmLogger.asm(f"{label}:")
            AsmLogger.asm(f"wfi")
            AsmLogger.asm(f"b {label}")
        else:
            if test_pass:
                AsmLogger.comment(f"Core0 reached end of test, write '** TEST PASSED OK **' to Trickbox")
            else:
                AsmLogger.comment(f"Core0 reached end of test, write '** TEST FAILED **' to Trickbox")

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
                # the test_pass string has to be exactly that "** TEST PASSED OK **\n" including the '\n' null terminator!!! 
                byte_list = list(b"** TEST PASSED OK **\n")  # Include null terminator
            else:
                byte_list = list(b"** TEST FAILED **\n")  # Include null terminator

            # Create MemoryBlock with byte representation
            test_end_str_block = MemoryBlock(
                name="test_end_str_block", 
                byte_size=len(byte_list), 
                init_value_byte_representation=byte_list,
                alignment=4,
            )
            
            # Print a string to the trickbox tube
            AsmLogger.comment("Print a string to the trickbox tube")
            AsmLogger.asm(f"ldr {tmp_reg1}, ={test_end_str_block.get_address()}", comment="Load the address of the test_end string")
            AsmLogger.asm(f"stp {tmp_reg2}, {tmp_reg3}, [{sp_reg}, #-16]!", comment=f"Push {tmp_reg2}, {tmp_reg3} to stack to get some temps")
            AsmLogger.asm(f"ldr {tmp_reg2}, =0x0", comment="Load the address of the trickbox tube")
            AsmLogger.asm(f"{print_str_loop_label}:", comment="Start of the loop")
            AsmLogger.asm(f"ldrb {tmp_reg3.as_size(32)}, [{tmp_reg1}], #1", comment="Load the next character from the string")
            AsmLogger.asm(f"cbz {tmp_reg3.as_size(32)}, {print_str_end_label}", comment="If the character is the null terminator, end the loop")
            AsmLogger.asm(f"strb {tmp_reg3.as_size(32)}, [{tmp_reg2}]", comment="Store the character to the Tbox tube")
            AsmLogger.asm(f"b {print_str_loop_label}", comment="Jump back to the start of the loop")
            AsmLogger.asm(f"{print_str_end_label}:", comment="End of the loop")
            AsmLogger.asm(f"ldp {tmp_reg2}, {tmp_reg3}, [sp], #16", comment=f"Pop {tmp_reg2}, {tmp_reg3} from stack")

            # Close the trickbox tube (end the test)
            AsmLogger.comment("Close the trickbox tube (end the test)")
            AsmLogger.asm(f"ldr {tmp_reg1}, =0x0", comment="Load the address of the trickbox tube")
            AsmLogger.asm(f"mov {tmp_reg2}, #0x4", comment="Load the EOT character")
            AsmLogger.asm(f"strb {tmp_reg2.as_size(32)}, [{tmp_reg1}]", comment="Store the EOT character to the trickbox tube")
            AsmLogger.asm(f"dsb sy", comment="Flush the data cache")

            AsmLogger.asm(f"{label}:")
            AsmLogger.asm(f"wfi", comment="End of test convention. not expecting to be waked")
            AsmLogger.asm(f"b {label}")

            register_manager.free(tmp_reg1)
            register_manager.free(tmp_reg2)
            register_manager.free(tmp_reg3)
            register_manager.free(sp_reg)
    else:
        raise ValueError(f"Unsupported architecture")