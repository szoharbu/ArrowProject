import os
import sys
import time
import traceback
from pathlib import Path
from Arrow.Externals.cloud.upload_run_statistics import upload_statistics


def main(args=None):
    start_time = time.time()

    ensure_correct_setting()

    from Arrow.Utils.arg_parser.arg_parser import parse_arguments
    from Arrow.Utils.logger_management import get_logger
    from Arrow.Utils.configuration_management import get_config_manager
    from Arrow.Utils.statistics_managment import get_statistics_manager

    set_basedir_path()

    logger = get_logger()
    parse_arguments(args)
    logger.info("==== Arrow main")

    try:

        from Arrow.Tool.stages import input_stage, evaluation_stage, init_stage, test_stage, final_stage

        input_stage.read_inputs()  # Read inputs, read template, read configuration, ARM/riscv, ...
        evaluation_stage.evaluate_section()  # review all configs and knobs, set them according to some logic and seal them ...
        init_stage.init_section()  # initialize the state, register, memory and other managers.
        test_stage.test_section()  # boot, body (foreach core, foreach scenario), test final

        logger.info("Test generated successful :)")
        dump_time(start_time, "Test generation")

        final_stage.final_section()  # post flows, generate binary, upload to cloud, etc.

    except Exception as e:
        logger.warning("Test failed :(")
        duration = dump_time(start_time, "Test total")
        upload_statistics(duration, run_status='Fail')
        logger.error("Test failed :(\n%s", traceback.format_exc())  # Logs the full error and traceback once
        raise

    else:
        # Test was successful

        statistics_manager = get_statistics_manager()
        logger.info(
            f"Test generated {statistics_manager.get('scenario_count')} scenarios and {statistics_manager.get('asm_unit_count')} instructions")

        duration = dump_time(start_time, "Test total")
        upload_statistics(duration, run_status='Pass')
        logger.info("Test was successful :)\n")
        logger.info("Mission accomplished...")

    finally:
        config_manager = get_config_manager()
        cloud_mode = config_manager.get_value('Cloud_mode')
        if cloud_mode:
            logger.info(f"Ending main in cloud_mode, resetting tool structures")
            from Arrow.Tool.stages import final_stage
            final_stage.reset_tool()

    return True


def dump_time(start_time, message_header=None) -> str:
    from Arrow.Utils.logger_management import get_logger
    logger = get_logger()

    current_time = time.time()  # Capture current time
    duration = current_time - start_time  # Calculate duration
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
    from Arrow.Utils.logger_management import get_logger
    from Arrow.Utils.configuration_management import get_config_manager

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
    required_dirs = ["Arrow", "Externals", "Tool"]  # Directories that should exist in the project root
    cwd = os.getcwd()
    for dir_name in required_dirs:
        if not os.path.isdir(os.path.join(cwd, "Arrow", dir_name)):
            raise RuntimeError(
                f"Invalid working directory: {cwd}\n"
                f"Please run this script from the project root directory, e.g., 'ArrowProject/' and not 'ArrowProject/Arrow/'."
            )


if __name__ == "__main__":
    main()
