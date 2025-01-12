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
            logger.info(f"Cleaning existing output directory: {output_dir}")
            shutil.rmtree(output_dir)
        else:
            logger.info(f"Output directory does not exist, creating: {output_dir}")

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
        logger.info(f"Logging configured to file: {log_file}")
    except Exception as e:
        logger.error(f"Failed to configure logging: {e}")
        raise

