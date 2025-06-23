import os
import Arrow.Tool
from Arrow.Utils.configuration_management import get_config_manager, Configuration

#Assembler_syntax = "GAS" # (GNU Assembler) syntax but not for NASM
Assembler_syntax = "NASM"
def generate_asm_from_AsmUnits(instruction_blocks):
    asm_code = ""

    for block in instruction_blocks:
        block_name = block.name
        block_address = hex(block.address)
        if Assembler_syntax == "NASM":
            asm_code += f"section .text\n"
            asm_code += f"global {block_name}\n"
            asm_code += f"{block_name}:\n"
        elif Assembler_syntax == "GAS":
            asm_code += f".section .text.{block_name}\n"
            asm_code += f".global {block_name}\n"
            asm_code += f"{block_name}:\n"
        else:
            raise ValueError(f"Invalid Assembler syntax used {Assembler_syntax}")

        # Process each asm unit in the block
        for asm_unit in block.asm_units_list:
            asm_code += f"    {asm_unit}\n"

        asm_code += "\n"

    return asm_code


def generate_data_from_DataUnits(data_blocks):
    data_code = ""

    for block in data_blocks:
        block_name = block.name
        block_address = hex(block.address)

        # First, process initialized data (go to .data section)

        if Assembler_syntax == "NASM":
            data_code += f"section .data\n"
            data_code += f"global {block_name}\n"
            data_code += f"{block_name}:\n"
        elif Assembler_syntax == "GAS":
            data_code += f".section .data.{block_name}\n"
            data_code += f".global {block_name}\n"
            data_code += f"{block_name}:\n"
        else:
            raise ValueError(f"Invalid Assembler syntax used {Assembler_syntax}")

        for data_unit in block.data_units_list:
            data_unit_info = data_unit.data_unit_str.strip("[]").split(", ")
            data_dict = {item.split(":")[0].strip(): item.split(":")[1].strip() for item in data_unit_info}

            name = data_dict.get('name', 'None')
            memory_block = data_dict.get('memory_block', 'None')
            address = data_dict.get('address', 'None')
            byte_size = data_dict.get('byte_size', 'None')
            init_value = data_dict.get('init_value', 'None')

            if init_value != 'None':
                # Initialize data with a value in the .data section
                data_code += f"    dd {init_value}  ; {name} - {byte_size} bytes initialized\n"

        # Now, process uninitialized data (go to .bss section)
        if Assembler_syntax == "NASM":
            data_code += f"section .bss\n"
            data_code += f"global {block_name}_bss\n"
            data_code += f"{block_name}_bss:\n"
        elif Assembler_syntax == "GAS":
            data_code += f".section .bss.{block_name}\n"
            data_code += f".global {block_name}_bss\n"
            data_code += f"{block_name}_bss:\n"
        else:
            raise ValueError(f"Invalid Assembler syntax used {Assembler_syntax}")

        for data_unit in block.data_units_list:
            data_unit_info = data_unit.data_unit_str.strip("[]").split(", ")
            data_dict = {item.split(":")[0].strip(): item.split(":")[1].strip() for item in data_unit_info}

            name = data_dict.get('name', 'None')
            memory_block = data_dict.get('memory_block', 'None')
            address = data_dict.get('address', 'None')
            byte_size = data_dict.get('byte_size', 'None')
            init_value = data_dict.get('init_value', 'None')

            if init_value == 'None':
                # Reserve space for uninitialized data in the .bss section
                if byte_size == '8':
                    data_code += f"    resq 1  ; {name} - Reserved {byte_size} bytes\n"  # 8 bytes = qword
                elif byte_size == '4':
                    data_code += f"    resd 1  ; {name} - Reserved {byte_size} bytes\n"  # 4 bytes = dword
                elif byte_size == '2':
                    data_code += f"    resw 1  ; {name} - Reserved {byte_size} bytes\n"  # 2 bytes = word
                else:
                    data_code += f"    resb {byte_size}  ; {name} - Reserved {byte_size} bytes\n"  # 1 byte = byte

        data_code += "\n"

    return data_code


def generate_x86_assembly():

    current_state = Arrow.Tool.state_manager.get_active_state()
    all_code_blocks = current_state.segment_manager.get_segments(pool_type=[Configuration.Memory_types.BOOT_CODE, Configuration.Memory_types.CODE])
    all_data_blocks = current_state.segment_manager.get_segments(pool_type=[Configuration.Memory_types.DATA_SHARED, Configuration.Memory_types.DATA_PRESERVE])

    # Generate assembly code for instructions and data blocks
    asm_code = generate_asm_from_AsmUnits(all_code_blocks)
    data_code = generate_data_from_DataUnits(all_data_blocks)

    # Combine the instruction and data parts
    full_asm_code = asm_code + "\n" + data_code

    config_manager = get_config_manager()
    output_dir = config_manager.get_value('output_dir_path')
    asm_file = os.path.join(output_dir,"test.asm")
    config_manager.set_value('asm_file',asm_file)

    # Output the result to a .s file
    with open(asm_file, "w") as f:
        f.write(full_asm_code)

    Arrow.Tool.logger.info(f"---- Assembly code generated successfully. Check {asm_file}")
