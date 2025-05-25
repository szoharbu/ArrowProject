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
    available_segments = current_state.segment_manager.get_segments(pool_type=[Configuration.Memory_types.BOOT_CODE, Configuration.Memory_types.CODE])

    # Prepare data for JSON
    data = []  # List to store all segments and their asm_units_list

    for segment in available_segments:
        segment_data = {
            "segment_name": segment.name,
            "segment_address": hex(segment.address),
            "asm_units": []
        }
        for asm_unit in segment.asm_units_list:
            asm_unit_data = {
                f"{asm_unit.type}": f"{asm_unit}",  # Replace with actual attributes
                # add other asm_unit attributes as needed
            }
            segment_data["asm_units"].append(asm_unit_data)

        data.append(segment_data)

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

    all_segments = current_state.segment_manager.get_segments(pool_type=[Configuration.Memory_types.BOOT_CODE,
                                                                      Configuration.Memory_types.CODE,
                                                                      Configuration.Memory_types.DATA_SHARED,
                                                                      Configuration.Memory_types.DATA_PRESERVE])
    all_data_segments = current_state.segment_manager.get_segments(pool_type=[Configuration.Memory_types.DATA_SHARED,
                                                                           Configuration.Memory_types.DATA_PRESERVE])

    # Prepare JSON structure with two sections: summary and detailed data
    output_data = {
        "segment_summary": [], # Top-level list for segment summaries
        "segments_data_units": []  # List to store all segments and their data_units_list
    }

    # First section: summary of available segments
    for segment in all_segments:
        summary = {
            "segment_name": segment.name,
            "segment_info": f"address={hex(segment.address)}, pa_address={hex(segment.pa_address)}, byte_size={segment.byte_size}, type={segment.memory_type}"
        }
        output_data["segment_summary"].append(summary)

    for segment in all_data_segments:
        segment_data = {
            "segment_name": segment.name,
            "segment_address": hex(segment.address),
            "segment_pa_address": hex(segment.pa_address),
            "data_units": [],
        }
        for data_unit in segment.data_units_list:
            data_unit_info = {
                "data_unit": data_unit.data_unit_str,
                "data_unit_address": hex(data_unit.address),
                "data_unit_pa_address": hex(data_unit.pa_address),
                "data_unit_segment_offset": hex(data_unit.segment_offset),
                # add other asm_unit attributes as needed
            }
            segment_data["data_units"].append(data_unit_info)

        output_data["segments_data_units"].append(segment_data)
        #data.append(block_data)

    config_manager = get_config_manager()
    output_dir = config_manager.get_value('output_dir_path')
    output_file = os.path.join(output_dir,"memory_usage.json")
    # Write to a JSON file
    with open(output_file, "w") as json_file:
        json.dump(output_data, json_file, indent=4)