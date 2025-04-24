import os
from Utils.logger_management import get_logger
from Utils.configuration_management import Configuration, get_config_manager
from Externals.binary_generation.arm_binary import ArmBuildPipeline
from Externals.binary_generation.riscv_binary import RiscvBuildPipeline
from Externals.binary_generation.x86_binary import x86BuildPipeline


def generate_binary():
    logger = get_logger()
    config_manager = get_config_manager()

    # Define output file paths
    output_dir = config_manager.get_value('output_dir_path')

    internal_content_dir_path = config_manager.get_value('internal_content_dir_path')

    assembly_file = config_manager.get_value('asm_file')
    # Extract base file name (without extension) for output files
    base_name = os.path.splitext(os.path.basename(assembly_file))[0]
    # TODO:: refactor it, currently hard coded pointing to fibonacci only
    cpp_file = os.path.join(internal_content_dir_path, "ingredients","fibonacci","fibonacci.cpp")
    cpp_asm_file = os.path.join(output_dir, f"{base_name}_cpp_asm.s")
    object_file = os.path.join(output_dir, f"{base_name}.o")
    executable_file = os.path.join(output_dir, f"{base_name}.elf")
    iss_prerun_log_file = os.path.join(output_dir, f"{base_name}_iss_prerun.log")

    pipeline = None
    if Configuration.Architecture.x86:
        pipeline = x86BuildPipeline()
    elif Configuration.Architecture.arm:
        pipeline = ArmBuildPipeline()
    elif Configuration.Architecture.riscv:
        pipeline = RiscvBuildPipeline()
    else:
        raise ValueError(f"Unknown Architecture requested")

    # TODO:: Expose as Config parameters
    fail_on_error = True
    C_file_supported = False
    if C_file_supported:

        # TODO:: check if C files exist, or else skip the step

        # Step 1: Compile C++ to Assembly
        pipeline.cpp_to_asm(cpp_file, cpp_asm_file)

        # Step 2: Append files
        pipeline.append_files(cpp_asm_file, assembly_file)

    # Step 3: Assemble the final assembly file into an object file
    pipeline.assemble(assembly_file, object_file)

    # Step 4: Link the object file into an executable ELF file
    pipeline.link(object_file, executable_file)

    # Step 5: Run the executable on ISS
    pipeline.golden_reference_simolator(executable_file, iss_prerun_log_file)

    logger.info("---- Build process completed successfully!")
