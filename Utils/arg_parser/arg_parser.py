import argparse
import sys
from Utils.logger_management import get_logger
from Utils.configuration_management import get_config_manager, get_knob_manager
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
    knob_manager = get_knob_manager()

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

    parser.add_argument('--cloud_mode', choices=['True', 'False'],
                        help="is Cloud_mode enable, ('True', 'False').")

    parser.add_argument('--execution_platform', choices=['baremetal', 'linked_elf'],
                        help="execution_platform to run with, ('baremetal', 'linked_elf').")

    parser.add_argument('--upload_statistics', choices=['True', 'False'],
                        help="Upload run statistics at test end, ('True', 'False').")

    parser.add_argument('--create_binary', choices=['True', 'False'],
                        help="Continue with binary creation or stop at generation stage, ('True', 'False').")

    parser.add_argument('--identifier', type=str, help='Identifier to use during statistics upload.')

    parser.add_argument('--debug_mode', choices=['True', 'False'],
                        help="Run Arrow with additional debug prints checking logic, ('True', 'False').")

    parser.add_argument('--instruction_debug_prints', choices=['True', 'False'],
                        help="Run Arrow with additional debug prints checking logic, ('True', 'False').")


    # Optional argument: --define or -D (multiple key-value pairs)
    parser.add_argument('-D', '--define', action='append',
                        help="Define knobs in the format key=value. Can be used multiple times.")


    # Parse the arguments
    args = parser.parse_args(input_args) if input_args else parser.parse_args()

    # Update configurations based on arguments

    # Get the full command line as a string
    command_line_string = ' '.join(sys.argv)
    config_manager.set_value('command_line_string', command_line_string)



    # Logic based on the parsed arguments
    setup_template_and_content(args.template, args.content)
    template = config_manager.get_value('template_path')
    internal_content_path = config_manager.get_value('internal_content_dir_path')
    external_content_path = config_manager.get_value('external_content_dir_path')
    logger.info(f"--------------- Template: {template}")
    logger.info(f"--------------- Internal Content directory: {internal_content_path}")
    if external_content_path != "External-content-not-available":
        logger.info(f"--------------- External Content directory: {external_content_path}")

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

    #logger.info(f"--------------- Environment: {args.env}")

    if args.arch:
        logger.info(f"--------------- architecture: {args.arch}")
        config_manager.set_value('Architecture', args.arch)
    else:
        arch = 'riscv'
        logger.info(f"--------------- architecture: {arch} (default)")
        config_manager.set_value('Architecture', arch)
    setup_chosen_architecture()

    if args.cloud_mode:
        cloud_mode = True if (args.cloud_mode == "True") else False
        logger.info(f"--------------- Cloud_mode: {cloud_mode}")
    else:
        cloud_mode = False
        logger.info(f"--------------- Cloud_mode: {cloud_mode} (default)")
    config_manager.set_value('Cloud_mode', cloud_mode)

    if args.execution_platform:
        logger.info(f"--------------- execution_platform: {args.execution_platform}")
        config_manager.set_value('Execution_platform', args.execution_platform)
    else:
        execution_platform = 'linked_elf'
        logger.info(f"--------------- execution_platform: {execution_platform} (default)")
        config_manager.set_value('Execution_platform', execution_platform)

    if args.upload_statistics:
        upload_statistics = True if (args.upload_statistics == "True") else False
        logger.info(f"--------------- upload_statistics: {upload_statistics}")
    else:
        upload_statistics = True
        logger.info(f"--------------- upload_statistics: {upload_statistics} (defaults)")
    config_manager.set_value('Upload_statistics', upload_statistics)

    if args.identifier:
        logger.info(f"--------------- identifier: {args.identifier}")
        config_manager.set_value('Identifier', args.identifier)

    if args.debug_mode:
        debug_mode = True if (args.debug_mode == "True") else False
        logger.info(f"--------------- debug_mode: {debug_mode}")
    else:
        debug_mode = True
        logger.info(f"--------------- debug_mode: {debug_mode} (defaults)")
    config_manager.set_value('Debug_mode', debug_mode)

    if args.instruction_debug_prints:
        instruction_debug_prints = True if (args.instruction_debug_prints == "True") else False
        logger.info(f"--------------- instruction_debug_prints: {instruction_debug_prints}")
    else:
        instruction_debug_prints = False
        logger.info(f"--------------- instruction_debug_prints: {instruction_debug_prints} (defaults)")
    config_manager.set_value('Instruction_debug_prints', instruction_debug_prints)


    if args.create_binary:
        create_binary = True if (args.create_binary == "True") else False
        logger.info(f"--------------- create_binary: {create_binary}")
    else:
        create_binary = True
        logger.info(f"--------------- create_binary: {create_binary} (defaults)")
    config_manager.set_value('Create_binary', create_binary)


    # when in 'Cloud_mode' there is no need to Continue with Binary creation unless explicitly asked for
    if args.cloud_mode == "True":
        if args.create_binary != "True":
            config_manager.set_value('Create_binary', False)

    # Process --define arguments
    if args.define:
        for item in args.define:
            if '=' in item:
                key, value = item.split('=', 1)
                logger.info(f"--------------- defines: {key}={value}")
                knob_manager.override_knob(key,value)
            else:
                raise ValueError(f"Invalid format for --define: {item}. Expected format is key=value.")

    return args

