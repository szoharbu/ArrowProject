from Tool.memory_management.memory import Memory
from Tool.asm_blocks import AsmUnit
from Utils.configuration_management import Configuration
from Tool.state_management import get_state_manager

class GeneratedInstruction:
    def __init__(
            self,
            *,
            prefix:str=None,
            mnemonic: str,
            operands: list,
            comment: str,
    ):
        state_manager = get_state_manager()
        current_state = state_manager.get_active_state()

        self.prefix = prefix
        self.mnemonic = mnemonic
        self.operands = operands
        self.comment = comment

        for i, operand in enumerate(operands):
            if isinstance(operand, Memory):
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
                else: # x86 or riscv
                    operands[i] = hex(operand)

        self.asm_unit = AsmUnit(prefix=self.prefix, mnemonic=self.mnemonic, operands=self.operands, comment=self.comment)
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