
from Utils.logger_management import get_logger
from Utils.configuration_management import get_config_manager
from Tool.stages.final_stage.json_dump import generation_json_dump, memory_usage_json_dump
from Externals.db_manager.models import get_instruction_db
from Utils.singleton_management import SingletonManager

from Externals.binary_generation.asm_generation import generate_assembly
from Externals.binary_generation.binary_generation import generate_binary

def final_section():
    logger = get_logger()
    config_manager = get_config_manager()
    logger.info("======== final_section")

    generation_json_dump()
    memory_usage_json_dump()

    generate_assembly()

    # when in 'Cloud_mode' there is no need to run assembler and linker
    cloud_mode = config_manager.get_value('Cloud_mode')
    if not cloud_mode:
        generate_binary()

    # def assemble_and_run_riscv(assembly_code, output_file="program.elf"):
    logger.info("Finalizing...")
    # Add any cleanup or final logic here
    close_instruction_db()


def close_instruction_db():
    logger = get_logger()
    # Close the database connection
    Instruction = get_instruction_db()
    Instruction._meta.database.close()

    logger.debug(f"------ close DB connection")


def reset_tool():
    """
    Reset tool states (e.g., factories, settings, ...).
    this is needed when running under cloud mode and rerun the tool without reinitialize all its instances.
    """
    logger = get_logger()
    logger.debug(f"------ reset_tool")
    # resetting logger
    logger_manager = get_logger(get_manager=True)
    logger_manager.clean_logger()

    # resetting all managers, including State, logger, Configuration, Knobs, ingredients, scenarios...
    SingletonManager.reset()


