import os
from Arrow.Utils.logger_management import get_logger
from Arrow.Utils.configuration_management import get_config_manager, Configuration
from Arrow.Tool.asm_blocks.asm_unit import get_comment_mark
from Arrow.Tool.state_management import get_state_manager
from Arrow.Utils.singleton_management import SingletonManager
from Arrow.Tool.memory_management.utils import convert_bytes_to_words

x86_Assembler_syntax = "NASM" ## other option is "GAS" (GNU Assembler) syntax but not for NASM

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
            "riscv": f".section .data.{block_name}\n.global {block_name}\n.align 3\n{block_name}:\n",
            "arm": f".section .data\n.global {block_name}\n{block_name}:\n",
        },
        "bss_block_header": {
            "x86_NASM": f"section .bss\nglobal {block_name}_bss\n{block_name}_bss:\n",
            "x86_GAS": f".section .bss.{block_name}\n.global {block_name}_bss\n{block_name}_bss:\n",
            "riscv":  f".section .bss.{block_name}\n.global {block_name}_bss\n.align 3\n{block_name}_bss:\n",
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
            tmp_asm_code += f".align 3       {get_comment_mark()} Align to 8-byte boundary\n"
        tmp_asm_code += f"{block_name}:\n"

        # Access or initialize the singleton variable
        is_first_block = SingletonManager.get("is_first_block", default=True)
        if is_first_block:
            asm_code_counter += 1
            tmp_asm_code += f"_start:\n"
            SingletonManager.set("is_first_block", False)

        # Process each asm unit in the block
        for asm_unit in block.asm_units_list:
            asm_code_counter +=1
            tmp_asm_code += f"    {asm_unit}\n"

        tmp_asm_code += "\n"

        #planting  .text block only if some entries exist in that section
        if asm_code_counter != 0:
            asm_code += tmp_asm_code
            asm_code_counter = 0
            tmp_asm_code = ""
        else:
            asm_code += f"{get_comment_mark()} No code on {block_name} block. skipping .text section\n\n"

    return asm_code


def generate_data_from_DataUnits(data_blocks):
    state_manager = get_state_manager()
    current_state = state_manager.get_active_state()
    memory_manager = current_state.memory_manager


    data_code = ""

    for block in data_blocks:
        block_name = block.name
        block_address = hex(block.address)

        data_code_counter = 0
        tmp_data_code = ""

        # First, process initialized data (go to .data section)
        tmp_data_code += get_output(location="data_block_header", block_name=block_name)

        data_unit_list = memory_manager.get_segment_dataUnit_list(block.name)
        first_data_unit = True
        for data_unit in data_unit_list:
            name = data_unit.name if data_unit.name is not None else 'no-name'
            #unique_label = data_dict.get('unique_label', 'None')
            unique_label = data_unit.memory_block_id  #data data_dict.get('memory_block', 'None')
            address = data_unit.address # data_dict.get('address', 'None')
            byte_size = data_unit.byte_size #data_dict.get('byte_size', 'None')
            init_value = data_unit.init_value_byte_representation # data_dict.get('init_value', 'None')

            if init_value is not None:
                data_code_counter += 1

                words_tuple = convert_bytes_to_words(init_value)
                break_lines_between_same_data_unit = "\n" if len(words_tuple)>1 else ""
                break_lines_between_different_data_units = "" if first_data_unit else "\n"
                first_data_unit = False
                tmp_data_code += f"{break_lines_between_different_data_units}{unique_label}:"
                if Configuration.Architecture.x86:
                    # x86 Assembly: Use `.long` for 4-byte values
                    for value, value_type in words_tuple:
                        if value_type == "word":
                            tmp_data_code += f"{break_lines_between_same_data_unit}    .long 0x{value:08x}  {get_comment_mark()} 4 bytes"
                        elif value_type == "byte":
                            tmp_data_code+= f"{break_lines_between_same_data_unit}    .byte 0x{value:02x}  {get_comment_mark()} 1 bytes"
                elif Configuration.Architecture.arm:
                    # ARM Assembly: Use `.word` for 4-byte values
                    for value, value_type in words_tuple:
                        if value_type == "word":
                            tmp_data_code+= f"{break_lines_between_same_data_unit}    .word 0x{value:08x}  {get_comment_mark()} 4 bytes"
                        elif value_type == "byte":
                            tmp_data_code+= f"{break_lines_between_same_data_unit}    .byte 0x{value:02x}  {get_comment_mark()} 1 byte"
                elif Configuration.Architecture.riscv:
                    # RISC-V Assembly: Use `.dword` for 8-byte values and `.byte` for smaller chunks
                    for value, value_type in words_tuple:
                        if value_type == "word":
                            tmp_data_code+= f"{break_lines_between_same_data_unit}    .dword 0x{value:08x}  {get_comment_mark()} 4 bytes"  # 4 bytes (adjust if architecture supports larger)
                        elif value_type == "byte":
                            tmp_data_code+= f"{break_lines_between_same_data_unit}    .byte 0x{value:02x}  {get_comment_mark()} 1 byte"
                else:
                    raise ValueError('Unsupported Architecture')

                # # Initialize data with a value in the .data section
                # if Configuration.Architecture.x86:
                #     pass
                # elif Configuration.Architecture.arm:
                #     tmp_data_code += f"    {unique_label}: .word {init_value}  //  {name} - {byte_size} bytes initialized\n"
                # elif Configuration.Architecture.riscv:
                #     tmp_data_code += f"    {unique_label}: .quad {address}, {init_value}  # {name} - {byte_size} bytes initialized\n"

        tmp_data_code += "\n"

        #planting  .data block only if some entries exist in that section
        if data_code_counter != 0:
            data_code += tmp_data_code
            data_code_counter = 0
            tmp_data_code = ""
        else:
            data_code += f"{get_comment_mark()} No initialized data on {block_name} block. skipping .data section\n\n"

        # Now, process uninitialized data (go to .bss section)
        tmp_data_code += get_output(location="bss_block_header", block_name=block_name)

        data_unit_list = memory_manager.get_segment_dataUnit_list(block.name)
        for data_unit in data_unit_list:
            name = data_unit.name if data_unit.name is not None else 'no-name'
            #unique_label = data_dict.get('unique_label', 'None')
            unique_label = data_unit.memory_block_id  #data data_dict.get('memory_block', 'None')
            address = data_unit.address # data_dict.get('address', 'None')
            byte_size = data_unit.byte_size #data_dict.get('byte_size', 'None')
            init_value = data_unit.init_value_byte_representation # data_dict.get('init_value', 'None')

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

        tmp_data_code += "\n"

        #planting  .bss block only if some entries exist in that section
        if data_code_counter != 0:
            data_code += tmp_data_code
            data_code_counter = 0
            tmp_data_code = ""
        else:
            data_code += f"{get_comment_mark()} No uninitialized data on {block_name} block. skipping .bss section\n\n"

    return data_code


def generate_assembly():
    logger = get_logger()
    state_manager = get_state_manager()
    current_state = state_manager.get_active_state()
    all_code_blocks = current_state.memory_manager.get_segments(pool_type=[Configuration.Memory_types.BOOT_CODE, Configuration.Memory_types.CODE])
    all_data_blocks = current_state.memory_manager.get_segments(pool_type=[Configuration.Memory_types.DATA_SHARED, Configuration.Memory_types.DATA_PRESERVE])

    # Generate assembly code for instructions and data blocks
    asm_code = generate_asm_from_AsmUnits(all_code_blocks)
    data_code = generate_data_from_DataUnits(all_data_blocks)

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
