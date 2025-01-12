import argparse
import os
from pathlib import Path
import shutil
from Utils.logger_management import get_logger
from Utils.configuration_management import get_config_manager
from Utils.seed_management import set_seed

def parse_arguments(input_args=None):
    """
    Parses command-line arguments and updates configuration values.

    Args:
        input_args (list, optional): A list of arguments to parse. Defaults to None, which uses sys.argv.

    Returns:
        argparse.Namespace: Parsed arguments.
    """

    logger = get_logger()
    logger.info("======================== parse_arguments")

    config_manager = get_config_manager()

    # Initialize the argument parser
    parser = argparse.ArgumentParser(description="Process a template with optional overrides.")

    # Positional argument: template (required)
    parser.add_argument('template', type=str, help='The template name or path.')

    # Optional argument: --content (optional)
    parser.add_argument('--content', type=str, help='Path to the content directory.')

    # Optional argument: --output (default: 'Output')
    parser.add_argument('--output', type=str, help='Path to the output directory.')

    # Optional argument: --seed (optional)
    parser.add_argument('--seed', type=int, help='seed for reproducibility.')

    # Optional argument: --arch (optional, with choices x86/riscv/arm)
    parser.add_argument('--arch', choices=['x86', 'riscv', 'arm'],
                        help="Architecture to run with, ('x86', 'riscv', 'arm').")

    # Optional argument: --env (optional, with choices sim/emu)
    parser.add_argument('--env', choices=['sim', 'emu'], default='sim',
                        help="Environment to run in ('sim' or 'emu'). Default is 'sim'.")

    # Parse the arguments
    args = parser.parse_args(input_args) if input_args else parser.parse_args()

    # Update configurations based on arguments

    # Logic based on the parsed arguments
    setup_template_and_content(args.template, args.content)
    template = config_manager.get_value('template_file')
    content_path = config_manager.get_value('content_dir_path')
    logger.info(f"--------------- Template: {template}")
    logger.info(f"--------------- Content directory: {content_path}")


    if args.output:
        logger.info(f"--------------- Output directory: {args.output}")
        config_manager.set_value('output_dir_path', args.output)
    else:
        logger.info(f"--------------- Output directory: Output (default)")
        config_manager.set_value('output_dir_path', 'Output')
    setup_output_directory()

    if args.seed:
        logger.info(f"--------------- seed: {args.seed}")
        set_seed(args.seed)
    else:
        seed = set_seed(None)
        logger.info(f"--------------- seed: {seed} (random)")

    logger.info(f"--------------- Environment: {args.env}")

    if args.arch:
        logger.info(f"--------------- architecture: {args.arch}")
        config_manager.set_value('Architecture', args.arch)
    else:
        arch = 'riscv'
        logger.info(f"--------------- architecture: {arch} (default)")
        config_manager.set_value('Architecture', arch)

    return args



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
        content_base_path = Path(base_dir).resolve() / ".." / 'Submodules' / 'content'
        content_base_path = content_base_path.resolve()
        logger.debug(f"Derived submodule content path from base_dir: {content_base_path}")
    # Ensure the content directory exists
    if not content_base_path.exists() or not content_base_path.is_dir():
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

