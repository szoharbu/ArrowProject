import os
from pathlib import Path
import shutil
from Utils.logger_management import get_logger
from Utils.configuration_management import get_config_manager
from Utils.configuration_management.enums import Architecture

def setup_chosen_architecture():
    config_manager = get_config_manager()
    architecture = config_manager.get_value('Architecture')
    if architecture == "x86":
        Architecture.x86 = True
        Architecture.arch_str = "x86"
    elif architecture == "riscv":
        Architecture.riscv = True
        Architecture.arch_str = "riscv"
    elif architecture == "arm":
        Architecture.arm = True
        Architecture.arch_str = "arm"
    else:
        raise ValueError(f"Unknown architecture: {architecture}")

def setup_template_and_content(template_file_path, input_content_path=None):
    """
    Validates the existence of a template file.

    Priority:
    1. Check if the file exists relative to the submodule content path:
       - If `submodule_content_path` is provided, use it.
       - Otherwise, derive it from `base_dir` in the configuration manager.
    2. Check if the file exists as a full path.

    Args:
        template_file_path (str): The path of the template file (relative or full).
        input_content_path (str, optional): Custom submodule content path to use.

    Returns:
        str: The absolute path to the validated template file.

    Raises:
        FileNotFoundError: If the template file cannot be located.
        ValueError: If the `base_dir` configuration is missing and a fallback path cannot be constructed.
    """
    logger = get_logger()
    logger.debug("============================ setup_template_and_content")

    config_manager = get_config_manager()


    # Step 1: Determine the content path
    if input_content_path:
        # if provided as input by user
        external_content_base_path = Path(input_content_path).resolve()
        logger.debug(f"Using provided submodule content path: {external_content_base_path}")
        # Ensure the content directory exists
        if not external_content_base_path.exists() or not external_content_base_path.is_dir():
            logger.error(f"User provided Content path '{external_content_base_path}' does not exist or is not a directory.")
            raise FileNotFoundError(f"Content provided path '{external_content_base_path}' does not exist or is not a directory.")
    else:
        # Fallback to base_dir/submodules/content
        base_dir = config_manager.get_value('base_dir_path')
        external_content_base_path = Path(base_dir).resolve() / ".." / 'Submodules' / 'arrow_content'/ 'content_repo' / 'content'
        external_content_base_path = external_content_base_path.resolve()
        logger.debug(f"Derived submodule content path from base_dir: {external_content_base_path}")
        # Ensure the content directory exists
        if not external_content_base_path.exists() or not external_content_base_path.is_dir():
            external_content_base_path = f"External-content-not-available"
    config_manager.set_value('external_content_dir_path', external_content_base_path)

    internal_content_base_path = Path(base_dir).resolve() / ".." / 'Internal_content'
    internal_content_base_path = internal_content_base_path.resolve()
    config_manager.set_value('internal_content_dir_path', internal_content_base_path)

    # Step 2: Check if the file exists relative to the Internal content path
    relative_template_path = internal_content_base_path / template_file_path
    if relative_template_path.exists() and relative_template_path.is_file():
        logger.debug(f"Template file found relative to Internal content directory: {relative_template_path.resolve()}")
        config_manager.set_value('template_path', relative_template_path)
        return

    # Step 3: Check if the file exists relative to the External content path
    relative_template_path = external_content_base_path / template_file_path
    if relative_template_path.exists() and relative_template_path.is_file():
        logger.debug(f"Template file found relative to External content directory: {relative_template_path.resolve()}")
        config_manager.set_value('template_path', relative_template_path)
        return

    # Step 4: Check if the file exists as a full path
    full_template_path = Path(template_file_path).resolve()
    if full_template_path.exists() and full_template_path.is_file():
        logger.debug(f"Template file found at full path: {full_template_path}")
        config_manager.set_value('template_path',full_template_path)
        return

    # Log and raise an error if the file could not be located
    logger.error(f"Template file '{template_file_path}' not found in either the content directory '{external_content_base_path}' "
                 f"or as a full path.")
    raise FileNotFoundError(f"Template file '{template_file_path}' could not be located.")


def setup_output_directory():
    """
    Prepares the output directory for the application.

    - Ensures the directory exists.
    - Cleans up any existing contents in the directory.
    - Configures logging to use a log file within the output directory.
    """
    logger = get_logger()
    config_manager = get_config_manager()
    output_dir = config_manager.get_value('output_dir_path')

    logger.debug("============================ setup_output_directory")

    # Clean up the output directory if it exists
    try:
        if os.path.exists(output_dir):
            logger.debug(f"Cleaning existing output directory: {output_dir}")
            shutil.rmtree(output_dir)
        else:
            logger.debug(f"Output directory does not exist, creating: {output_dir}")

        # Create the directory
        os.makedirs(output_dir, exist_ok=True)
    except OSError as e:
        logger.error(f"Failed to clean or create output directory '{output_dir}': {e}")
        raise

    # Set up logging to a file within the output directory
    try:
        log_manager = get_logger(get_manager=True)
        log_manager.setup_output_dir(output_dir)
        logger.debug(f"Logging configured with output_dir: {output_dir}")
    except Exception as e:
        logger.error(f"Failed to configure logging: {e}")
        raise

