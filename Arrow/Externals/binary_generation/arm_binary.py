import os
import subprocess
import sys
import shlex
from Arrow.Utils.configuration_management import get_config_manager, Configuration
from Arrow.Tool.state_management import get_state_manager, get_current_state
from Arrow.Externals.binary_generation.utils import run_command, check_file_exists, check_tool_exists, trim_path, BuildPipeline
from Arrow.Tool.memory_management.memory_logger import get_memory_logger
from Arrow.Tool.memory_management.memlayout.page_table_manager import get_page_table_manager

class ArmBuildPipeline(BuildPipeline):
    def __init__(self):
        """
        Converts an ARM assembly file into an executable.

        Steps:
            1. Assemble the `.s` file into an object file using `as`.
            2. Link the object file into an executable ELF file using `ld`.
            3. Optionally verify the ELF file using `objdump`.
        """
        self.toolchain_prefix = "aarch64-unknown-linux-gnu"
        self.toolchain_extensions = "-march=armv9.2-a+cssc+bf16+crypto"
        # self.toolchain_emulation_extensions = "aarch64elf" # Supported emulations: aarch64linux aarch64elf aarch64elf32 aarch64elf32b aarch64elfb armelf armelfb aarch64linuxb aarch64linux32 aarch64linux32b armelfb_linux_eabi armelf_linux_eabi

    def cpp_to_asm(self, cpp_file, asm_file):
        """
        Compiles a C++ file to assembly using the given toolchain.
        """

        tool = f"{self.toolchain_prefix}-g++"
        check_tool_exists(tool)

        cpp_assemble_cmd = [tool, self.toolchain_extensions, "-S", "-o", asm_file, cpp_file]
        check_file_exists(cpp_file, "CPP Source File")
        run_command(cpp_assemble_cmd, f"CPP Assembling '{trim_path(cpp_file)}' to '{trim_path(asm_file)}'")

    def assemble(self, assembly_file, object_file):
        """
        Assembles an assembly file into an object file.
        """
        tool = f"{self.toolchain_prefix}-as"
        check_tool_exists(tool)

        assemble_cmd = [tool, self.toolchain_extensions, "-o", object_file, assembly_file]
        check_file_exists(assembly_file, "Assembly File")
        run_command(assemble_cmd, f"Assembling '{assembly_file}' to '{object_file}'")

    def parse_pgt_scatter_file(self, output_dir):
        """
        Parse the PGT scatter file to extract section names and addresses.
        
        Args:
            output_dir: The output directory where the scatter file is located
            
        Returns:
            List of tuples containing (section_name, address)
        """
        pgt_dir = os.path.join(output_dir, "pgt")
        scatter_file = os.path.join(pgt_dir, "pg.scat")
        
        if not os.path.exists(scatter_file):
            print(f"Warning: PGT scatter file not found at {scatter_file}")
            return []
            
        pgt_sections = []
        current_section = None
        current_address = None
        
        memory_logger = get_memory_logger()
        memory_logger.log(f"Parsing PGT scatter file: {scatter_file}")
        
        try:
            with open(scatter_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    
                    # Skip empty lines
                    if not line:
                        continue
                        
                    # Parse section header with address
                    if "_load" in line and "{" not in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            current_section = parts[0].replace("_load", "")
                            current_address = parts[1]
                            
                    # Parse section definition with pg.o reference
                    elif "pg.o" in line and "(" in line and ")" in line:
                        section_name = line.split("(")[1].split(")")[0].strip()
                        if current_section and current_address:
                            # Use the exact section name from the scatter file
                            pgt_sections.append((section_name, current_address))
                            memory_logger.log(f"Found PGT section: {section_name} at address {current_address}")
        except Exception as e:
            memory_logger.log(f"Error parsing scatter file: {e}")
            
        return pgt_sections
    
    def link_automated(self, object_file, page_table_object, constants_object, executable_file):
        """
        Link the object file into an executable ELF file using `ld`.
        Uses the memory segments from the state manager and PGT sections from scatter file.
        """
        memory_logger = get_memory_logger()
        memory_logger.log(f"Starting automated linking process")
        tool = f"{self.toolchain_prefix}-ld"
        check_tool_exists(tool)

        linker_file = self.extract_linker_file()
        
        # Build link command
        link_files = [object_file, page_table_object, constants_object]
        
        section_start = self.get_bsp_boot_code_start_label()
        link_cmd = [
            tool, 
            "-T", linker_file, 
            "--no-gc-sections", 
            "--allow-multiple-definition",  # Allow intentional PA overlaps for cross-core sections
            "-e", section_start,  # Entry point
            "-z", "common-page-size=4096",
            "-z", "max-page-size=4096",
            "-o", executable_file
        ] + link_files
        
        # Execute link command
        check_file_exists(object_file, "Object File")
        run_command(link_cmd, f"Linking files to produce '{executable_file}'")
        
        # Generate objdump
        tool = f"{self.toolchain_prefix}-objdump"
        dump_file = f"{executable_file}.objdump"
        dump_cmd = [tool, "-d", "-s", executable_file]
        with open(dump_file, "w") as f:
            run_command(dump_cmd, f"Generating objdump", output_file=dump_file)
            
        memory_logger.log("Automated linking completed successfully")


    def link(self, object_file, executable_file):
        raise Exception(" old link version - stop using it")

        """
        Link the object file into an executable ELF file using `ld`.
        """
        tool = f"{self.toolchain_prefix}-ld"
        check_tool_exists(tool)

        section_start = "--section-start=.text=0x80000000 --section-start=.data=0x80020000 --section-start=.bss=0x80040000 --section-start=.stack=0x80060000"  # needed to avoid lower MMIO space which is not DRAM
        section_start_split = shlex.split(
            section_start)  # needed to split the section start command before running the command
        link_cmd = [tool] + section_start_split + ["-o", executable_file, object_file]

        command_str_split = shlex.split(command_str)  # needed to split the section start command before running the command

        link_cmd = [tool, "-T", linker_file, "--no-gc-sections", "-e", "0x90000000", "-o", "Output/test.elf", "Output/test.o", "Output/test_pg.o"]


        # link_cmd = [tool, section_start, "-o", executable_file, object_file]
        check_file_exists(object_file, "Object File")
        run_command(link_cmd, f"Linking '{object_file}' to '{executable_file}'")

        # New objdump stage
        tool = f"{self.toolchain_prefix}-objdump"
        dump_file = f"{executable_file}.objdump"

        dump_cmd = [tool, "-d", "-s", executable_file]  # objdump command, -d for disassembly, -s to see all sections
        with open(dump_file, "w") as f:
            run_command(dump_cmd, f"Dumping ELF file info to '{dump_file}'", output_file=dump_file)

    def golden_reference_simolator(self, executable_file, iss_prerun_log_file):
        """
        Rerun executable ELF on ISS simolator.
        """
        runsim_tool = "/home/nvcpu-sw-co100/cosim/1.0/current/debug_arm/x86_64/bin/runsim"
        dsim_tool = "/home/nvcpu-sw-co100/ccplexsim/1.0/current/debug_arm/x86_64/lib/libdsim_dbg.so"
        tsim_tool = "/home/nvcpu-sw-co100/tsim/1.0/current/debug_arm/x86_64/lib/libtsim_develop.so"

        check_tool_exists(runsim_tool)
        check_file_exists(executable_file, "Executable File")

        file_name, file_ext = os.path.splitext(iss_prerun_log_file)
        tbox_log_file = f"{file_name}.tbox.log"

        # TODO:: refactor this code and take cores_counts from elsewhere.
        state_manager = get_state_manager()
        cpu_count = len(state_manager.get_all_states())
        # set bit for each core
        core_activation_vector = 0
        for i in range(cpu_count):
            core_activation_vector |= 1 << i


        section_start = self.get_bsp_boot_code_start_label()
        #section_start = "0x90000000"  # needed to avoid lower MMIO space which is not DRAM

        ISS_step_limit = 20000
        page_walk_log = "0x3"  # 0 - minimal, 1 - page_walk, 2 - gpt_walks, 3 - all
        # iss_flags = f"--cosim_smp --cosim_quant 1 --cosim_memquant 1 --cosim_advance 1 --cosim_cmpvec 0x30016 --cosim_startcmp 0 --cosim_s_ns_mem_duplicate --cosimtr_verbose 1 --cosim_sec_melf {executable_file} --cosim_models 1 --cosim_max 1000201 --dsim=/home/nvcpu-sw-co100/ccplexsim/1.0/cl85653745/debug_arm/x86_64/lib/libdsim_dbg.so --config.sim:platform_ns_bit_position=48 --config.core.sim:disable_tsim_platform=1 --configtsim /home/nvcpu-sw-co100/tsim/1.0/cl85653745/debug_arm/x86_64/lib/libtsim_develop.so --target olympus-dv -cpu olympus -reset_pc {section_start} -trickbox_base 0x13000000 -smp 1 -activate_coremask 1 -trickbox_log tbox_prerun.log --tsim=/home/nvcpu-sw-co100/tsim/1.0/cl85653745/debug_arm/x86_64/lib/libtsim_develop.so --target olympus-dv -cpu olympus -reset_pc {section_start} -trickbox_base 0x13000000 -smp 1 -activate_coremask 1"
        iss_flags = f"--cosim_smp --cosim_quant 1 --cosim_memquant 1 --cosim_advance 1 --cosim_s_ns_mem_duplicate --cosimtr_verbose 0 --cosim_verbose_tarmac --cosim_sec_melf {executable_file} --cosim_models 1 --cosim_fail_max {ISS_step_limit} --dsim={dsim_tool} --config.sim:platform_ns_bit_position=48 --config.core.sim:disable_tsim_platform=1 --configtsim {tsim_tool} -core_quant 1 --target olympus-dv -cpu olympus -reset_pc {section_start} -trickbox_base 0x13000000 -smp {cpu_count} -activate_coremask {core_activation_vector} -logs {page_walk_log} -trickbox_log {tbox_log_file} --tsim={tsim_tool} --target olympus-dv -cpu olympus -reset_pc {section_start} -trickbox_base 0x13000000 -smp {cpu_count} -activate_coremask {core_activation_vector}"
        iss_flags_split = shlex.split(iss_flags)  # needed before running the command
        iss_cmd = [runsim_tool] + iss_flags_split

        try:
            run_command(command=iss_cmd, description=f"Rerunning '{executable_file}' on ISS",
                        output_file=iss_prerun_log_file)
        except Exception as e:
            # checking last 10 lines of the output, if matches few knowns issues raise them, else raise the error message
            known_issues = ["time limit reached", "memory limit reached", "instruction limit reached","test fail code"]
            with open(iss_prerun_log_file, 'r') as f:
                lines = f.readlines()[-10:]
                for line in lines:
                    for issue in known_issues:
                        if issue in line:
                            # Create a new clean exception that won't get wrapped
                            e = RuntimeError(f"ISS failure: {line.strip()}\n - please check the {iss_prerun_log_file} for more details")
                            e.__cause__ = None  # This prevents the "During handling..." messages
                            raise e
            raise  # If no known issues found, re-raise the original exception

    def extract_linker_file(self):


        state_manager = get_state_manager()
        cores_states = state_manager.get_all_states()
        page_table_manager = get_page_table_manager()

        # Get configuration and output paths
        output_dir = get_config_manager().get_value('output_dir_path')
        pgt_sections = self.parse_pgt_scatter_file(output_dir)
        linker_file = os.path.join(output_dir, "automated_linker.ld")

        memory_logger = get_memory_logger()
        memory_logger.log(f"\n extract_linker_file - creating linker file {linker_file}")


        pgt_vma_base = 0xF00000000

        # Create linker script
        with open(linker_file, 'w') as f:
            # Write memory regions
            f.write("MEMORY\n{\n")
            f.write("  trickbox_mem : ORIGIN = 0x13000000, LENGTH = 0x200000\n")
            f.write("  memory_region_utilities : ORIGIN = 0x80000000, LENGTH = 0x200000000\n")
            f.write(f"  pgt_vma_base_memory_region : ORIGIN = {pgt_vma_base}, LENGTH = 0x10000000\n")

            for page_table in page_table_manager.get_all_page_tables():
            ###for state_name in cores_states:
            ###    state_manager.set_active_state(state_name)
            ###    curr_state = state_manager.get_active_state()
            ###    core_page_tables = curr_state.enabled_page_tables
            ###    for page_table in core_page_tables:
                f.write(f"  memory_region_{page_table.page_table_name} : ORIGIN = {hex(page_table.va_memory_range_start_address)}, LENGTH = {hex(page_table.va_memory_range_start_address+page_table.va_memory_range_size)}\n")
            ###state_manager.set_active_state("core_0")

            f.write("}\n\n")
            
            # Start sections
            f.write("SECTIONS\n{\n")
            f.write("  .data.trickbox 0x13000000 :\n")
            f.write("  {\n")
            f.write("    *(.data.trickbox)\n")
            f.write("  } > trickbox_mem\n\n")
            

            # Get all memory segments per state
            linked_data_segments_pa_addresses = []  # list of cross-core PA addresses that are already linked

            for page_table in page_table_manager.get_all_page_tables():
                state_segments = page_table.segment_manager.get_segments(pool_type=[
                    Configuration.Memory_types.BSP_BOOT_CODE, 
                    Configuration.Memory_types.BOOT_CODE, 
                    Configuration.Memory_types.CODE,
                    Configuration.Memory_types.DATA_SHARED, 
                    Configuration.Memory_types.DATA_PRESERVE,
                    Configuration.Memory_types.STACK
                ])

                sorted_segments = sorted(state_segments, key=lambda x: x.address)

                # Add code segments
                for segment in sorted_segments:
                    if segment.memory_type in [Configuration.Memory_types.CODE, 
                                                Configuration.Memory_types.BSP_BOOT_CODE, 
                                                Configuration.Memory_types.BOOT_CODE]:
                        memory_logger.log(f"Adding code segment: {segment.name} at {hex(segment.address)}")
                        segment_name = segment.name
                        section_name = f".text.{segment_name}"
                        
                        f.write(f"  {section_name} {hex(segment.address)} : AT({hex(segment.pa_address)})\n")
                        f.write("  {\n")
                        # Use specific patterns to match only relevant sections
                        f.write(f"    *({section_name})\n")  # Match this exact section name
                        
                        # For BSP boot segment, also include any boot-related sections
                        if segment.memory_type == Configuration.Memory_types.BSP_BOOT_CODE:
                            f.write(f"    *(.text.boot*)\n")  # Also include any boot-related sections
                            f.write(f"    *(.boot*)\n")
                        
                        #f.write("  } > main_mem\n\n")
                        f.write(f"  }} > memory_region_{page_table.page_table_name}\n\n")
                    
                    elif segment.memory_type in [Configuration.Memory_types.DATA_SHARED, 
                                                Configuration.Memory_types.DATA_PRESERVE]:
                        memory_logger.log(f"Adding data segment: {segment.name} at VA:{hex(segment.address)} PA:{hex(segment.pa_address)}")
                        segment_name = segment.name
                        section_name = f".data.{segment_name}"
                        
                        if segment.is_cross_core and segment.pa_address in linked_data_segments_pa_addresses:
                            # This PA address has already been used, omit AT() clause and use NOLOAD
                            linked_data_str = f"  {section_name} {hex(segment.address)} (NOLOAD) :\n"
                            memory_logger.log(f"Cross-core segment {segment.name} shares PA {hex(segment.pa_address)} - using NOLOAD")
                        else:
                            # First time seeing this PA address, include AT() clause
                            linked_data_str = f"  {section_name} {hex(segment.address)} : AT({hex(segment.pa_address)})\n"
                            if segment.is_cross_core:
                                linked_data_segments_pa_addresses.append(segment.pa_address)
                                memory_logger.log(f"Cross-core segment {segment.name} first occurrence at PA {hex(segment.pa_address)} - including AT() clause")

                        f.write(linked_data_str)
                        f.write("  {\n")
                        # Use specific patterns for this data segment
                        f.write(f"    *({section_name})\n")  # Match this exact section name
                        #f.write("  } > main_mem\n\n")
                        f.write(f"  }} > memory_region_{page_table.page_table_name}\n\n")
                
                # Add standard sections
                stack_data_start_address = page_table.segment_manager.get_stack_data_start_address()
                f.write(f"  .stack {hex(stack_data_start_address)} : AT({hex(stack_data_start_address)})\n")
                f.write("  {\n")
                f.write("    *(.stack)\n")
                #f.write("  } > main_mem\n\n")
                f.write(f"  }} > memory_region_{page_table.page_table_name}\n\n")
            
            # Add PGT constants section - find the constants region from PGT mappings
            constants_address = "0x801c0000"  # Default fallback
            f.write(f"  .data.pgt_constants {constants_address} : AT({constants_address})\n")
            f.write("  {\n")
            f.write("    *(.data.pgt_constants)\n")  # Match specific section, not all .data
            f.write("  } > memory_region_utilities\n\n")

            # Add PGT sections: Use unique VMA + AT() to avoid VMA conflicts
            # ARM page tables are accessed by MMU hardware via physical addresses only.
            # VMA=virtual address (can conflict), LMA=physical address (MMU requirement)
            # Solution: High VMA (0xF00000000+) for conflict avoidance, AT() for correct physical placement
            # Note: NOLOAD rejected - would cause MMU translation table walk failures
            # pgt_vma_base = 0xF00000000  # High VMA base to avoid conflicts
            for idx, (section_name, address) in enumerate(pgt_sections):
                memory_logger.log(f"Adding PGT section: {section_name} at PA {address}")
                section_name_clean = section_name.lower().replace("(", "_").replace(")", "_").replace(" ", "_")
                
                # Unique VMA per section, MMU accesses via physical address (AT clause)
                vma_address = pgt_vma_base + (idx * 0x10000)  # 64KB spacing
                f.write(f"  .data.{section_name_clean} {hex(vma_address)} : AT({address})\n")
                f.write("  {\n")
                f.write(f"    *(.data.{section_name_clean})\n")
                f.write(f"    *(.{section_name})\n")  # Original section name from PGT
                f.write("  } > pgt_vma_base_memory_region\n\n")
            
            # Close sections
            f.write("}\n")

        return linker_file

    def get_bsp_boot_code_start_label(self):
        page_table_manager = get_page_table_manager()
        page_tables = page_table_manager.get_all_page_tables()
        core_0_el3_page_table = next(page_table for page_table in page_tables if page_table.core_id == "core_0" and page_table.execution_context == Configuration.Execution_context.EL3)
        bsp_segment = core_0_el3_page_table.segment_manager.get_segments(pool_type=[Configuration.Memory_types.BSP_BOOT_CODE])
        if len(bsp_segment) != 1:
            raise ValueError(f"Expected exactly one BSP boot code segment, got {len(bsp_segment)}")
        bsp_segment = bsp_segment[0]
        return hex(bsp_segment.address)
