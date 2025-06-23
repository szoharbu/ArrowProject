import os
import Arrow.Tool
from Arrow.Utils.configuration_management import get_config_manager, Configuration

_first_block=True

def generate_asm_from_AsmUnits(instruction_blocks):
    global _first_block
    asm_code = ""
    asm_code += f".global _start\n"

    for block in instruction_blocks:

        asm_code_counter = 0
        tmp_asm_code = ""

        block_name = block.name
        tmp_asm_code += f".text\n"
        tmp_asm_code += f".global {block_name}\n"
        tmp_asm_code += f"{block_name}:\n"
        if _first_block:
            asm_code_counter += 1
            tmp_asm_code += f"_start:\n"
            _first_block=False

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
            asm_code += f"// No code on {block_name} block. skipping .text section\n\n"

    return asm_code


def generate_data_from_DataUnits(data_blocks):
    data_code = ""

    for block in data_blocks:
        block_name = block.name
        block_address = hex(block.address)

        data_code_counter = 0
        tmp_data_code = ""

        # First, process initialized data (go to .data section)

        tmp_data_code += f".section .data\n"
        tmp_data_code += f".global {block_name}\n"
        tmp_data_code += f"{block_name}:\n"


        for data_unit in block.data_units_list:
            data_unit_info = data_unit.data_unit_str.strip("[]").split(", ")
            data_dict = {item.split(":")[0].strip(): item.split(":")[1].strip() for item in data_unit_info}

            name = data_dict.get('name', 'None')
            unique_label = data_dict.get('unique_label', 'None')
            memory_block = data_dict.get('memory_block', 'None')
            address = data_dict.get('address', 'None')
            byte_size = data_dict.get('byte_size', 'None')
            init_value = data_dict.get('init_value', 'None')

            if init_value != 'None':
                data_code_counter += 1
                # Initialize data with a value in the .data section
                if name == 'None':
                    tmp_data_code += f"    {unique_label}: .word {init_value}  // {byte_size} bytes initialized\n"
                else:
                    tmp_data_code += f"    {unique_label}: .word {init_value}  //  {name} - {byte_size} bytes initialized\n"

        tmp_data_code += "\n"

        #planting  .data block only if some entries exist in that section
        if data_code_counter != 0:
            data_code += tmp_data_code
            data_code_counter = 0
            tmp_data_code = ""
        else:
            data_code += f"// No initialized data on {block_name} block. skipping .data section\n\n"

        # Now, process uninitialized data (go to .bss section)
        tmp_data_code += f".section .bss\n"
        tmp_data_code += f".global {block_name}_bss\n"
        tmp_data_code += f"{block_name}_bss:\n"

        for data_unit in block.data_units_list:
            data_unit_info = data_unit.data_unit_str.strip("[]").split(", ")
            data_dict = {item.split(":")[0].strip(): item.split(":")[1].strip() for item in data_unit_info}

            name = data_dict.get('name', 'None')
            unique_label = data_dict.get('unique_label', 'None')
            memory_block = data_dict.get('memory_block', 'None')
            address = data_dict.get('address', 'None')
            byte_size = data_dict.get('byte_size', 'None')
            init_value = data_dict.get('init_value', 'None')

            if init_value == 'None':
                data_code_counter += 1
                # Reserve space for uninitialized data in the .bss section
                if name == 'None':
                    tmp_data_code += f"    {unique_label}: .skip {byte_size}  // Reserved {byte_size} bytes\n"  # 1,2,4,8 bytes
                else:
                    tmp_data_code += f"    {unique_label}: .skip {byte_size}  // {name} - Reserved {byte_size} bytes\n"  # 1,2,4,8 bytes

        tmp_data_code += "\n"

        #planting  .bss block only if some entries exist in that section
        if data_code_counter != 0:
            data_code += tmp_data_code
            data_code_counter = 0
            tmp_data_code = ""
        else:
            data_code += f"// No uninitialized data on {block_name} block. skipping .bss section\n\n"

    return data_code


def generate_arm_assembly():

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
