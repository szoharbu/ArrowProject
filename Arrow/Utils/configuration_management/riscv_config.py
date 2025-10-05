
from collections import defaultdict
import random
from Arrow.Tool.register_management.register_manager import RegisterManager
from Arrow.Utils.configuration_management.enums import PrivilegeLevel
from Arrow.Utils.configuration_management.knob_manager import Knob

class RiscvConfig:
    """Configuration class for RISC-V architecture."""
    isa = Knob(name='isa', value_func='rv64g', read_only=True, dynamic=False, global_knob=False, description="Specify the supported architecture (with extensions)")
    
    def __init__(self):
        registers = [reg for reg in RegisterManager.get_riscv_registers() if reg.type == "gpr" and reg.name != "x0"]
        #self.m_stack_pointer = random.choice(registers)
        #self.s_stack_pointer = random.choice(registers)
        # TODO dynamic stack pointer register
        # note sp is reserved for each state in test_boot.py
        sp = [reg for reg in registers if reg.name == 'sp'][0]
        self.stack_pointers = defaultdict(lambda: sp)
        self.ecall_arg_reg = random.choice(registers)
        self.ecall_arg_magic_val = "0xdeadacedbeefface"
        self.stack_memory_per_privilege = defaultdict(lambda: None)

    def get_privileged_stack_pointer(self, privilege_level):
        """Get the stack pointer for a specific privilege level."""
        return self.stack_pointers[privilege_level]
    
    def register_stack_memory(self, privilege_level, mem):
        """Register stack memory for a specific privilege level."""
        self.stack_memory_per_privilege[privilege_level] = mem

    def get_stack_memory(self, privilege_level):
        return self.stack_memory_per_privilege[privilege_level]
