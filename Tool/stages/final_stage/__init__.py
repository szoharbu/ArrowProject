from Utils.logger_management import get_logger
from Utils.configuration_management import get_config_manager
from Tool.stages.final_stage.json_dump import generation_json_dump, memory_usage_json_dump
from Externals.db_manager.models import get_instruction_db
from Utils.singleton_management import SingletonManager

from Externals.binary_generation.asm_generation import generate_assembly
from Externals.binary_generation.binary_generation import generate_binary
from Externals.binary_generation.pgt_page_table_generation import run_PGT_prototype

def final_section():
    logger = get_logger()
    config_manager = get_config_manager()
    logger.info("======== final_section")

    generation_json_dump()
    memory_usage_json_dump()


    enable_mmu = True # config_manager.get_value('Enable_MMU')
    if enable_mmu:
        run_PGT_prototype()

    generate_assembly()

    create_binary = config_manager.get_value('Create_binary')
    if create_binary:
        try:
            generate_binary()
        except Exception as e:
            logger.error("Binary creation failed :(   if Binary is not needed please try running with '--create_binary False' ")
            raise

    # def assemble_and_run_riscv(assembly_code, output_file="program.elf"):
    logger.info("Finalizing...")
    # Add any cleanup or final logic here
    close_instruction_db()


def close_instruction_db():
    logger = get_logger()
    # Close the database connection
    db_models = get_instruction_db()
    
    if isinstance(db_models, dict):
        # ARM case - returns dict with Instruction and Operand models
        Instruction = db_models['Instruction']
        Instruction._meta.database.close()
    else:
        # Standard case - returns Instruction model directly
        db_models._meta.database.close()

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


