import subprocess
import os
import re

from Arrow.Utils.configuration_management import get_config_manager
from Arrow.Utils.logger_management import get_logger

from Arrow.Externals.binary_generation.utils import run_command, check_file_exists, check_tool_exists, trim_path, BuildPipeline


class x86BuildPipeline(BuildPipeline):

    def cpp_to_asm(self, cpp_file, cpp_asm_file):
        """
        Compiles a C++ file to assembly using the given toolchain.
        """

        tool = f"gcc"
        check_tool_exists(tool)

        #gcc -m32 -S -o program.s program.c
        cpp_assemble_cmd = [ tool, "-m64", "-S",  "-o", cpp_asm_file, cpp_file ]

        check_file_exists(cpp_file, "CPP Source File")
        run_command(cpp_assemble_cmd, f"CPP Assembling '{trim_path(cpp_file)}' to '{trim_path(cpp_asm_file)}'")


    def assemble(self, assembly_file, object_file):
        """
        Assembles an assembly file into an object file.
        """
        tool = "nasm"
        check_tool_exists(tool)

        assemble_cmd = [tool, "-f", "win64", assembly_file, "-o", object_file]
        check_file_exists(assembly_file, "Assembly File")
        run_command(assemble_cmd, f"Assembling '{assembly_file}' to '{object_file}'")

    def link(self, object_file, executable_file):
        """
        Link the object file into an executable binary file using `GCC`.
        """
        tool = "gcc"
        check_tool_exists(tool)

        link_cmd = ["gcc", object_file, "-o", executable_file, "-m64", "-lmsvcrt"]
        check_file_exists(object_file, "Object File")
        run_command(link_cmd, f"Linking '{object_file}' to '{executable_file}'")


def x86_assemble_and_link():

    logger = get_logger()
    # Define file names
    config_manager = get_config_manager()
    output_dir = config_manager.get_value('output_dir_path')
    assembly_file = config_manager.get_value('asm_file')

    # Extract base file name (without extension) for output files
    base_name = os.path.splitext(os.path.basename(assembly_file))[0]

    try:
        # Define output file paths
        cpp_asm_file = os.path.join(output_dir, f"{base_name}_cpp.s")
        cpp_file = os.path.join(output_dir, "..\\Submodules\\Content\\ingredients\\fibonacci\\fibonacci.cpp")

        # Generate Assembly from C++ Source
        #gcc -m32 -S -o program.s program.c
        cpp_assemble_cmd = [
            f"gcc",
            "-m64",  # Assembler command
            "-S",  # Assembler command
            "-o", cpp_asm_file,  # Output file
            cpp_file  # Input cpp file
        ]
        print(f"---- CPP Assembling '{cpp_file}' into object file using '{" ".join(cpp_assemble_cmd)}'")
        subprocess.run(cpp_assemble_cmd, check=True)
        print(f"---- CPP Assembly successful: Object file created: {cpp_asm_file}")

        def convert_line_to_nasm(line:str):
            print(f"old line: {line}")
            if line.startswith('.file') or line.startswith('.def') or line.startswith('.seh'):
                return "" # Skip unsupported directives
            line = line.replace('.text', 'section .text')  # Replace .text
            # Dictionary of replacements
            replacements = {
                '.globl': 'global',
                '%': '',
                'pushq': 'push',
                'subq': 'sub',
                'leaq': 'lea',
                # Add more replacements here
            }
            # line = line.replace('.globl', 'global')  # Replace .globl
            # line = line.replace('%', '')  # Remove % for registers
            # line = line.replace('pushq', 'push')  # Replace pushq
            pattern = re.compile("|".join(map(re.escape, replacements.keys())))
            new_line = pattern.sub(lambda match: replacements[match.group(0)], line)

            print(f"new line: {new_line}")
            return new_line


        # Concatenate the 2 Files
        try:
            with open(assembly_file, "a") as outfile:  # Open output file in append mode
                with open(cpp_asm_file, "r") as infile:
                    for line in infile:  # Process each line in the input file
                        nasm_line = convert_line_to_nasm(line.strip())  # Convert and strip extra whitespace
                        outfile.write(nasm_line)  # Append the converted line
                        outfile.write("\n")  # Add a newline for separation

            # with open(assembly_file, "a") as outfile:  # Open output file in append mode
            #     with open(cpp_asm_file, "r") as infile:
            #         line = infile.read()
            #         nasm_line = convert_line_to_nasm(line)
            #         outfile.write(nasm_line)  # Append content
            #         outfile.write("\n")  # Optionally add a newline for separation
            print(f"---- Content from {cpp_asm_file} appended to {assembly_file}")
        except Exception as e:
            print(f"Error during file appending: {e}")
    except subprocess.CalledProcessError as e:
        raise ValueError(f"Error during toolchain execution: {e}")
        exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        exit(1)

    object_file = os.path.join(output_dir,"test.obj")
    executable_file = os.path.join(output_dir,"test.exe")

    # Assemble with NASM
    try:
        logger.info(f"---- x86 Assembling with NASM... ")
        subprocess.run(["nasm", "-f", "win64", assembly_file, "-o", object_file], check=True)
        logger.info(f"---- x86 Assembly successful: {object_file} created.")
    except subprocess.CalledProcessError as e:
        logger.info("---- Error during assembly with NASM:", e)
        exit(1)

    # try:
    #     print("---- Running objdump -f object_file.obj ")
    #     subprocess.run(["objdump", "-f", object_file], check=True)
    # except subprocess.CalledProcessError as e:
    #     print("---- Error during assembly with NASM:", e)
    #     exit(1)
    #
    # # Link with GCC
    # try:
    #     print("---- Linking with GCC...")
    #     subprocess.run(["gcc", object_file, "-o", executable_file, "-m64", "-lmsvcrt"], check=True)
    #     print(f"---- Linking successful: {executable_file} created.")
    # except subprocess.CalledProcessError as e:
    #     print("---- Error during linking with GCC:", e)
    #     exit(1)
    #
    # # Run the executable
    # try:
    #     print(f"Running {executable_file}...\n")
    #     subprocess.run([executable_file], check=True)
    # except subprocess.CalledProcessError as e:
    #     print("Error running the executable:", e)
    # except FileNotFoundError:
    #     print("Executable not found. Please check if linking was successful.")
