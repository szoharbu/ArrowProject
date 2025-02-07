
import os
import subprocess
import sys
from Utils.configuration_management import get_config_manager
from Externals.binary_generation.utils import run_command, check_file_exists, check_tool_exists, trim_path, BuildPipeline


class ArmBuildPipeline(BuildPipeline):
    def __init__(self):
        """
        Converts an ARM assembly file into an executable.

        Steps:
            1. Assemble the `.s` file into an object file using `as`.
            2. Link the object file into an executable ELF file using `ld`.
            3. Optionally verify the ELF file using `objdump`.
        """
        self.toolchain_prefix = "aarch64-none-elf"

    def cpp_to_asm(self, cpp_file, asm_file):
        """
        Compiles a C++ file to assembly using the given toolchain.
        """

        #tool = f"{self.toolchain_prefix}-g++"
        tool = "g++"
        check_tool_exists(tool)

        cpp_assemble_cmd = [tool , "-S", "-o", asm_file, cpp_file]
        check_file_exists(cpp_file, "CPP Source File")
        run_command(cpp_assemble_cmd, f"CPP Assembling '{trim_path(cpp_file)}' to '{trim_path(asm_file)}'")

    def assemble(self, assembly_file, object_file):
        """
        Assembles an assembly file into an object file.
        """
        #tool = f"{self.toolchain_prefix}-as"
        tool = "as"
        check_tool_exists(tool)
        extension = "-march=armv9-a+cssc"

        assemble_cmd = [tool, extension, "-o", object_file, assembly_file]
        check_file_exists(assembly_file, "Assembly File")
        run_command(assemble_cmd, f"Assembling '{assembly_file}' to '{object_file}'")

    def link(self, object_file, executable_file):
        """
        Link the object file into an executable ELF file using `ld`.
        """
        #tool = f"{self.toolchain_prefix}-ld"
        tool = "ld"
        check_tool_exists(tool)

        link_cmd = [tool, "-o", executable_file, object_file]
        check_file_exists(object_file, "Object File")
        run_command(link_cmd, f"Linking '{object_file}' to '{executable_file}'")


def arm_assemble_and_link():
    """
    Converts an ARM assembly file into an executable.

    Steps:
        1. Assemble the `.s` file into an object file using `as`.
        2. Link the object file into an executable ELF file using `ld`.
        3. Optionally verify the ELF file using `objdump`.
    """
    # Define file names
    config_manager = get_config_manager()
    output_dir = config_manager.get_value('output_dir_path')
    content_dir_path = config_manager.get_value('content_dir_path')

    assembly_file = config_manager.get_value('asm_file')

    toolchain_prefix = "aarch64-none-elf"

    # Ensure the input file exists
    if not os.path.isfile(assembly_file):
        print(f"Error: Assembly file '{assembly_file}' does not exist.")
        sys.exit(1)

    # Extract base file name (without extension) for output files
    base_name = os.path.splitext(os.path.basename(assembly_file))[0]

    # Define output file paths
    object_file = os.path.join(output_dir, f"{base_name}.o")
    executable_file = os.path.join(output_dir, f"{base_name}.elf")


    try:
        # Define output file paths
        cpp_object_file = os.path.join(output_dir, f"{base_name}_cpp.o")
        cpp_asm_file = os.path.join(output_dir, f"{base_name}_cpp.s")
        cpp_file = os.path.join(content_dir_path, "ingredients","fibonacci","fibonacci.cpp")

        # Generate Assembly from C++ Source
        #aarch64-none-elf-g++ -S -o Output/fibonacci.s fibonacci.cpp
        cpp_assemble_cmd = [
            f"{toolchain_prefix}-g++",
            "-S",  # Assembler command
            "-o", cpp_asm_file,  # Output file
            cpp_file  # Input cpp file
        ]
        print(f"---- CPP Assembling '{cpp_file}' into object file using '{" ".join(cpp_assemble_cmd)}'")
        subprocess.run(cpp_assemble_cmd, check=True)
        print(f"---- CPP Assembly successful: Object file created: {cpp_asm_file}")

        # Concatenate the 2 Files
        try:
            with open(assembly_file, "a") as outfile:  # Open output file in append mode
                with open(cpp_asm_file, "r") as infile:
                    outfile.write(infile.read())  # Append content
                    outfile.write("\n")  # Optionally add a newline for separation
            print(f"---- Content from {cpp_asm_file} appended to {assembly_file}")
        except Exception as e:
            print(f"Error during file appending: {e}")
    except subprocess.CalledProcessError as e:
        print(f"Error during toolchain execution: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

    try:
        # Step 1: Assemble the assembly file into an object file
        assemble_cmd = [
            f"{toolchain_prefix}-as",  # Assembler command
            "-o", object_file,  # Output file
            assembly_file  # Input assembly file
        ]
        print(f"---- Arm Assembling '{assembly_file}' into object file using '{" ".join(assemble_cmd)}'")
        subprocess.run(assemble_cmd, check=True)
        print(f"---- Arm Assembly successful: Object file created: {object_file}")

        # # Define output file paths
        # cpp_object_file = os.path.join(output_dir, f"{base_name}_cpp.o")
        # cpp_asm_file = os.path.join(output_dir, f"{base_name}_cpp.s")
        # cpp_file = os.path.join(output_dir, "..\\Submodules\\Content\\ingredients\\fibonacci\\fibonacci.cpp")
        #
        # # Generate Assembly from C++ Source
        # #aarch64-none-elf-g++ -S -o Output/fibonacci.s fibonacci.cpp
        # cpp_assemble_cmd = [
        #     f"{toolchain_prefix}-g++",
        #     "-S",  # Assembler command
        #     "-o", cpp_asm_file,  # Output file
        #     cpp_file  # Input cpp file
        # ]
        # print(f"---- CPP Assembling '{cpp_file}' into object file using '{" ".join(cpp_assemble_cmd)}'")
        # subprocess.run(cpp_assemble_cmd, check=True)
        # print(f"---- CPP Assembly successful: Object file created: {cpp_asm_file}")
        #
        # # Concatenate the 2 Files
        # try:
        #     with open(assembly_file, "a") as outfile:  # Open output file in append mode
        #         with open(cpp_asm_file, "r") as infile:
        #             outfile.write(infile.read())  # Append content
        #             outfile.write("\n")  # Optionally add a newline for separation
        #     print(f"---- Content from {cpp_asm_file} appended to {assembly_file}")
        # except Exception as e:
        #     print(f"Error during file appending: {e}")


        # TODO:: the below complie the cpp into an object file and then link two obj files into one.
        # this is less recommended as its harder to debug as the cpp is not visable in the main asm file.
        '''        
        # aarch64-none-elf-g++ -c -o Output\\test_cpp.o ..\\Submodules\\Content\\ingredients\\fibonacci\\fibonacci.cpp
        compile_cmd = [
            f"{toolchain_prefix}-g++",
            "-c",  # Assembler command
            "-o", cpp_object_file,  # Output file
            cpp_file  # Input cpp file
        ]
        print(f"---- CPP compiling '{cpp_file}' into object file using '{" ".join(compile_cmd)}'")
        subprocess.run(compile_cmd, check=True)
        print(f"---- CPP compilation successful: Object file created: {cpp_object_file}")
        # Step 2: Link the object file into an executable ELF file
        link_cmd = [
            f"{toolchain_prefix}-ld",  # Linker command
            "-o", executable_file,  # Output ELF file
            object_file,  # Input object file
            cpp_object_file # Input cpp object file
        ]
        '''


        # Step 2: Link the object file into an executable ELF file
        link_cmd = [
            f"{toolchain_prefix}-ld",  # Linker command
            "-o", executable_file,  # Output ELF file
            object_file,  # Input object file
        ]
        print(f"---- Arm Linking object file '{object_file}' into executable ELF file using '{" ".join(link_cmd)}'")
        subprocess.run(link_cmd, check=True)
        print(f"---- Arm link successful: Executable file created: {executable_file}")

        # # Step 3: Verify the ELF file (optional)
        # print(f"Verifying the ELF file...")
        # objdump_cmd = [
        #     f"{toolchain_prefix}-objdump",  # Objdump command
        #     "-d",  # Disassemble
        #     executable_file  # Input ELF file
        # ]
        # subprocess.run(objdump_cmd, check=True)
        # print(f"ELF file verified successfully.")

    except subprocess.CalledProcessError as e:
        print(f"Error during toolchain execution: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)
