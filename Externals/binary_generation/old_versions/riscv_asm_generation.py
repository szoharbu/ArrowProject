import os
import Tool
from Utils.configuration_management import get_config_manager, Configuration

def generate_asm_from_AsmUnits(instruction_blocks):

    asm_code = ""

    for block in instruction_blocks:
        block_name = block.name
        block_address = hex(block.address)
        asm_code += f".section .text.{block_name}\n"
        asm_code += f".global {block_name}\n"
        asm_code += f"{block_name}:\n"

        # Process each asm unit in the block
        for asm_unit in block.asm_units_list:
            if asm_unit.type == 'asm_string':
                asm_code += f"    {asm_unit}  # {asm_unit.comment if hasattr(asm_unit, 'comment') else ''}\n"
            elif asm_unit.type == 'comment':
                asm_code += f"    {asm_unit}\n"
            elif asm_unit.type == 'generation':
                asm_code += f"    {asm_unit}\n"
            else:
                raise ValueError(f"Unsupported asm_unit type {asm_unit.type}")
            # Add other types of units if needed (e.g., labels, branches, etc.)

        asm_code += "\n"

    return asm_code


def generate_data_from_DataUnits(data_blocks):
    data_code = ""

    for block in data_blocks:
        block_name = block.name
        block_address = hex(block.address)

        # First, process initialized data (go to .data section)
        data_code += f".section .data.{block_name}\n"
        data_code += f".global {block_name}\n"
        data_code += f"{block_name}:\n"

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
                data_code += f"    .quad {address}, {init_value}  # {name} - {byte_size} bytes initialized\n"

        # Now, process uninitialized data (go to .bss section)
        data_code += f".section .bss.{block_name}\n"
        data_code += f".global {block_name}_bss\n"
        data_code += f"{block_name}_bss:\n"

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
                data_code += f"    .skip {byte_size}  # {name} - Reserved {byte_size} bytes\n"

        data_code += "\n"

    return data_code


def generate_riscv_assembly():

    current_state = Tool.state_manager.get_active_state()
    all_code_blocks = current_state.segment_manager.get_segments(pool_type=[Configuration.Memory_types.BOOT_CODE, Configuration.Memory_types.CODE])
    all_data_blocks = current_state.segment_manager.get_segments(pool_type=[Configuration.Memory_types.DATA_SHARED, Configuration.Memory_types.DATA_PRESERVE])

    # Generate assembly code for instructions and data blocks
    asm_code = generate_asm_from_AsmUnits(all_code_blocks)
    data_code = generate_data_from_DataUnits(all_data_blocks)

    # Combine the instruction and data parts
    full_asm_code = asm_code + "\n" + data_code

    config_manager = get_config_manager()
    output_dir = config_manager.get_value('output_dir_path')
    asm_file = os.path.join(output_dir,"generated_asm_riscv.s")

    # Output the result to a .s file
    with open(asm_file, "w") as f:
        f.write(full_asm_code)

    Tool.logger.info(f"---- Assembly code generated successfully. Check {asm_file}")



