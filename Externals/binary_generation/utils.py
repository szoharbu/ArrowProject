import shutil
import subprocess
import os
from Utils.logger_management import get_logger



class BuildPipeline:
    def cpp_to_asm(self, cpp_file, cpp_asm_file):
        raise NotImplementedError("Subclasses must implement this method.")

    def assemble(self, asm_file, obj_file):
        raise NotImplementedError("Subclasses must implement this method.")

    def link(self, obj_file, executable_file):
        raise NotImplementedError("Subclasses must implement this method.")

    def append_files(self, input_file, output_file, fail_on_error=True):
        """
        Appends content of one file to another.
        """
        logger = get_logger()
        check_file_exists(input_file, "Input File")
        try:
            with open(output_file, "a") as outfile:
                with open(input_file, "r") as infile:
                    outfile.write(infile.read())
                    outfile.write("\n")
            logger.debug(f"---- Content from {input_file} appended to {output_file}")
        except Exception as e:
            error_msg = f"Error appending {input_file} to {output_file}: {str(e)}"
            if fail_on_error:
                raise RuntimeError(error_msg)
            else:
                logger.warning(f"Warning: {error_msg}")


def check_tool_exists(tool):
    """
    Check if a given tools is available in PATH.

    Args:
        tool: a tool command to check (e.g., ['aarch64-none-elf-g++', 'aarch64-none-elf-as']).
    """
    from Utils.configuration_management import Configuration
    logger = get_logger()
    if shutil.which(tool) is None:
        error_str = (f"Missing required tool {tool} in PATH\n"
                     f"Ensure you have {Configuration.Architecture.arch_str} toolchain installed.\n")

        if Configuration.Architecture.riscv:
            error_str = (error_str + "Installation instructions:\n"
                         "  - Ubuntu: sudo apt install gcc-riscv64-unknown-elf binutils-riscv64-unknown-elf\n"
                         "  - Arch Linux: sudo pacman -S riscv64-elf-binutils riscv64-elf-gcc\n"
                         "  - Manual: https://github.com/riscv-collab/riscv-gnu-toolchain")

        raise FileNotFoundError(error_str)
    else:
        logger.debug(f"Required tool {tool} is available.")

def run_command(command, description, fail_on_error=True):
    """
    Runs a shell command and provides robust error handling.
    """
    logger = get_logger()
    try:
        logger.info(f"---- Running: '{" ".join(command)}'")
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        logger.info(f"---- Success: {description}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        error_msg = f"Error during {description}: {e.stderr or e.output}"
        if fail_on_error:
            raise RuntimeError(error_msg)
        else:
            logger.warning(f"Warning: {error_msg}")
            return None

def check_file_exists(filepath, description, fail_on_missing=True):
    """
    Ensures the file exists before proceeding.
    """
    logger = get_logger()
    if not os.path.isfile(filepath):
        error_msg = f"{description} not found: {filepath}"
        if fail_on_missing:
            raise RuntimeError(error_msg)
        else:
            print(f"Warning: {error_msg}")
            return False
    return True

def trim_path(path, keep_last=3):
    """
    Trims a path to include only the last `keep_last` segments.

    Args:
        path (str): The full path to be trimmed.
        keep_last (int): Number of segments to keep from the end of the path.

    Returns:
        str: The trimmed path.
    """
    path_parts = os.path.normpath(path).split(os.sep)
    return os.sep.join(path_parts[-keep_last:])

