import time
import traceback
from pathlib import Path
from Utils.arg_parser import parse_arguments
from Utils.logger_management import get_logger
from Utils.configuration_management import get_config_manager
from Tool.Stages import input_stage, evaluation_stage, init_stage

def main(args=None):
    start_time = time.time()
    set_basedir_path()

    logger = get_logger()
    parse_arguments(args)
    logger.info("==== Arrow main")

    try:
        input_stage.read_inputs()          # Read inputs, read template, read configuration, ARM/riscv, ...
        evaluation_stage.evaluate_section() # review all configs and knobs, set them according to some logic and seal them ...
        init_stage.init_section()           # initialize the state, register, memory and other managers.
        #test_section()           # boot, body (foreach core, foreach scenario), test final

        logger.info("Test generated successful :)")
        dump_time(start_time, "Test generation")

        #final_section()         # post flows?

    except Exception as e:
        logger.warning("Test failed :(")
        dump_time(start_time, "Test total")
        logger.error(f"Error: {e}")
        logger.error(traceback.format_exc())
    else:
        # Test was successful
        dump_time(start_time, "Test total")
        logger.info("Test was successful :)\n")
        logger.info("Mission accomplished...")

    return True


def dump_time(start_time, message_header):
    logger = get_logger()
    current_time = time.time()  # Capture current time
    duration = current_time - start_time # Calculate duration
    logger.info(f'{message_header} took {duration:.2f} seconds')


def set_basedir_path():
    """
    Sets the base directory and submodule content directory paths in the configuration manager.
    - `base_dir_path`: The directory where the script resides.
    - `submodule_content_path`: The resolved path to the submodule content directory.
    The paths are stored in the configuration manager for easy access throughout the application.
    """
    logger = get_logger()
    config_manager = get_config_manager()

    try:
        # Determine the base directory
        base_dir = Path(__file__).resolve().parent
        logger.debug(f"Base directory determined: {base_dir}")
        config_manager.set_value('base_dir_path', str(base_dir))

        # # Determine the submodule content path relative to the base directory
        # submodule_content_path = base_dir / '..' / 'Submodules' / 'arrow_content'
        # resolved_path = submodule_content_path.resolve()
        # logger.debug(f"Submodule content path resolved: {resolved_path}")
        # config_manager.set_value('submodule_content_path', str(resolved_path))

    except Exception as e:
        logger.error(f"Error setting base or submodule paths: {e}")
        raise

if __name__ == "__main__":
    main()
