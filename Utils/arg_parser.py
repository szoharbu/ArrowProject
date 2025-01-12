import argparse
import os
from pathlib import Path
import shutil
from Utils.logger_management import get_logger

def parse_arguments(input_args=None):
    logger = get_logger()
    logger.info("======================== parse_arguments")

    # Initialize the argument parser
    parser = argparse.ArgumentParser(description="Process a template with optional overrides.")

    # Optional argument: --output (optional)
    parser.add_argument('--output', type=str, help='Path to the output directory.')

    # Optional argument: --arch (optional, with choices x86/riscv/arm)
    parser.add_argument('--arch', choices=['x86', 'riscv', 'arm'],
                        help="Architecture to run with, ('x86', 'riscv', 'arm').")

    if input_args is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(input_args)

    if args.output:
        logger.info(f"--------------- Output directory: {args.output}")
    else:
        logger.info(f"--------------- Output directory: Output (default)")

    if args.arch:
        logger.info(f"--------------- architecture: {args.arch}")
    else:
        arch = 'riscv'
        logger.info(f"--------------- architecture: {arch} (default)")

    return args
