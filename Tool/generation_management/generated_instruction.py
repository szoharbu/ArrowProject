from Tool.memory_management.memory import Memory
from Tool.asm_blocks import AsmUnit
from Utils.configuration_management import Configuration, get_config_manager
from Tool.state_management import get_current_state


class GeneratedInstruction:
    def __init__(
            self,
            *,
            prefix: str = None,
            mnemonic: str,
            operands: list,
            comment: str,
    ):
        current_state = get_current_state()

        self.prefix = prefix
        self.mnemonic = mnemonic
        self.operands = operands
        self.comment = comment

        for i, operand in enumerate(operands):
            if isinstance(operand, Memory):
                # TODO:: we will enter this case only in x86 when memory is passed as an operand. this is not supported in linked_elf mode, and need to refactor X86 to use memory label and dynamic init!!!!
                operand.address = 0x0
                memory_hint = f" mem.address: {hex(operand.address)}"
                if operand.reused_memory:
                    memory_hint = f" reused memory {operand.unique_label} (address: {hex(operand.address)})"
                if self.comment:
                    self.comment += memory_hint
                else:
                    self.comment = memory_hint
            if isinstance(operand, int):
                if Configuration.Architecture.arm:
                    # The '#' prefix is mandatory for immediate values used in most instructions, but not for memory addresses, or constants in assembly directives
                    operands[i] = f"#{hex(operand)}"
                else:  # x86 or riscv
                    operands[i] = hex(operand)

        self.asm_unit = AsmUnit(prefix=self.prefix, mnemonic=self.mnemonic, operands=self.operands,
                                comment=self.comment)

        asl_extract = True  # TODO:: remove this after testing!!!!
        if Configuration.Architecture.arm and asl_extract:
            config_manager = get_config_manager()
            debug_mode = config_manager.get_value('Debug_mode')
            if debug_mode:
                success, error = test_asm_instruction(str(self.asm_unit))
                if success:
                    instruction_debug_prints = config_manager.get_value('Instruction_debug_prints')
                    if instruction_debug_prints:
                        print(f"        ✅  Debug mode: Generated Instruction: {self.asm_unit}")
                    current_code_block = current_state.current_code_block
                    current_code_block.asm_units_list.append(self.asm_unit)
                else:
                    instruction_debug_prints = config_manager.get_value('Instruction_debug_prints')
                    if instruction_debug_prints:
                        print(f"        ❌  Skipping invalid instruction: {self.asm_unit}")
                        single_line_error = error.replace("\n", " ")
                        print(f"                {single_line_error}")
            else:
                # print(f"    Generated Instruction: {self.asm_unit}")
                current_code_block = current_state.current_code_block
                current_code_block.asm_units_list.append(self.asm_unit)
        else:
            current_code_block = current_state.current_code_block
            current_code_block.asm_units_list.append(self.asm_unit)

    def __str__(self):
        instr = ""
        if self.prefix:
            instr += f"{self.prefix} "
        instr += f"{self.mnemonic} {', '.join(map(str, self.operands))}"
        if self.comment:
            instr += f" # {self.comment}"
        return instr


def test_asm_instruction(instruction):
    import subprocess
    import tempfile
    import os

    assembler = "aarch64-unknown-linux-gnu-as"
    flags = "-march=armv9-a+cssc+bf16+crypto"

    with tempfile.TemporaryDirectory() as tmpdir:
        asm_path = os.path.join(tmpdir, "test.s")
        obj_path = os.path.join(tmpdir, "test.o")

        # Wrap instruction in minimal valid ASM
        with open(asm_path, "w") as f:
            f.write(f"\t.text\n\t.global _start\n_start:\n\t{instruction}\n")

        cmd = [assembler] + flags.split() + ["-o", obj_path, asm_path]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return True, ""
        except subprocess.CalledProcessError as e:
            return False, e.stderr
