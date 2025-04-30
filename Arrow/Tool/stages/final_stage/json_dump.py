import json
import os
from Utils.configuration_management import Configuration, get_config_manager
from Utils.logger_management import get_logger
from Tool.state_management import get_state_manager

def generation_json_dump():
    logger = get_logger()
    logger.info("---- generation.json dump")

    state_manager = get_state_manager()
    current_state = state_manager.get_active_state()
    available_blocks = current_state.memory_manager.get_segments(pool_type=[Configuration.Memory_types.BOOT_CODE, Configuration.Memory_types.CODE])

    # Prepare data for JSON
    data = []  # List to store all blocks and their asm_units_list

    for block in available_blocks:
        block_data = {
            "block_name": block.name,
            "block_address": hex(block.address),
            "asm_units": []
        }
        for asm_unit in block.asm_units_list:
            asm_unit_data = {
                f"{asm_unit.type}": f"{asm_unit}",  # Replace with actual attributes
                # add other asm_unit attributes as needed
            }
            block_data["asm_units"].append(asm_unit_data)

        data.append(block_data)

    config_manager = get_config_manager()
    output_dir = config_manager.get_value('output_dir_path')
    output_file = os.path.join(output_dir,"generation.json")
    # Write to a JSON file
    with open(output_file, "w") as json_file:
        json.dump(data, json_file, indent=4)

def memory_usage_json_dump():
    logger = get_logger()
    logger.info("---- memory_usage.json dump")
    state_manager = get_state_manager()
    current_state = state_manager.get_active_state()

    all_blocks = current_state.memory_manager.get_segments(pool_type=[Configuration.Memory_types.BOOT_CODE,
                                                                      Configuration.Memory_types.CODE,
                                                                      Configuration.Memory_types.DATA_SHARED,
                                                                      Configuration.Memory_types.DATA_PRESERVE])
    all_data_blocks = current_state.memory_manager.get_segments(pool_type=[Configuration.Memory_types.DATA_SHARED,
                                                                           Configuration.Memory_types.DATA_PRESERVE])

    # Prepare JSON structure with two sections: summary and detailed data
    output_data = {
        "block_summary": [], # Top-level list for block summaries
        "blocks_data_units": []  # List to store all blocks and their data_units_list
    }

    # First section: summary of available blocks
    for block in all_blocks:
        summary = {
            "block_name": block.name,
            "block_info": f"address={hex(block.address)}, byte_size={block.byte_size}, type={block.memory_type}"
        }
        output_data["block_summary"].append(summary)

    for block in all_data_blocks:
        block_data = {
            "block_name": block.name,
            "block_address": hex(block.address),
            "data_units": [],
        }
        for data_unit in block.data_units_list:
            data_unit_info = {
                f"data_unit": data_unit.data_unit_str,
                # add other asm_unit attributes as needed
            }
            block_data["data_units"].append(data_unit_info)

        output_data["blocks_data_units"].append(block_data)
        #data.append(block_data)

    config_manager = get_config_manager()
    output_dir = config_manager.get_value('output_dir_path')
    output_file = os.path.join(output_dir,"memory_usage.json")
    # Write to a JSON file
    with open(output_file, "w") as json_file:
        json.dump(output_data, json_file, indent=4)