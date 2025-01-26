import os
import sys
import time
import traceback
from pathlib import Path

def main(args=None):

    start_time = time.time()

    ensure_correct_setting()

    from Utils.arg_parser.arg_parser import parse_arguments
    from Utils.logger_management import get_logger
    from Utils.configuration_management import get_config_manager

    set_basedir_path()

    logger = get_logger()
    parse_arguments(args)
    logger.info("==== Arrow main")

    try:

        from Tool.stages import input_stage, evaluation_stage, init_stage, test_stage, final_stage

        input_stage.read_inputs()          # Read inputs, read template, read configuration, ARM/riscv, ...
        evaluation_stage.evaluate_section() # review all configs and knobs, set them according to some logic and seal them ...
        init_stage.init_section()           # initialize the state, register, memory and other managers.
        test_stage.test_section()           # boot, body (foreach core, foreach scenario), test final

        logger.info("Test generated successful :)")
        dump_time(start_time, "Test generation")

        final_stage.final_section()         # post flows?

    except Exception as e:
        logger.warning("Test failed :(")
        dump_time(start_time, "Test total")
        upload_data = True #config_manager.get_value('upload_data')
        if upload_data:
            upload_statistics(start_time, run_status='Fail')
        logger.error(f"Error: {e}")
        logger.error(traceback.format_exc())
        raise

    else:
        # Test was successful
        dump_time(start_time, "Test total")
        logger.info("Test was successful :)\n")
        logger.info("Mission accomplished...")

        upload_data = True #config_manager.get_value('upload_data')
        if upload_data:
            upload_statistics(start_time, run_status='Pass')

    finally:
        config_manager = get_config_manager()
        cloud_mode = config_manager.get_value('Cloud_mode')
        if cloud_mode:
            logger.info(f"Ending main in cloud_mode, resetting tool structures")
            from Tool.stages import final_stage
            final_stage.reset_tool()

    return True


def upload_statistics(start_time, run_status):
    '''
    Entry fields:
    - Name: ??
    - Template:
    - Command Line
    - Status : Pass / Fail
    - Start time
    - Duration
    '''
    from Externals.Cloud.Airtable import upload_run_statistics
    from Utils.configuration_management import get_config_manager

    config_manager = get_config_manager()
    template_path = config_manager.get_value('template_path')
    template_name = os.path.basename(template_path)
    command_line = config_manager.get_value('command_line_string')
    duration = dump_time(start_time=start_time)
    Architecture = config_manager.get_value("Architecture")
    Cloud_mode = config_manager.get_value('Cloud_mode')

    upload_run_statistics(template=template_name,
                          command_line=command_line,
                          duration=duration,
                          run_status=run_status,
                          architecture=Architecture,
                          cloud_mode=Cloud_mode,
                          )


def dump_time(start_time, message_header = None) -> str:
    from Utils.logger_management import get_logger
    logger = get_logger()

    current_time = time.time()  # Capture current time
    duration = current_time - start_time # Calculate duration
    if message_header is not None:
        logger.info(f'{message_header} took {duration:.2f} seconds')
    return duration

def set_basedir_path():
    """
    Sets the base directory and submodule content directory paths in the configuration manager.
    - `base_dir_path`: The directory where the script resides.
    - `submodule_content_path`: The resolved path to the submodule content directory.
    The paths are stored in the configuration manager for easy access throughout the application.
    """
    from Utils.logger_management import get_logger
    from Utils.configuration_management import get_config_manager

    logger = get_logger()
    config_manager = get_config_manager()

    try:
        # Determine the base directory
        base_dir = Path(__file__).resolve().parent
        logger.debug(f"Base directory determined: {base_dir}")
        config_manager.set_value('base_dir_path', str(base_dir))

    except Exception as e:
        logger.error(f"Error setting base or submodule paths: {e}")
        raise

def ensure_correct_setting():

    """Ensure the correct Python version is used."""
    if sys.version_info < (3, 12):
        raise RuntimeError(
            f"Arrow requires Python 3.12 or higher. You are using Python {sys.version_info.major}.{sys.version_info.minor}."
        )

    """Ensure the script is being run from the project root directory."""
    required_dirs = ["Arrow", "Externals", "Submodules"]  # Directories that should exist in the project root
    cwd = os.getcwd()
    for dir_name in required_dirs:
        if not os.path.isdir(os.path.join(cwd, dir_name)):
            raise RuntimeError(
                f"Invalid working directory: {cwd}\n"
                f"Please run this script from the project root directory, e.g., 'ArrowProject/' and not 'ArrowProject/Arrow/'."
            )

if __name__ == "__main__":
    main()
