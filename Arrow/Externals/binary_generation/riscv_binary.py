import os
import re
import signal
import subprocess
from pathlib import Path
from Arrow.Utils.configuration_management import get_config_manager
from Arrow.Externals.binary_generation.utils import run_command, check_file_exists, check_tool_exists, trim_path, BuildPipeline


class RiscvBuildPipeline(BuildPipeline):
    def __init__(self):
        self.toolchain_prefix = "riscv64-unknown-elf"
        self._linker_template_name = "riscv_baremetal.ld"
        self._load_address = 0x80000000
        self._memory_length = 0x10000000  # 256MB, matches QEMU virt default
        self._last_objdump = None
        self._qemu_trace_name = "qemu_trace.log"
        self._qemu_timeout_seconds = 3

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

        linker_script = self._emit_linker_script()
        link_cmd = [
            tool,
            "-T",
            linker_script,
            "-z",
            "max-page-size=4096",
            "-nostdlib",
            "-static",
            "-o",
            executable_file,
            object_file,
        ]
        check_file_exists(object_file, "Object File")
        run_command(
            link_cmd,
            f"Linking '{trim_path(object_file)}' to '{trim_path(executable_file)}'",
        )

        objdump_file = self._generate_objdump(executable_file)
        self._last_objdump = objdump_file
        return objdump_file

    def golden_reference_simolator(self, executable_file, iss_prerun_log_file):
        """
        Run the generated ELF inside QEMU to ensure the binary boots and executes the
        expected instructions sequence.
        """
        trace_file = os.path.join(
            os.path.dirname(executable_file), self._qemu_trace_name
        )
        self._run_qemu(executable_file, iss_prerun_log_file, trace_file)
        if self._last_objdump:
            self._verify_qemu_trace(trace_file, self._last_objdump)

    # -----------------------------------------------------------------------------
    # Helper methods
    # -----------------------------------------------------------------------------

    def _emit_linker_script(self):
        """
        Emits a baremetal linker script inside the output directory and returns
        the script path.
        """
        output_dir = get_config_manager().get_value("output_dir_path")
        script_path = Path(output_dir) / self._linker_template_name
        linker_body = f"""OUTPUT_ARCH(riscv)
ENTRY(_start)

MEMORY
{{
  RAM (rxw) : ORIGIN = 0x{self._load_address:016x}, LENGTH = 0x{self._memory_length:08x}
}}

SECTIONS
{{
  . = ORIGIN(RAM);

  .text : ALIGN(4) {{
    *(.text.core0_thread0_boot_code*)
    *(.text*)
  }} > RAM

  .rodata : ALIGN(16) {{
    *(.srodata*)
    *(.rodata*)
  }} > RAM

  .data : ALIGN(16) {{
    *(.sdata*)
    *(.data*)
  }} > RAM

  .bss (NOLOAD) : ALIGN(16) {{
    *(.sbss*)
    *(.bss*)
    *(COMMON)
  }} > RAM

  PROVIDE(_stack_top = ORIGIN(RAM) + LENGTH(RAM));
  PROVIDE(end = .);
  PROVIDE(_end = .);
}}
"""
        script_path.write_text(linker_body, encoding="utf-8")
        return str(script_path)

    def _generate_objdump(self, executable_file):
        tool = f"{self.toolchain_prefix}-objdump"
        check_tool_exists(tool)
        dump_file = f"{executable_file}.objdump"
        dump_cmd = [tool, "-d", executable_file]
        run_command(
            dump_cmd,
            f"Generating objdump for '{trim_path(executable_file)}'",
            output_file=dump_file,
        )
        return dump_file

    def _run_qemu(self, executable_file, console_log_file, trace_file):
        """
        Run qemu-system-riscv64 against the generated ELF.
        """
        qemu_binary = "qemu-system-riscv64"
        check_tool_exists(qemu_binary)

        qemu_cmd = [
            qemu_binary,
            "-machine",
            "virt",
            "-cpu",
            "rv64",
            "-m",
            "256M",
            "-nographic",
            "-bios",
            "none",
            "-kernel",
            executable_file,
            "-d",
            "in_asm",
            "-D",
            trace_file,
        ]

        process = subprocess.Popen(
            qemu_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        console_output = ""
        try:
            console_output, _ = process.communicate(timeout=self._qemu_timeout_seconds)
        except subprocess.TimeoutExpired:
            process.send_signal(signal.SIGINT)
            try:
                console_output, _ = process.communicate(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                console_output, _ = process.communicate()

        if console_log_file:
            Path(console_log_file).write_text(console_output or "", encoding="utf-8")

        # qemu exits with 0 on SIGINT, but treat 130 as acceptable too
        if process.returncode not in (0, 130, -signal.SIGINT):
            raise RuntimeError(
                f"QEMU exited with unexpected code {process.returncode}. "
                "Check Arrow_output/qemu_trace.log for details."
            )

    def _verify_qemu_trace(self, trace_file, objdump_file):
        trace_addresses = self._collect_trace_addresses(trace_file)
        if not trace_addresses:
            raise RuntimeError(
                "QEMU trace file is empty. Simulation may have failed to execute."
            )

        objdump_addresses = self._collect_objdump_addresses(objdump_file)

        missing = [
            f"0x{addr:016x}"
            for addr in trace_addresses
            if addr >= self._load_address and addr not in objdump_addresses
        ]
        if missing:
            raise RuntimeError(
                "QEMU executed addresses that do not exist in the generated ELF: "
                + ", ".join(missing)
            )

    @staticmethod
    def _collect_trace_addresses(trace_file):
        pattern = re.compile(r"^0x([0-9a-fA-F]+):")
        addresses = []
        if not os.path.exists(trace_file):
            return addresses

        with open(trace_file, "r", encoding="utf-8", errors="ignore") as trace:
            for line in trace:
                match = pattern.match(line.strip())
                if match:
                    addresses.append(int(match.group(1), 16))
        return addresses

    @staticmethod
    def _collect_objdump_addresses(objdump_file):
        pattern = re.compile(r"^\s*([0-9a-fA-F]+):\s+[0-9a-fA-F]+")
        addresses = set()
        if not os.path.exists(objdump_file):
            return addresses

        with open(objdump_file, "r", encoding="utf-8", errors="ignore") as dump:
            for line in dump:
                match = pattern.match(line)
                if match:
                    addresses.add(int(match.group(1), 16))
        return addresses
