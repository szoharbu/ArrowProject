import os
from Utils.logger_management import get_logger
from Utils.configuration_management import get_config_manager, Configuration
from Tool.asm_blocks.asm_unit import get_comment_mark
from Tool.state_management import get_state_manager
from Utils.singleton_management import SingletonManager
from Tool.memory_management.utils import convert_bytes_to_words
from Tool.asm_libraries.barrier.barrier_manager import get_barrier_manager

x86_Assembler_syntax = "NASM"  ## other option is "GAS" (GNU Assembler) syntax but not for NASM


def get_output(location, block_name=None):
    print_logic = {
        "text_block_header": {
            "x86_NASM": f"section .text\n",
            "x86_GAS": f".section .text.{block_name}\n",
            "riscv": f".section .text.{block_name}\n",
            "arm": f".text\n",
        },
        "data_block_header": {
            "x86_NASM": f"section .data\nglobal {block_name}\n{block_name}:\n",
            "x86_GAS": f".section .data.{block_name}\n.global {block_name}\n{block_name}:\n",
            "riscv": f".section .data.{block_name}\n.global {block_name}\n.align 2\n{block_name}:\n",
            "arm": f".section .data\n.global {block_name}\n{block_name}:\n",
        },
        "bss_block_header": {
            "x86_NASM": f"section .bss\nglobal {block_name}_bss\n{block_name}_bss:\n",
            "x86_GAS": f".section .bss.{block_name}\n.global {block_name}_bss\n{block_name}_bss:\n",
            "riscv": f".section .bss.{block_name}\n.global {block_name}_bss\n.align 2\n{block_name}_bss:\n",
            "arm": f".section .bss\n.global {block_name}_bss\n{block_name}_bss:\n",
        },
    }

    arch_syntax = Configuration.Architecture.arch_str
    if arch_syntax == "x86":
        if x86_Assembler_syntax == "NASM":
            arch_syntax = "x86_NASM"
        elif x86_Assembler_syntax == "GAS":
            arch_syntax = "x86_GAS"
        else:
            raise ValueError(f"Invalid Assembler syntax used {x86_Assembler_syntax}")

    # Fetch and return the output for the given section and condition
    return print_logic.get(location, {}).get(arch_syntax, "Default output")


def generate_asm_from_AsmUnits(instruction_blocks):
    asm_code = ""
    asm_code += f".global _start\n"

    for block in instruction_blocks:

        asm_code_counter = 0
        tmp_asm_code = ""

        block_name = block.name
        tmp_asm_code += get_output(location="text_block_header", block_name=block_name)
        tmp_asm_code += f".global {block_name}\n"
        if Configuration.Architecture.riscv:
            tmp_asm_code += f".align 2       {get_comment_mark()} Align to 4-byte boundary\n"
        tmp_asm_code += f"{block_name}:\n"

        # Access or initialize the singleton variable
        is_first_block = SingletonManager.get("is_first_block", default=True)
        if is_first_block:
            asm_code_counter += 1
            tmp_asm_code += f"_start:\n"
            SingletonManager.set("is_first_block", False)

        # Process each asm unit in the block
        for asm_unit in block.asm_units_list:
            asm_code_counter += 1
            tmp_asm_code += f"    {asm_unit}\n"

        tmp_asm_code += "\n"

        # planting  .text block only if some entries exist in that section

        skip_text_section = False
        if asm_code_counter == 0:
            skip_text_section = True
        elif asm_code_counter == 1:
            lines = tmp_asm_code.split("\n")
            lines = [line for line in lines if line.strip()]
            if len(lines) == 4:
                # Some text sections contain only labels like the below - skipping them
                '''
                .global core_1__code_segment_5_1316
                core_1__code_segment_5_1316:
                label_4858_core_1__code_segment_5_code_segment: 
                '''
                skip_text_section = True

        if skip_text_section:
            asm_code += f"{get_comment_mark()} No code on {block_name} block. skipping .text section\n\n"
        else:
            asm_code += tmp_asm_code
        asm_code_counter = 0
        tmp_asm_code = ""

    return asm_code


def generate_data_from_DataUnits(data_blocks):
    state_manager = get_state_manager()

    data_code = ""

    for block, state in data_blocks:

        state_manager.set_active_state(state)
        curr_state = state_manager.get_active_state()
        memory_manager = curr_state.memory_manager

        block_name = block.name
        block_address = hex(block.address)
        block_size = block.byte_size
        data_code_counter = 0
        tmp_data_code = ""

        # First, process initialized data (go to .data section)
        tmp_data_code += get_output(location="data_block_header", block_name=block_name)

        data_unit_list = memory_manager.get_segment_dataUnit_list(block.name)
        first_data_unit = True
        for data_unit in data_unit_list:
            name = data_unit.name if data_unit.name is not None else 'no-name'
            # unique_label = data_dict.get('unique_label', 'None')
            unique_label = data_unit.memory_block_id  # data data_dict.get('memory_block', 'None')
            address = data_unit.address  # data_dict.get('address', 'None')
            byte_size = data_unit.byte_size  # data_dict.get('byte_size', 'None')
            init_value = data_unit.init_value_byte_representation  # data_dict.get('init_value', 'None')

            # Handling barrier code, identified all the registered cores of that barrier
            # and setting its init data only to the registered cores.
            if "barrier_vector" in data_unit.name:
                barrier_manager = get_barrier_manager()
                barriers = barrier_manager.get_all_barriers()
                for barrier in barriers:
                    if barrier.memory.name in data_unit.name:
                        # go over all the registered cores and set the init value to the barrier vector
                        core_vector = 0x0
                        registered_cores = barrier.get_all_registered_cores()
                        for core_id in registered_cores:
                            core_vector = core_vector | (1 << core_id)

                        # Create new byte array with same size as original
                        original_bytes = data_unit.init_value_byte_representation
                        byte_array = []
                        remaining_vector = core_vector
                        for i in range(len(original_bytes)):
                            byte_array.append(remaining_vector & 0xFF)
                            remaining_vector >>= 8

                        print(
                            f"zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz replacing {data_unit.init_value_byte_representation} with core_vector: {byte_array}")
                        init_value = byte_array

            if init_value is not None:
                data_code_counter += 1

                words_tuple = convert_bytes_to_words(init_value)
                break_lines_between_same_data_unit = "\n" if len(words_tuple) > 1 else ""
                break_lines_between_different_data_units = "" if first_data_unit else "\n"
                first_data_unit = False
                tmp_data_code += f"{break_lines_between_different_data_units}{unique_label}:"
                if Configuration.Architecture.x86:
                    # x86 Assembly: Use `.long` for 4-byte values
                    for value, value_type in words_tuple:
                        if value_type == "word":
                            tmp_data_code += f"{break_lines_between_same_data_unit}    .long 0x{value:08x}  {get_comment_mark()} 4 bytes"
                        elif value_type == "byte":
                            tmp_data_code += f"{break_lines_between_same_data_unit}    .byte 0x{value:02x}  {get_comment_mark()} 1 bytes"
                elif Configuration.Architecture.arm:
                    # ARM Assembly: Use `.word` for 4-byte values
                    for value, value_type in words_tuple:
                        if value_type == "word":
                            tmp_data_code += f"{break_lines_between_same_data_unit}    .word 0x{value:08x}  {get_comment_mark()} 4 bytes"
                        elif value_type == "byte":
                            tmp_data_code += f"{break_lines_between_same_data_unit}    .byte 0x{value:02x}  {get_comment_mark()} 1 byte"
                elif Configuration.Architecture.riscv:
                    # RISC-V Assembly: Use `.dword` for 8-byte values and `.byte` for smaller chunks
                    for value, value_type in words_tuple:
                        if value_type == "word":
                            tmp_data_code += f"{break_lines_between_same_data_unit}    .dword 0x{value:08x}  {get_comment_mark()} 4 bytes"  # 4 bytes (adjust if architecture supports larger)
                        elif value_type == "byte":
                            tmp_data_code += f"{break_lines_between_same_data_unit}    .byte 0x{value:02x}  {get_comment_mark()} 1 byte"
                else:
                    raise ValueError('Unsupported Architecture')

                # # Initialize data with a value in the .data section
                # if Configuration.Architecture.x86:
                #     pass
                # elif Configuration.Architecture.arm:
                #     tmp_data_code += f"    {unique_label}: .word {init_value}  //  {name} - {byte_size} bytes initialized\n"
                # elif Configuration.Architecture.riscv:
                #     tmp_data_code += f"    {unique_label}: .quad {address}, {init_value}  # {name} - {byte_size} bytes initialized\n"

        # tmp_data_code += "\n"

        # planting  .data block only if some entries exist in that section
        if data_code_counter != 0:
            tmp_data_code += "\n"
            data_code += tmp_data_code
        else:
            data_code += f"{get_comment_mark()} No uninitialized data on {block_name} data block. skipping .data section\n\n"
            # tmp_data_code += f".space {block_size}\n"
        data_code_counter = 0
        tmp_data_code = ""

        # Now, process uninitialized data (go to .bss section)
        tmp_data_code += get_output(location="bss_block_header", block_name=block_name)

        data_unit_list = memory_manager.get_segment_dataUnit_list(block.name)
        for data_unit in data_unit_list:
            name = data_unit.name if data_unit.name is not None else 'no-name'
            # unique_label = data_dict.get('unique_label', 'None')
            unique_label = data_unit.memory_block_id  # data data_dict.get('memory_block', 'None')
            address = data_unit.address  # data_dict.get('address', 'None')
            byte_size = data_unit.byte_size  # data_dict.get('byte_size', 'None')
            init_value = data_unit.init_value_byte_representation  # data_dict.get('init_value', 'None')

            if init_value is None:
                data_code_counter += 1
                # Reserve space for uninitialized data in the .bss section
                if Configuration.Architecture.x86:
                    if byte_size == '8':
                        data_code += f"    resq 1  ; {name} - Reserved {byte_size} bytes\n"  # 8 bytes = qword
                    elif byte_size == '4':
                        data_code += f"    resd 1  ; {name} - Reserved {byte_size} bytes\n"  # 4 bytes = dword
                    elif byte_size == '2':
                        data_code += f"    resw 1  ; {name} - Reserved {byte_size} bytes\n"  # 2 bytes = word
                    else:
                        data_code += f"    resb {byte_size}  ; {name} - Reserved {byte_size} bytes\n"  # 1 byte = byte
                elif Configuration.Architecture.arm:
                    tmp_data_code += f"    {unique_label}: .skip {byte_size}  // {name} - Reserved {byte_size} bytes\n"  # 1,2,4,8 bytes
                elif Configuration.Architecture.riscv:
                    tmp_data_code += f"    {unique_label}: .skip {byte_size}  # {name} - Reserved {byte_size} bytes\n"
                else:
                    raise ValueError('Unsupported Architecture')

        # tmp_data_code += "\n"

        # always planting the .bss block, even if empty # TODO:: need to refactor this logic
        if data_code_counter != 0:
            tmp_data_code += "\n"
        else:
            tmp_data_code += f"{get_comment_mark()} No uninitialized data on {block_name} bss block.\n"
            tmp_data_code += f".space {block_size}\n"
        tmp_data_code += "\n"
        data_code += tmp_data_code
        data_code_counter = 0
        tmp_data_code = ""

    if Configuration.Architecture.arm:
        # TODO:: WA WA WA WA WA WA!!!!! need to replace with proper memory allocation!!
        # adding stack section to the data section
        data_code += f".section .stack\n"
        data_code += f".align 12         // 2^12 = 4096 byte alignment\n"
        data_code += f"_stack_start:\n"
        data_code += f".space 0x1000     // Reserve 4KB of stack\n"
        data_code += f"_stack_top:\n"

        # adding end of test string to the data section
        data_code += f".data\n.balign 0x4000\n"
        data_code += f"test_pass_str: .string \"** TEST PASSED OK **\n"
        # keep the above as is, and dont change to something like the below! regardless to the extra "
        # data_code += f"test_pass_str: .string \"** TEST PASSED OK **\"\n"

    return data_code


def generate_assembly():
    logger = get_logger()
    state_manager = get_state_manager()

    # need to fix this behavior, make sure there is only one boot, only one _start label.
    # make sure the segments are in order and not just core0 and then core1 ,...
    # and make sure all the logic and scenarios exist in the asm file

    all_code_blocks = []
    all_data_blocks = []

    orig_state = state_manager.get_active_state()
    cores_states = state_manager.list_states()
    for core_state in cores_states:
        state_manager.set_active_state(core_state)
        curr_state = state_manager.get_active_state()

        all_code_blocks.extend(curr_state.memory_manager.get_segments(
            pool_type=[Configuration.Memory_types.BSP_BOOT_CODE,
                       Configuration.Memory_types.BOOT_CODE,
                       Configuration.Memory_types.CODE]))

        # Need to pass the data blocks along with their state, as its needed for the data generation
        current_state_data_blocks = curr_state.memory_manager.get_segments(
            pool_type=[Configuration.Memory_types.DATA_SHARED, Configuration.Memory_types.DATA_PRESERVE])
        current_state_data_blocks_with_state = [(datablock, core_state) for datablock in current_state_data_blocks]
        all_data_blocks.extend(current_state_data_blocks_with_state)

    # Identify the BSP_BOOT_CODE in the all_code_blocks list and move it to the start so it will be the first one in the asm file next to the _start label
    for i, code_block in enumerate(all_code_blocks):
        if code_block.memory_type == Configuration.Memory_types.BSP_BOOT_CODE:
            found = all_code_blocks.pop(i)
            all_code_blocks.insert(0, found)
            break

    # Generate assembly code for instructions and data blocks
    asm_code = generate_asm_from_AsmUnits(all_code_blocks)
    data_code = generate_data_from_DataUnits(all_data_blocks)

    curr_state = state_manager.get_active_state()
    state_manager.set_active_state(state_id=orig_state.state_name)

    # Combine the instruction and data parts
    full_asm_code = asm_code + "\n" + data_code

    config_manager = get_config_manager()
    output_dir = config_manager.get_value('output_dir_path')
    if Configuration.Architecture.x86:
        asm_file = os.path.join(output_dir, "test.asm")
    elif Configuration.Architecture.arm:
        asm_file = os.path.join(output_dir, "test.asm")
    elif Configuration.Architecture.riscv:
        asm_file = os.path.join(output_dir, "test.s")
    else:
        raise ValueError('Unsupported Architecture')

    config_manager.set_value('asm_file', asm_file)

    # Output the result to a .s file
    with open(asm_file, "w") as f:
        f.write(full_asm_code)

    logger.info(f"---- Assembly code generated successfully. Check {asm_file}")
