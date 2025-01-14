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

def setup_template_and_content(template_file_path, submodule_content_path=None):
    """
    Validates the existence of a template file.

    Priority:
    1. Check if the file exists relative to the submodule content path:
       - If `submodule_content_path` is provided, use it.
       - Otherwise, derive it from `base_dir` in the configuration manager.
    2. Check if the file exists as a full path.

    Args:
        template_file_path (str): The path of the template file (relative or full).
        submodule_content_path (str, optional): Custom submodule content path to use.

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
    if submodule_content_path:
        content_base_path = Path(submodule_content_path).resolve()
        logger.debug(f"Using provided submodule content path: {content_base_path}")
    else:
        # Fallback to base_dir/submodules/content
        base_dir = config_manager.get_value('base_dir_path')
        content_base_path = Path(base_dir).resolve() / ".." / 'Submodules' / 'arrow_content'/ 'content_repo' / 'content'
        content_base_path = content_base_path.resolve()
        logger.debug(f"Derived submodule content path from base_dir: {content_base_path}")
    # Ensure the content directory exists
    if not content_base_path.exists() or not content_base_path.is_dir():
        cloud_mode = config_manager.get_value('Cloud_mode')
        if cloud_mode:
            '''
                When in Streamlit 'cloud mode',  the Submodules/content is not uploaded, and so not in use.
                # TODO:: need to fix this eventually. for now ignoring Content_path as a WA    
                Scenarios should be written locally on the template
            '''
            content_base_path = f"Not-available-in-cloud-mode"
        else:
            logger.error(f"Content path '{content_base_path}' does not exist or is not a directory.")
            raise FileNotFoundError(f"Content path '{content_base_path}' does not exist or is not a directory.")
    config_manager.set_value('content_dir_path', content_base_path)

    # Step 2: Check if the file exists relative to the content path
    relative_template_path = content_base_path / template_file_path
    if relative_template_path.exists() and relative_template_path.is_file():
        logger.debug(f"Template file found relative to content directory: {relative_template_path.resolve()}")
        config_manager.set_value('template_file', template_file_path)
        config_manager.set_value('template_path', relative_template_path)
        return

    # Step 3: Check if the file exists as a full path
    full_template_path = Path(template_file_path).resolve()
    if full_template_path.exists() and full_template_path.is_file():
        logger.debug(f"Template file found at full path: {full_template_path}")
        config_manager.set_value('template_file', full_template_path)
        config_manager.set_value('template_path',full_template_path)
        return

    # Log and raise an error if the file could not be located
    logger.error(f"Template file '{template_file_path}' not found in either the content directory '{content_base_path}' "
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

    logger.debug("============================ setup_output_directory")

    # Retrieve the output directory path from the configuration manager
    try:
        output_dir = config_manager.get_value('output_dir_path')
    except KeyError:
        logger.error("Configuration 'output_dir_path' is missing.")
        raise ValueError("The configuration key 'output_dir_path' must be set.") from None

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
        log_file = os.path.join(output_dir, 'test.log')
        log_manager = get_logger(get_manager=True)
        log_manager.setup_file_logging(log_file)
        logger.debug(f"Logging configured to file: {log_file}")
    except Exception as e:
        logger.error(f"Failed to configure logging: {e}")
        raise

