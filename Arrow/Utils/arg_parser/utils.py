import os
from pathlib import Path
import shutil
from Arrow.Utils.logger_management import get_logger
from Arrow.Utils.configuration_management import get_config_manager
from Arrow.Utils.configuration_management.enums import Architecture

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
    
    # Always get base_dir since we need it for internal content
    base_dir = config_manager.get_value('base_dir_path')

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
        external_content_base_path = Path(base_dir).resolve() / ".." / 'Submodules' / 'arrow_content'/ 'content_repo' / 'content'
        external_content_base_path = Path(external_content_base_path).resolve()
        logger.debug(f"Derived submodule content path from base_dir: {external_content_base_path}")
        # Ensure the content directory exists
        if not external_content_base_path.exists() or not external_content_base_path.is_dir():
            external_content_base_path = f"External-content-not-available"
    config_manager.set_value('external_content_dir_path', external_content_base_path)

    internal_content_base_path = Path(base_dir).resolve() / ".." / 'Internal_content'
    internal_content_base_path = Path(internal_content_base_path).resolve()
    config_manager.set_value('internal_content_dir_path', internal_content_base_path)

    # Check for template in both internal and external content
    internal_template_path = internal_content_base_path / template_file_path
    internal_template_path = Path(internal_template_path).resolve()
    internal_exists = internal_template_path.exists() and internal_template_path.is_file()
    
    external_template_path = None
    external_exists = False
    if external_content_base_path != "External-content-not-available":
        external_content_base_path = Path(external_content_base_path).resolve()
        external_template_path = external_content_base_path / template_file_path
        external_template_path = Path(external_template_path).resolve()
        external_exists = external_template_path.exists() and external_template_path.is_file()
    
    # Handle conflicts - error on ambiguity for relative paths
    if internal_exists and external_exists:
        # Conflict detected - this is ambiguous for relative paths
        error_msg = f"Template '{template_file_path}' found in both internal and external content:\n"
        error_msg += f"  - Internal: {internal_template_path}\n"
        error_msg += f"  - External: {external_template_path}\n"
        error_msg += f"Please use the full path to specify which template you want to use."
        
        logger.error(error_msg)
        raise ValueError(f"Ambiguous template path '{template_file_path}' - found in both internal and external content. Use full path to resolve conflict.")
    elif internal_exists:
        logger.debug(f"Template file found in Internal content directory: {internal_template_path}")
        config_manager.set_value('template_path', internal_template_path)
        return
    elif external_exists:
        logger.debug(f"Template file found in External content directory: {external_template_path}")
        config_manager.set_value('template_path', external_template_path)
        return

    # Step 4: Check if the file exists as a full path
    full_template_path = Path(template_file_path).resolve()
    if full_template_path.exists() and full_template_path.is_file():
        logger.debug(f"Template file found at full path: {full_template_path}")
        config_manager.set_value('template_path',full_template_path)
        return

    # Log and raise an error if the file could not be located
    error_msg = f"Template file '{template_file_path}' not found in:\n"
    error_msg += f"  - Internal content: {internal_content_base_path}\n"
    if external_content_base_path != "External-content-not-available":
        error_msg += f"  - External content: {external_content_base_path}\n"
    error_msg += f"  - As full path: {template_file_path}"
    
    logger.error(error_msg)
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

    # SAFETY CHECKS - only allow deletion of configured output directory
    if os.path.exists(output_dir):
        has_summary_log = os.path.exists(os.path.join(output_dir, "summary.log"))
        
        # Allow deletion only if the directory contains summary.log (indicating previous output)
        # This ensures we're not accidentally deleting a directory that was never used as output
        if not has_summary_log:
            # Additional safety: check if it's not a critical system directory
            abs_output_dir = os.path.abspath(output_dir)
            critical_paths = ["/", "/home", "/usr", "/etc", "/var", "/bin", "/sbin"]
            
            if abs_output_dir in critical_paths or abs_output_dir == os.path.expanduser("~"):
                raise ValueError(
                    f"Refusing to delete directory: {output_dir}\n"
                    f"This appears to be a critical system directory or home directory.\n"
                    f"Please use a subdirectory for output."
                )
            
            logger.debug(f"Output directory exists but has no summary.log - will clean it anyway as it's the configured output directory: {output_dir}")

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
