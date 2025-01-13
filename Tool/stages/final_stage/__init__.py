
from Utils.logger_management import get_logger
from Tool.stages.final_stage.json_dump import generation_json_dump, memory_usage_json_dump

def final_section():
    logger = get_logger()
    logger.info("======== final_section")

    generation_json_dump()
    memory_usage_json_dump()

    # generate_assembly()

    # def assemble_and_run_riscv(assembly_code, output_file="program.elf"):
    logger.info("Finalizing...")
    # Add any cleanup or final logic here

