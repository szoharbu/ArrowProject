import argparse
from Utils.logger_management import get_logger
from Utils.configuration_management import get_config_manager
from Utils.seed_management import set_seed
from Utils.arg_parser.utils import setup_template_and_content, setup_output_directory, setup_chosen_architecture

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
    setup_chosen_architecture()

    return args

