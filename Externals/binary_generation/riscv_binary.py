from Externals.binary_generation.utils import run_command, check_file_exists, check_tool_exists, trim_path, BuildPipeline

class RiscvBuildPipeline(BuildPipeline):
    def __init__(self):
        """
        Converts a RISC-V assembly file into an executable.
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


    # config_manager = get_config_manager()
    # output_dir = config_manager.get_value('output_directory')
    # asm_file = os.path.join(output_dir,"asm_file.s")
    # object_file = os.path.join(output_dir,"object_file.o")
    # # Write assembly code to a .s file
    # with open(asm_file, "w") as asm_f:
    #     asm_f.write(assembly_code)

#     # Assemble the code into an object file
#     try:
#         subprocess.run(["riscv64-unknown-elf-as", "-o", object_file, asm_file], check=True)
#         print("Assembled program.o successfully.")
#     except subprocess.CalledProcessError:
#         print("Error during assembly.")
#         return
#
#
# #
#
# def assemble_and_run_riscv(assembly_code, output_file="program.elf"):

#
#     # Link the object file into an ELF executable
#     try:
#         subprocess.run(["riscv64-unknown-elf-ld", "-o", output_file, "program.o"], check=True)
#         print(f"Linked {output_file} successfully.")
#     except subprocess.CalledProcessError:
#         print("Error during linking.")
#         return
#
#     # Run the ELF file with QEMU emulator
#     try:
#         result = subprocess.run(["qemu-riscv64", output_file], capture_output=True, text=True, check=True)
#         print("Program output:")
#         print(result.stdout)
#     except subprocess.CalledProcessError:
#         print("Error during execution.")
#
#     # Clean up intermediate files if desired
#     os.remove("program.s")
#     os.remove("program.o")
#
#