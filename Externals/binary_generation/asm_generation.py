import os
import random
from Utils.logger_management import get_logger
from Utils.configuration_management import get_config_manager, Configuration
from Tool.asm_blocks.asm_unit import get_comment_mark
from Tool.state_management import get_state_manager
from Utils.singleton_management import SingletonManager
from Tool.memory_management.utils import convert_bytes_to_words
from Tool.asm_libraries.barrier.barrier_manager import get_barrier_manager
from Tool.memory_management.memlayout.page_table_manager import get_page_table_manager


x86_Assembler_syntax = "NASM"  ## other option is "GAS" (GNU Assembler) syntax but not for NASM


def get_output(location, segment_name=None):
    print_logic = {
        "text_segment_header": {
            "x86_NASM": f"section .text\n",
            "x86_GAS": f".section .text.{segment_name}\n",
            "riscv": f".section .text.{segment_name}\n",
            "arm": f".section .text.{segment_name}\n",
            #"arm": f".text\n",
        },
        "data_segment_header": {
            "x86_NASM": f"section .data\nglobal {segment_name}\n{segment_name}:\n",
            "x86_GAS": f".section .data.{segment_name}\n.global {segment_name}\n{segment_name}:\n",
            "riscv": f".section .data.{segment_name}\n.global {segment_name}\n.align 2\n{segment_name}:\n",
            "arm": f".section .data.{segment_name}\n.global {segment_name}\n{segment_name}:\n",
        },
        "bss_segment_header": {
            "x86_NASM": f"section .bss\nglobal {segment_name}_bss\n{segment_name}_bss:\n",
            "x86_GAS": f".section .bss.{segment_name}\n.global {segment_name}_bss\n{segment_name}_bss:\n",
            "riscv": f".section .bss.{segment_name}\n.global {segment_name}_bss\n.align 2\n{segment_name}_bss:\n",
            "arm": f".section .bss.{segment_name}\n.global {segment_name}_bss\n{segment_name}_bss:\n",
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


def generate_asm_from_AsmUnits(instruction_segments):
    asm_code = ""
    asm_code += f".global _start\n"

    for segment in instruction_segments:

        asm_code_counter = 0
        tmp_asm_code = ""

        segment_name = segment.name
        tmp_asm_code += get_output(location="text_segment_header", segment_name=segment_name)
        tmp_asm_code += f".global {segment_name}\n"
        if Configuration.Architecture.riscv:
            tmp_asm_code += f".align 2       {get_comment_mark()} Align to 4-byte boundary\n"
        tmp_asm_code += f"{segment_name}:\n"

        # Access or initialize the singleton variable
        is_first_segment = SingletonManager.get("is_first_segment", default=True)
        if is_first_segment:
            asm_code_counter += 1
            tmp_asm_code += f"_start:\n"
            SingletonManager.set("is_first_segment", False)

        # Process each asm unit in the segment
        for asm_unit in segment.asm_units_list:
            asm_code_counter += 1
            tmp_asm_code += f"    {asm_unit}\n"

        tmp_asm_code += "\n"

        # planting  .text segment only if some entries exist in that section

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
            asm_code += f"{get_comment_mark()} No code on {segment_name} segment. skipping .text section\n\n"
        else:
            asm_code += tmp_asm_code
        asm_code_counter = 0
        tmp_asm_code = ""

    return asm_code


def generate_data_from_DataUnits(data_segments):

    data_code = ""

    for segment in data_segments:

        segment_name = segment.name
        segment_address = hex(segment.address)
        segment_pa_address = hex(segment.pa_address)
        segment_size = segment.byte_size
        data_code_counter = 0
        tmp_data_code = "\n"

        # First, process initialized data (go to .data section)
        tmp_data_code += get_output(location="data_segment_header", segment_name=segment_name)
        
        data_unit_list = segment.data_units_list

        if segment.memory_type == Configuration.Memory_types.DATA_SHARED:
            # Generate assembly code for a data section with random values and embedded labels.
            # This function creates assembly directives (.quad, .word, .byte) filled with random 
            # values while ensuring labels are placed at their specified offsets. It processes
            # the entire segment sequentially, placing each label at the exact offset required
            # and filling the spaces between labels with random data.

            assembly_code = generate_random_data_section(data_unit_list, segment_size)
            for line in assembly_code:
                tmp_data_code += f"{line}\n"

            data_code += tmp_data_code
            data_code_counter = 0
            tmp_data_code = ""
            continue

        if segment.memory_type != Configuration.Memory_types.DATA_PRESERVE and segment.memory_type != Configuration.Memory_types.STACK:
            raise ValueError(f"Unsupported Memory Type: {segment.memory_type}")

        # sort the data_unit_list by thier segment_offset, to avoid having a .org backward
        data_unit_list = sorted(data_unit_list, key=lambda x: x.segment_offset)

        first_data_unit = True
        for data_unit in data_unit_list:
            name = data_unit.name if data_unit.name is not None else 'no-name'
            # unique_label = data_dict.get('unique_label', 'None')
            unique_label = data_unit.memory_block_id
            address = data_unit.address
            pa_address = data_unit.pa_address
            segment_offset = data_unit.segment_offset
            byte_size = data_unit.byte_size
            init_value = data_unit.init_value_byte_representation
            alignment = data_unit.alignment

            # Handling barrier code, identified all the registered cores of that barrier
            # and setting its init data only to the registered cores.
            if "barrier_vector" in data_unit.name:
                init_value = handle_barrier_vector(data_unit)

            if init_value is not None:
                data_code_counter += 1

                words_tuple = convert_bytes_to_words(init_value)
                break_lines_between_same_data_unit = "\n" if len(words_tuple) > 1 else ""
                break_lines_between_different_data_units = "" if first_data_unit else "\n"
                first_data_unit = False
                
                tmp_data_code += f".org {hex(segment_offset)}\n"
                if alignment is not None:
                    tmp_data_code += f".align {alignment}\n"
                #tmp_data_code += f"{break_lines_between_different_data_units}{unique_label}:\n"
                tmp_data_code += f"{unique_label}:\n"

                if Configuration.Architecture.x86:
                    # x86 Assembly: Use `.long` for 4-byte values
                    for value, value_type in words_tuple:
                        if value_type == "word":
                            tmp_data_code += f"{break_lines_between_same_data_unit}    .long 0x{value:08x}  {get_comment_mark()} 4 bytes\n"
                        elif value_type == "byte":
                            tmp_data_code += f"{break_lines_between_same_data_unit}    .byte 0x{value:02x}  {get_comment_mark()} 1 bytes\n"
                elif Configuration.Architecture.arm:
                    # ARM Assembly: Use `.word` for 4-byte values
                    for value, value_type in words_tuple:
                        if value_type == "word":
                            tmp_data_code += f"    .word 0x{value:08x}  {get_comment_mark()} 4 bytes\n"
                            #tmp_data_code += f"{break_lines_between_same_data_unit}    .word 0x{value:08x}  {get_comment_mark()} 4 bytes\n"
                        elif value_type == "byte":
                            tmp_data_code += f"    .byte 0x{value:02x}  {get_comment_mark()} 1 byte\n"
                            #tmp_data_code += f"{break_lines_between_same_data_unit}    .byte 0x{value:02x}  {get_comment_mark()} 1 byte\n"
                    tmp_data_code += "\n"
                elif Configuration.Architecture.riscv:
                    # RISC-V Assembly: Use `.dword` for 8-byte values and `.byte` for smaller chunks
                    for value, value_type in words_tuple:
                        if value_type == "word":
                            tmp_data_code += f"{break_lines_between_same_data_unit}    .dword 0x{value:08x}  {get_comment_mark()} 4 bytes\n"  # 4 bytes (adjust if architecture supports larger)
                        elif value_type == "byte":
                            tmp_data_code += f"{break_lines_between_same_data_unit}    .byte 0x{value:02x}  {get_comment_mark()} 1 byte\n"
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

        # planting  .data segment only if some entries exist in that section
        if data_code_counter != 0:
            tmp_data_code += "\n"
            data_code += tmp_data_code
        else:
            data_code += f"{get_comment_mark()} No uninitialized data on {segment_name} data segment. skipping .data section\n\n"
            # tmp_data_code += f".space {segment_size}\n"
        data_code_counter = 0
        tmp_data_code = ""

        # # Now, process uninitialized data (go to .bss section)
        # tmp_data_code += get_output(location="bss_segment_header", segment_name=segment_name)

        # data_unit_list = segment_manager.get_segment_dataUnit_list(segment.name)
        # for data_unit in data_unit_list:
        #     name = data_unit.name if data_unit.name is not None else 'no-name'
        #     # unique_label = data_dict.get('unique_label', 'None')
        #     unique_label = data_unit.memory_block_id
        #     address = data_unit.address
        #     byte_size = data_unit.byte_size
        #     init_value = data_unit.init_value_byte_representation

        #     if init_value is None:

        #         tmp_data_code += f"{unique_label}:\n"
        #         if data_unit.alignment is not None:
        #             tmp_data_code += f".align {data_unit.alignment}\n"

        #         data_code_counter += 1
        #         # Reserve space for uninitialized data in the .bss section
        #         if Configuration.Architecture.x86:
        #             if byte_size == '8':
        #                 data_code += f"    resq 1  ; {name} - Reserved {byte_size} bytes\n"  # 8 bytes = qword
        #             elif byte_size == '4':
        #                 data_code += f"    resd 1  ; {name} - Reserved {byte_size} bytes\n"  # 4 bytes = dword
        #             elif byte_size == '2':
        #                 data_code += f"    resw 1  ; {name} - Reserved {byte_size} bytes\n"  # 2 bytes = word
        #             else:
        #                 data_code += f"    resb {byte_size}  ; {name} - Reserved {byte_size} bytes\n"  # 1 byte = byte
        #         elif Configuration.Architecture.arm:
        #             tmp_data_code += f".skip {byte_size}  // {name} - Reserved {byte_size} bytes\n"  # 1,2,4,8 bytes
        #         elif Configuration.Architecture.riscv:
        #             tmp_data_code += f".skip {byte_size}  # {name} - Reserved {byte_size} bytes\n"
        #         else:
        #             raise ValueError('Unsupported Architecture')

        # # tmp_data_code += "\n"

        # # always planting the .bss segment, even if empty # TODO:: need to refactor this logic
        # if data_code_counter != 0:
        #     tmp_data_code += "\n"
        # else:
        #     tmp_data_code += f"{get_comment_mark()} No uninitialized data on {segment_name} bss segment.\n"
        #     tmp_data_code += f".space {segment_size}\n"
        # tmp_data_code += "\n"
        # data_code += tmp_data_code
        # data_code_counter = 0
        # tmp_data_code = ""

    if Configuration.Architecture.arm:
        pass
        # # TODO:: WA WA WA WA WA WA!!!!! need to replace with proper memory allocation!!
        # # adding stack section to the data section
        # data_code += f".section .data.trickbox\n"
        # data_code += f".align 12         // 2^12 = 4096 byte alignment\n"
        # data_code += f"_trickbox_start:\n"
        # data_code += f".space 0x200000     // Reserve 2MB of memory for trickbox\n"
        # data_code += f"_trickbox_end:\n"

        # # TODO:: WA WA WA WA WA WA!!!!! need to replace with proper memory allocation!!
        # # adding stack section to the data section
        # data_code += f".section .stack\n"
        # data_code += f".align 12         // 2^12 = 4096 byte alignment\n"
        # data_code += f"_stack_start:\n"
        # data_code += f".space 0x1000     // Reserve 4KB of stack\n"
        # data_code += f"_stack_top:\n"

        # adding end of test string to the data section
        # data_code += f".data\n.balign 0x4000\n"
        # data_code += f"test_pass_str: .string \"** TEST PASSED OK **\n"
        # keep the above as is, and dont change to something like the below! regardless to the extra "
        # data_code += f"test_pass_str: .string \"** TEST PASSED OK **\"\n"

    return data_code


def generate_assembly():
    logger = get_logger()
    state_manager = get_state_manager()

    # need to fix this behavior, make sure there is only one boot, only one _start label.
    # make sure the segments are in order and not just core0 and then core1 ,...
    # and make sure all the logic and scenarios exist in the asm file

    all_code_segments = []
    all_data_segments = []

    page_table_manager = get_page_table_manager()

    for page_table in page_table_manager.get_all_page_tables():

        all_code_segments.extend(page_table.segment_manager.get_segments(
            pool_type=[Configuration.Memory_types.BSP_BOOT_CODE,
                       Configuration.Memory_types.BOOT_CODE,
                       Configuration.Memory_types.CODE]))
        
        all_data_segments.extend(page_table.segment_manager.get_segments(
            pool_type=[Configuration.Memory_types.DATA_SHARED, 
                        Configuration.Memory_types.DATA_PRESERVE, 
                        Configuration.Memory_types.STACK]))

    # Identify the BSP_BOOT_CODE in the all_code_segments list and move it to the start so it will be the first one in the asm file next to the _start label
    for i, code_segment in enumerate(all_code_segments):
        if code_segment.memory_type == Configuration.Memory_types.BSP_BOOT_CODE:
            found = all_code_segments.pop(i)
            all_code_segments.insert(0, found)
            break

    # Generate assembly code for instructions and data segments
    asm_code = generate_asm_from_AsmUnits(all_code_segments)
    data_code = generate_data_from_DataUnits(all_data_segments)


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


def handle_barrier_vector(data_unit):
    # Handling barrier code, identified all the registered cores of that barrier
    # and setting its init data only to the registered cores.
    barrier_manager = get_barrier_manager()
    barriers = barrier_manager.get_all_barriers()

    for barrier in barriers:
        barrier_memory = barrier.get_memory()
        if barrier_memory.name in data_unit.name:
            # go over all the registered cores and set the init value to the barrier vector
            core_vector = 0x0
            registered_cores = barrier.get_all_registered_cores()
            for core_id in registered_cores:
                core_vector = core_vector | (1 << core_id)

            # Create new byte array with same size as original
            # original_bytes = data_unit.init_value_byte_representation
            original_bytes = data_unit.init_value_byte_representation
            byte_array = []
            remaining_vector = core_vector
            for i in range(len(original_bytes)):
                byte_array.append(remaining_vector & 0xFF)
                remaining_vector >>= 8

            # print(f"zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz replacing {data_unit.init_value_byte_representation} with core_vector: {byte_array}")
            return byte_array


def generate_random_data_section(data_unit_list, segment_size):
    """
    Generate assembly code for a data section with random values and embedded labels.
    
    This function creates assembly directives (.quad, .word, .byte) filled with random 
    values while ensuring labels are placed at their specified offsets. It processes
    the entire segment sequentially, placing each label at the exact offset required
    and filling the spaces between labels with random data.
    
    The function tries to use the largest data directive possible (.quad for 8 bytes,
    .word for 4 bytes, .byte for 1 byte) that won't overlap with the next label,
    optimizing for both assembly file size and generation efficiency.
    
    Args:
        data_unit_list: List of data_unit objects, each containing:
            - label: String with the label name
            - segment_offset: Integer offset within the segment where label should be placed
        segment_size: Total size of the segment in bytes
        
    Returns:
        List of strings containing assembly directives with embedded labels
        
    Note:
        The data_unit_list will be sorted by segment_offset internally.
        Labels with offsets beyond segment_size will not be included (warning logged).
    """
    # Ensure the data_unit_list is sorted by segment_offset
    data_unit_list = sorted(data_unit_list, key=lambda x: x.segment_offset)
    
    # Track offset and remaining data units
    current_offset = 0
    remaining_units = data_unit_list.copy()
    
    # Assembly output
    assembly_lines = []
    
    # Process until we've covered the entire segment
    while current_offset < segment_size:
        # Check if we need to output labels at this offset
        labels_at_current_offset = []
        
        while remaining_units and remaining_units[0].segment_offset == current_offset:
            labels_at_current_offset.append(remaining_units.pop(0).name)
        
        # Output any labels at this position
        for label in labels_at_current_offset:
            assembly_lines.append(f"{label}:")
        
        # Determine what size chunk to output next
        if current_offset + 8 <= segment_size:
            # No label in the way, can output a quad
            next_label_offset = remaining_units[0].segment_offset if remaining_units else segment_size
            if current_offset + 8 <= next_label_offset:
                # Generate random 8-byte value
                random_value = random.randint(0, 0xFFFFFFFFFFFFFFFF)
                assembly_lines.append(f"    .quad 0x{random_value:016x}")
                current_offset += 8
                continue
        
        if current_offset + 4 <= segment_size:
            # Try a word
            next_label_offset = remaining_units[0].segment_offset if remaining_units else segment_size
            if current_offset + 4 <= next_label_offset:
                # Generate random 4-byte value
                random_value = random.randint(0, 0xFFFFFFFF)
                assembly_lines.append(f"    .word 0x{random_value:08x}")
                current_offset += 4
                continue
        
        # Just output a byte
        random_value = random.randint(0, 0xFF)
        assembly_lines.append(f"    .byte 0x{random_value:02x}")
        current_offset += 1
    
    # Verify all labels were processed
    if remaining_units:
        print(f"WARNING: {len(remaining_units)} labels were not placed because their offsets exceed segment size")
    
    return assembly_lines