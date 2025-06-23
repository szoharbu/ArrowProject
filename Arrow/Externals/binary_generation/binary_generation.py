import os
from Arrow.Utils.logger_management import get_logger
from Arrow.Utils.configuration_management import Configuration, get_config_manager
from Arrow.Externals.binary_generation.arm_binary import ArmBuildPipeline
from Arrow.Externals.binary_generation.riscv_binary import RiscvBuildPipeline
from Arrow.Externals.binary_generation.x86_binary import x86BuildPipeline
from Arrow.Externals.binary_generation.merge_asm_objdump import merge_files

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
    objdump_file = os.path.join(output_dir, f"{base_name}.elf.objdump")
    iss_prerun_log_file = os.path.join(output_dir, f"iss_prerun.log")
    debug_aid_file = os.path.join(output_dir, f"{base_name}_debug_aid.asm")

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

    # TODO:: replace this hard-coded with a proper logic! 
    PGT_enabled=True # TODO:: replace this hard-coded with a proper logic! 
    if Configuration.Architecture.arm and PGT_enabled:

        page_table_asm_file = os.path.join(output_dir, "pgt", "pg_generic_gnu.s")
        page_table_object = os.path.join(output_dir, f"{base_name}_pg.o")
        pipeline.assemble(page_table_asm_file, page_table_object)
        
        constants_file = os.path.join(output_dir, "pgt", "pgt_constants.s")
        constants_object = os.path.join(output_dir, f"{base_name}_pg_constants.o")
        pipeline.assemble(constants_file, constants_object)

    # Step 4: Link the object file into an executable ELF file
    if Configuration.Architecture.arm and PGT_enabled:
        pipeline.link_automated(object_file, page_table_object, constants_object, executable_file)
    else:
        pipeline.link(object_file, executable_file)

    # Step 5: Run the executable on ISS
    pipeline.golden_reference_simolator(executable_file, iss_prerun_log_file)


    # Step 6: Merge the asm file with the objdump file
    merge_files(assembly_file, objdump_file, debug_aid_file)





def main():
    # File paths
    asm_file = "Arrow_output/test.asm"
    objdump_file = "Arrow_output/test.elf.objdump"
    output_file = "Arrow_output/test_merged.asm"
    
    # Check if files exist
    if not os.path.exists(asm_file):
        print(f"Error: ASM file not found: {asm_file}")
        sys.exit(1)
        
    if not os.path.exists(objdump_file):
        print(f"Error: Objdump file not found: {objdump_file}")
        sys.exit(1)
    
    print("Starting merge process...")
    merge_files(asm_file, objdump_file, output_file)
    print("Done!")


    logger.info("---- Build process completed successfully!")
