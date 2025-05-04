import os
import subprocess
import sys
import shlex
# from Utils.configuration_management import get_config_manager
from Tool.state_management import get_state_manager
from Externals.binary_generation.utils import run_command, check_file_exists, check_tool_exists, trim_path, \
    BuildPipeline


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

    def link(self, object_file, executable_file):
        """
        Link the object file into an executable ELF file using `ld`.
        """
        tool = f"{self.toolchain_prefix}-ld"
        check_tool_exists(tool)

        section_start = "--section-start=.text=0x80000000 --section-start=.data=0x80020000 --section-start=.bss=0x80040000 --section-start=.stack=0x80060000"  # needed to avoid lower MMIO space which is not DRAM
        section_start_split = shlex.split(
            section_start)  # needed to split the section start command before running the command
        link_cmd = [tool] + section_start_split + ["-o", executable_file, object_file]
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
        cpu_count = len(state_manager.list_states())
        # set bit for each core
        core_activation_vector = 0
        for i in range(cpu_count):
            core_activation_vector |= 1 << i

        section_start = "0x80000000"  # needed to avoid lower MMIO space which is not DRAM
        ISS_step_limit = 20000
        page_walk_log = "0x0"  # 0 - minimal, 1 - page_walk, 2 - gpt_walks, 3 - all
        # iss_flags = f"--cosim_smp --cosim_quant 1 --cosim_memquant 1 --cosim_advance 1 --cosim_cmpvec 0x30016 --cosim_startcmp 0 --cosim_s_ns_mem_duplicate --cosimtr_verbose 1 --cosim_sec_melf {executable_file} --cosim_models 1 --cosim_max 1000201 --dsim=/home/nvcpu-sw-co100/ccplexsim/1.0/cl85653745/debug_arm/x86_64/lib/libdsim_dbg.so --config.sim:platform_ns_bit_position=48 --config.core.sim:disable_tsim_platform=1 --configtsim /home/nvcpu-sw-co100/tsim/1.0/cl85653745/debug_arm/x86_64/lib/libtsim_develop.so --target projectA-dv -cpu projectA -reset_pc {section_start} -trickbox_base 0x0 -smp 1 -activate_coremask 1 -trickbox_log tbox_prerun.log --tsim=/home/nvcpu-sw-co100/tsim/1.0/cl85653745/debug_arm/x86_64/lib/libtsim_develop.so --target projectA-dv -cpu projectA -reset_pc {section_start} -trickbox_base 0x0 -smp 1 -activate_coremask 1"
        iss_flags = f"--cosim_smp --cosim_quant 1 --cosim_memquant 1 --cosim_advance 1 --cosim_s_ns_mem_duplicate --cosimtr_verbose 0 --cosim_verbose_tarmac --cosim_sec_melf {executable_file} --cosim_models 1 --cosim_fail_max {ISS_step_limit} --dsim={dsim_tool} --config.sim:platform_ns_bit_position=48 --config.core.sim:disable_tsim_platform=1 --configtsim {tsim_tool} -core_quant 1 --target projectA-dv -cpu projectA -reset_pc {section_start} -trickbox_base 0x0 -smp {cpu_count} -activate_coremask {core_activation_vector} -logs {page_walk_log} -trickbox_log {tbox_log_file} --tsim={tsim_tool} --target projectA-dv -cpu projectA -reset_pc {section_start} -trickbox_base 0x0 -smp {cpu_count} -activate_coremask {core_activation_vector}"
        iss_flags_split = shlex.split(iss_flags)  # needed before running the command
        iss_cmd = [runsim_tool] + iss_flags_split

        try:
            run_command(command=iss_cmd, description=f"Rerunning '{executable_file}' on ISS",
                        output_file=iss_prerun_log_file)
        except Exception as e:
            # checking last 10 lines of the output, if matches few knowns issues raise them, else raise the error message
            known_issues = ["time limit reached", "memory limit reached", "instruction limit reached"]
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
