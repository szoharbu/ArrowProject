import os
import subprocess
import sys
from Utils.configuration_management import get_config_manager
from Externals.binary_generation.utils import run_command, check_file_exists, check_tool_exists, trim_path, BuildPipeline


class RiscvBuildPipeline(BuildPipeline):
    def __init__(self):
        """
        Converts RISC-V assembly file into an executable.

        Steps:
            1. Assemble the `.s` file into an object file using `as`.
            2. Link the object file into an executable ELF file using `ld`.
            3. Optionally verify the ELF file using `objdump`.
        """
        self.toolchain_prefix = "riscv64-unknown-elf"

    def cpp_to_asm(self, cpp_file, asm_file):
        """
        Compiles a C++ file to assembly using the given toolchain.
        """

        tool = f"{self.toolchain_prefix}-g++"
        check_tool_exists(tool)

        cpp_assemble_cmd = [tool , "-S", "-o", asm_file, cpp_file]
        check_file_exists(cpp_file, "CPP Source File")
        run_command(cpp_assemble_cmd, f"CPP Assembling '{trim_path(cpp_file)}' to '{trim_path(asm_file)}'")

    def assemble(self, assembly_file, object_file):
        """
        Assembles an assembly file into an object file.
        """
        tool = f"{self.toolchain_prefix}-as"
        check_tool_exists(tool)

        assemble_cmd = [tool, "-o", object_file, assembly_file]
        check_file_exists(assembly_file, "Assembly File")
        run_command(assemble_cmd, f"Assembling '{assembly_file}' to '{object_file}'")

    def link(self, object_file, executable_file):
        """
        Link the object file into an executable ELF file using `ld`.
        """
        tool = f"{self.toolchain_prefix}-ld"
        check_tool_exists(tool)

        link_cmd = [tool, "-o", executable_file, object_file]
        check_file_exists(object_file, "Object File")
        run_command(link_cmd, f"Linking '{object_file}' to '{executable_file}'")
