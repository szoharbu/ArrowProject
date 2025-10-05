
import random
from Arrow.Tool.asm_libraries.label import Label
from Arrow.Tool.asm_libraries.end_test import end_test_asm_convention 
from Arrow.Arrow_API.resources.memory_manager import MemoryManager_API as MemoryManager
from Arrow.Tool.state_management import get_state_manager
from Arrow.Tool.asm_libraries.asm_logger import AsmLogger
from Arrow.Arrow_API.resources.register_manager import RegisterManager_API as RegisterManager
from Arrow.Utils.configuration_management import Configuration
from Arrow.Utils.configuration_management.enums import PrivilegeLevel
from Arrow.Utils.singleton_management import SingletonManager


def get_xpp_mask(current_privilege_level, target_privilege_level):
    """
    Returns the mask values for setting and clearing xPP bits in the status register
    based on the current and target privilege levels.
    """
    if current_privilege_level == PrivilegeLevel.RISCV.MACHINE:
        if target_privilege_level == PrivilegeLevel.RISCV.MACHINE:
            mpp_bits = 0b11
        elif target_privilege_level == PrivilegeLevel.RISCV.SUPERVISOR:
            mpp_bits = 0b01
        elif target_privilege_level == PrivilegeLevel.RISCV.USER:
            mpp_bits = 0b00
        else:
            raise ValueError(f"Unsupported target privilege level {target_privilege_level} for RISC-V mode switching.")
        set_mask = mpp_bits << 11
        mpp_mask = 0xFFFF_FFFF_FFFF_E7FF
        clear_mask = mpp_mask | set_mask
        return set_mask, clear_mask
    elif current_privilege_level == PrivilegeLevel.RISCV.SUPERVISOR:
        if target_privilege_level == PrivilegeLevel.RISCV.SUPERVISOR:
            spp_bit = 0b1
        elif target_privilege_level == PrivilegeLevel.RISCV.USER:
            spp_bit = 0b0
        else:
            raise ValueError(f"Unsupported target privilege level {target_privilege_level} for RISC-V mode switching.")
        set_mask = spp_bit << 8
        spp_mask = 0xFFFF_FFFF_FFFF_FEFF
        clear_mask = spp_mask | set_mask
        return set_mask, clear_mask
    else:
        raise ValueError(f"Unsupported current privilege level {current_privilege_level} for RISC-V mode switching.")

class PrivilegeManager:
    """
        Basic class to hold information about privelege management such as
         - label of the test body for the managed privilege mode
         - label of the trap handler for the managed privilege mode
         - label of the stack pointer save memory for each privilege mode
    """
    def __init__(self):
        self.managed_test_body_label = Label(f"managed_test_body_label")
        self.m_trap_handler_label = Label(f"m_trap_handler")
        self.s_trap_handler_label = Label(f"s_trap_handler")
        self.s_sp_save_mem = MemoryManager.Memory(byte_size=8, init_value=0)
        self.m_sp_save_mem = MemoryManager.Memory(byte_size=8, init_value=0)
        # Track if we've already generated the setup and handlers
        self.setup_generated = False
        self.m_handler_generated = False
        self.s_handler_generated = False

    def gen_privilege_setup(self):
        # Only generate setup once
        if self.setup_generated:
            return
        self.setup_generated = True
        AsmLogger.asm(f"{self.managed_test_body_label}:")
        mtvec_reg = RegisterManager.get(reg_type="gpr")
        dest_reg = RegisterManager.get(reg_type="gpr")
        AsmLogger.asm(f"la {mtvec_reg}, {self.m_trap_handler_label}")
        AsmLogger.asm(f"csrrw {dest_reg}, mtvec, {mtvec_reg}")
        stvec_reg = RegisterManager.get(reg_type="gpr")
        dest_reg = RegisterManager.get(reg_type="gpr")
        AsmLogger.asm(f"la {stvec_reg}, {self.s_trap_handler_label}")
        AsmLogger.asm(f"csrrw {dest_reg}, stvec, {stvec_reg}")

    def xret_to_scenario(self, scenario):
        scenario_label = scenario.get_label()
        state_manager = get_state_manager()
        current_state = state_manager.get_active_state()
        sp = Configuration.RiscvConfig.get_privileged_stack_pointer(current_state.privilege_level)
        return_label = Label(postfix=f"{scenario._name}_return")
        if Configuration.Architecture.riscv:
            if current_state.privilege_level == PrivilegeLevel.RISCV.MACHINE:
                xret_instruction = "mret"
                # TODO support sret from m mode
                epc = "mepc"
                status = "mstatus"
                sp_save_label = self.m_sp_save_mem.unique_label
            elif current_state.privilege_level == PrivilegeLevel.RISCV.SUPERVISOR:
                xret_instruction = "sret"
                epc = "sepc"
                status = "sstatus"
                sp_save_label = self.s_sp_save_mem.unique_label
            else:
                raise ValueError(f"Unsupported privilege level {current_state.privilege_level} for RISC-V mode switching.")
            save_regs = [reg for reg in RegisterManager.get_used_registers() if reg.name != sp.name]
            num_extra_stack_slots = 3  # +3 for status, previous stack pointer, return address
            AsmLogger.asm(f"addi {sp}, {sp}, -{8*(len(save_regs) + num_extra_stack_slots)}")
            for i in range(len(save_regs)):
                AsmLogger.asm(f"sd {save_regs[i]}, {8*(i + num_extra_stack_slots)}({sp})")

            # Now that we've saved the registers, we can use any register to store the return label, except the stack pointer
            x0_reg = RegisterManager.get(reg_name="x0")
            non_sp_regs = RegisterManager.get_used_registers(reg_type="gpr") + RegisterManager.get_free_registers(reg_type="gpr")
            non_sp_regs = [reg for reg in non_sp_regs if reg.name != sp.name and reg.name != "x0"]  # don't want to overwrite the stack pointer or use x0

            # save xstatus register and set the xPP privilege level
            status_reg = random.choice(non_sp_regs)
            mask_regs = [reg for reg in non_sp_regs if reg != status_reg]
            set_mask_reg = random.choice(mask_regs)
            clear_mask_reg = random.choice(mask_regs)
            dummy_reg = random.choice(non_sp_regs + [x0_reg])
            set_mask,clear_mask = get_xpp_mask(current_state.privilege_level, scenario.privilege_level)
            AsmLogger.asm(f"csrr {status_reg}, {status}")
            AsmLogger.asm(f"sd {status_reg}, 16({sp})")
            if set_mask != 0:
                AsmLogger.asm(f"li {set_mask_reg}, {set_mask}")
                AsmLogger.asm(f"or {status_reg}, {status_reg}, {set_mask_reg}")
            if clear_mask != 0xFFFF_FFFF_FFFF_FFFF:
                AsmLogger.asm(f"li {clear_mask_reg}, {clear_mask}")
                AsmLogger.asm(f"and {status_reg}, {status_reg}, {clear_mask_reg}")
            AsmLogger.asm(f"csrrw {dummy_reg}, {status}, {status_reg}")

            reg = random.choice(non_sp_regs)
            AsmLogger.asm(f"ld {reg}, {sp_save_label}")
            AsmLogger.asm(f"sd {reg}, 8({sp})", comment="save previous saved stack pointer to stack")
            reg = random.choice(non_sp_regs)
            AsmLogger.asm(f"sd {sp}, {sp_save_label}, {reg}", comment="save current stack pointer")

            reg = random.choice(non_sp_regs)
            AsmLogger.asm(f"la {reg}, {return_label}")
            AsmLogger.asm(f"sd {reg}, 0({sp})", comment="save return address")

            reg = RegisterManager.get_any(reg_type="gpr", exclude=["x0", sp.name])
            AsmLogger.asm(f"la {reg}, {scenario_label}")
            AsmLogger.asm(f"csrrw {RegisterManager.get_any(reg_type='gpr', exclude=[sp.name])}, {epc}, {reg}", comment=f"set the {xret_instruction} target address")

            if scenario.privilege_level < current_state.privilege_level:
                stack_mem = Configuration.RiscvConfig.get_stack_memory(scenario.privilege_level)
                AsmLogger.asm(f"la {Configuration.RiscvConfig.get_privileged_stack_pointer(scenario.privilege_level)}, {stack_mem.unique_label} + {stack_mem.byte_size - 8}", comment="Set the stack pointer for the target privilege level")

            # Do the xret
            AsmLogger.asm(f"{xret_instruction}")
            AsmLogger.asm(f"{return_label}:", comment="at this point ecall handler has already restored sp in order to jump to return_label")

            reg1 = random.choice(non_sp_regs)
            reg2 = random.choice([reg for reg in non_sp_regs if reg != reg1])
            AsmLogger.asm(f"ld {reg1}, 8({sp})")
            AsmLogger.asm(f"sd {reg1}, {sp_save_label}, {reg2}", comment="restore previous saved stack pointer")

            # 
            reg1 = random.choice(non_sp_regs)
            reg2 = random.choice(non_sp_regs + [x0_reg])
            AsmLogger.asm(f"ld {reg1}, 16({sp})")
            AsmLogger.asm(f"csrrw {reg2}, {status}, {reg1}", comment=f"restore {status} register")

            AsmLogger.comment("restore saved registers")
            for i in range(len(save_regs)):
                AsmLogger.asm(f"ld {save_regs[i]}, {8*(i + num_extra_stack_slots)}({sp})")
            AsmLogger.asm(f"addi {sp}, {sp}, {8*(len(save_regs) + num_extra_stack_slots)}")
        else:
            raise NotImplementedError("This test is currently only implemented for RISC-V architecture.")

    def gen_trap_handler(self, privilege_level):
        if privilege_level == PrivilegeLevel.RISCV.MACHINE:
            # Only generate M-mode handler once
            if self.m_handler_generated:
                return
            self.m_handler_generated = True
            handler_label = self.m_trap_handler_label
        elif privilege_level == PrivilegeLevel.RISCV.SUPERVISOR:
            # Only generate S-mode handler once
            if self.s_handler_generated:
                return
            self.s_handler_generated = True
            handler_label = self.s_trap_handler_label
        else:
            raise ValueError(f"Unsupported privilege level {privilege_level} for RISC-V trap handling.")

        AsmLogger.asm(f".align 2", comment="Align to 2^2=4-byte boundary")
        AsmLogger.asm(f"{handler_label}:")

        msp = Configuration.RiscvConfig.get_privileged_stack_pointer(PrivilegeLevel.RISCV.MACHINE)
        ssp = Configuration.RiscvConfig.get_privileged_stack_pointer(PrivilegeLevel.RISCV.SUPERVISOR)
        x0_reg = RegisterManager.get(reg_name="x0")
        available_regs = RegisterManager.get_used_registers(reg_type="gpr") + RegisterManager.get_free_registers(reg_type="gpr")
        # don't want to overwrite the stack pointer or ecall arg reg, and can't write to x0
        available_regs = [reg for reg in available_regs if reg.name not in [msp.name, ssp.name, Configuration.RiscvConfig.ecall_arg_reg.name, "x0"]]
        tmp_reg = random.choice(available_regs)

        # Helper function to randomly get x0 or tmp register
        get_tmp_or_x0_reg = lambda: random.choice([tmp_reg, x0_reg])

        if privilege_level == PrivilegeLevel.RISCV.MACHINE:
            AsmLogger.asm(f"csrrw {get_tmp_or_x0_reg()}, mscratch, {tmp_reg}", comment=f"Save temp register ({tmp_reg}) to mscratch")
        elif privilege_level == PrivilegeLevel.RISCV.SUPERVISOR:
            AsmLogger.asm(f"csrrw {get_tmp_or_x0_reg()}, sscratch, {tmp_reg}", comment=f"Save temp register ({tmp_reg}) to sscratch")
        else:
            raise ValueError(f"Unsupported privilege level {privilege_level} for RISC-V trap handling.")

        instruction_access_fault_cause = 0x1
        illegal_instruction_cause = 0x2
        breakpoint_cause = 0x3
        load_access_fault_cause = 0x5
        store_amo_access_fault_cause = 0x7
        ecall_u_cause = 0x8
        ecall_s_cause = 0x9
        ecall_m_cause = 0xb

        # labels
        check_cause = Label(postfix="check_cause")
        ret_same_priv = Label(postfix="ret_same_priv")
        ecall_handler = Label(postfix="ecall_handler")
        skip_handler = Label(postfix="skip_handler")
        instruction_fault_handler = Label(postfix="instruction_fault_handler")
        virtualize_s_trap = Label(postfix="virtualize_s_trap")

        if privilege_level == PrivilegeLevel.RISCV.MACHINE:
            AsmLogger.asm(f"csrr {tmp_reg}, mstatus", comment="mstatus.mpp is lower privilege")
            AsmLogger.asm(f"srli {tmp_reg}, {tmp_reg}, 11")
            AsmLogger.asm(f"andi {tmp_reg}, {tmp_reg}, 0x3")
            AsmLogger.asm(f"addi {tmp_reg}, {tmp_reg}, -3")
            AsmLogger.asm(f"beqz {tmp_reg}, {check_cause}", comment="If mstatus.mpp == machine, handle that normally")

            AsmLogger.asm(f"ld {tmp_reg}, {self.s_sp_save_mem.unique_label}")
            AsmLogger.asm(f"bnez {tmp_reg}, {virtualize_s_trap}", comment="Check if supervisor stack pointer save is not zero")
            AsmLogger.asm(f"li {tmp_reg}, {Configuration.RiscvConfig.ecall_arg_magic_val}", comment="Check if a0 contains magic value")
            AsmLogger.asm(f"beq {Configuration.RiscvConfig.ecall_arg_reg}, {tmp_reg}, {ret_same_priv}", comment="if not a magic value ecall, just return by skipping over the instruction")
            #AsmLogger.asm(f"ld {tmp_reg}, {self.s_sp_save_mem.unique_label}")
            #AsmLogger.asm(f"csrr {tmp_reg}, mcause", comment="see if it was an ecall_s")
            #AsmLogger.asm(f"addi {tmp_reg}, {tmp_reg}, {0 - ecall_s_cause}")
            #AsmLogger.asm(f"beqz {tmp_reg}, {ret_same_priv}", comment="ecall from S-mode where stack save is 0 and arg reg is magic value, that means scenario is done, return to M-mode code")

            AsmLogger.asm(f"{virtualize_s_trap}:", comment="virtualize the trap to S mode")
            #AsmLogger.asm(f"mv {ssp}, {tmp_reg}", comment="Set supervisor stack pointer")

            AsmLogger.asm(f"csrr {tmp_reg}, mepc")
            AsmLogger.asm(f"csrw sepc, {tmp_reg}", comment="Set sepc to mepc")

            AsmLogger.asm(f"csrr {tmp_reg}, mcause", comment="Read mcause to set scause and sstatus.spp")
            AsmLogger.asm(f"csrw scause, {tmp_reg}", comment="Set scause to ecall (from U/S-mode depending on mcause)")

            AsmLogger.asm(f"csrrw {get_tmp_or_x0_reg()}, stval, zero", comment="Set stval to 0")

            AsmLogger.asm(f"csrr {tmp_reg}, stvec")
            AsmLogger.asm(f"csrrw {get_tmp_or_x0_reg()}, mepc, {tmp_reg}", comment="Set mepc to stvec")

            AsmLogger.asm(f"li {tmp_reg}, 0x0800", comment="Set mstatus.mpp to supervisor mode = 01")
            AsmLogger.asm(f"csrrs {tmp_reg}, mstatus, {tmp_reg}", comment="Already know that high bit of MPP is 0, no need to clear")
            spp_bit_position = 8
            AsmLogger.asm(f"srli {tmp_reg}, {tmp_reg}, 11")
            AsmLogger.asm(f"andi {tmp_reg}, {tmp_reg}, 0x1")
            AsmLogger.asm(f"slli {tmp_reg}, {tmp_reg}, {spp_bit_position}")
            AsmLogger.asm(f"csrs sstatus, {tmp_reg}", comment="Set sstatus.spp depending on mstatus.mpp bit 0")
            AsmLogger.asm(f"seqz {tmp_reg}, {tmp_reg}")
            AsmLogger.asm(f"slli {tmp_reg}, {tmp_reg}, {spp_bit_position}")
            AsmLogger.asm(f"csrrc {get_tmp_or_x0_reg()}, sstatus, {tmp_reg}", comment="Clear sstatus.spp depending on mstatus.mpp bit 0")

            AsmLogger.asm(f"csrrw {tmp_reg}, mscratch, {get_tmp_or_x0_reg()}", comment="Restore temp register from mscratch")

            AsmLogger.asm(f"mret", comment="Return to supervisor mode")
        elif privilege_level == PrivilegeLevel.RISCV.SUPERVISOR:
            pass
        else:
            raise ValueError(f"Unsupported privilege level {privilege_level} for RISC-V trap handling.")

        # This last chunk of code is generic to M and S modes, need to genericize the stack pointer register
        AsmLogger.asm(f"{check_cause}:", comment="branch here to check cause and branch to appropriate handler")
        if privilege_level == PrivilegeLevel.RISCV.MACHINE:
            sp = msp
            sp_save_label = self.m_sp_save_mem.unique_label
            epc = "mepc"
            scratch = "mscratch"
            ret = "mret"
            AsmLogger.asm(f"csrr {tmp_reg}, mcause", comment="Check mcause")
            AsmLogger.asm(f"addi {tmp_reg}, {tmp_reg}, {0 - ecall_m_cause}")
            AsmLogger.asm(f"beqz {tmp_reg}, {ecall_handler}", comment="ecall from M-mode")
            AsmLogger.asm(f"addi {tmp_reg}, {tmp_reg}, {ecall_m_cause - breakpoint_cause}")
        elif privilege_level == PrivilegeLevel.RISCV.SUPERVISOR:
            sp = ssp
            sp_save_label = self.s_sp_save_mem.unique_label
            epc = "sepc"
            scratch = "sscratch"
            ret = "sret"
            AsmLogger.asm(f"csrr {tmp_reg}, scause", comment="Check scause")
            AsmLogger.asm(f"addi {tmp_reg}, {tmp_reg}, {0 - ecall_u_cause}")
            AsmLogger.asm(f"beqz {tmp_reg}, {ecall_handler}", comment="ecall from U-mode")
            AsmLogger.asm(f"addi {tmp_reg}, {tmp_reg}, {ecall_u_cause - ecall_s_cause}")
            AsmLogger.asm(f"beqz {tmp_reg}, {ecall_handler}", comment="ecall from S-mode")
            AsmLogger.asm(f"addi {tmp_reg}, {tmp_reg}, {ecall_s_cause - breakpoint_cause}")
        else:
            raise ValueError(f"Unsupported privilege level {privilege_level} for RISC-V trap handling.")

        AsmLogger.asm(f"beqz {tmp_reg}, {skip_handler}", comment="Handle breakpoint exception")
        AsmLogger.asm(f"addi {tmp_reg}, {tmp_reg}, {breakpoint_cause - illegal_instruction_cause}")
        AsmLogger.asm(f"beqz {tmp_reg}, {skip_handler}", comment="Handle illegal instruction exception")
        AsmLogger.asm(f"addi {tmp_reg}, {tmp_reg}, {illegal_instruction_cause - instruction_access_fault_cause}")
        AsmLogger.asm(f"beqz {tmp_reg}, {instruction_fault_handler}", comment="Handle instruction access fault")
        AsmLogger.asm(f"addi {tmp_reg}, {tmp_reg}, {instruction_access_fault_cause - load_access_fault_cause}")
        AsmLogger.asm(f"beqz {tmp_reg}, {skip_handler}", comment="Handle load access fault - skip instruction")
        AsmLogger.asm(f"addi {tmp_reg}, {tmp_reg}, {load_access_fault_cause - store_amo_access_fault_cause}")
        AsmLogger.asm(f"beqz {tmp_reg}, {skip_handler}", comment="Handle store/AMO access fault - skip instruction")
        # If we get here, it's an unexpected exception
        end_test_asm_convention(test_pass=False)

        # For things like breakpoint and illegal instruction exceptions, simply skip over the excepting instruction
        AsmLogger.asm(f"{skip_handler}:", comment="Handle breakpoint/illegal instruction - skip and continue")
        AsmLogger.asm(f"csrr {tmp_reg}, {epc}", comment="Read exception PC")
        AsmLogger.asm(f"addi {tmp_reg}, {tmp_reg}, 4", comment="Skip past faulting instruction (4 bytes)")
        AsmLogger.asm(f"csrw {epc}, {tmp_reg}", comment="Write back updated PC")
        AsmLogger.asm(f"csrrw {tmp_reg}, {scratch}, {RegisterManager.get_any()}", comment="Restore temp register from scratch")
        AsmLogger.asm(f"{ret}", comment="Return from exception")

        # Instruction access fault handler - uses ecall magic register pattern
        AsmLogger.asm(f"{instruction_fault_handler}:", comment="Handle instruction access fault using riscv-dv pattern")
        ecall_reg = Configuration.RiscvConfig.ecall_arg_reg
        AsmLogger.asm(f"beqz {ecall_reg}, {skip_handler}", comment="If ecall register is 0, fall back to skip instruction")
        AsmLogger.asm(f"csrrw {get_tmp_or_x0_reg()}, {epc}, {ecall_reg}", comment="Set EPC to return address from JALR")
        AsmLogger.asm(f"csrrw {tmp_reg}, {scratch}, {RegisterManager.get_any()}", comment="Restore temp register from scratch")
        AsmLogger.asm(f"{ret}", comment="Return from exception")

        AsmLogger.asm(f"{ecall_handler}:", comment="branch here to check if a0 is magic value")
        AsmLogger.asm(f"li {tmp_reg}, {Configuration.RiscvConfig.ecall_arg_magic_val}", comment="Check if a0 contains magic value")
        AsmLogger.asm(f"bne {Configuration.RiscvConfig.ecall_arg_reg}, {tmp_reg}, {skip_handler}", comment="if not a magic value ecall, just return by skipping over the instruction")

        AsmLogger.asm(f"{ret_same_priv}:", comment="branch here if restoring last same-privilege level (non-trap handler) execution state")
        AsmLogger.asm(f"ld {sp}, {sp_save_label}", comment="Restore stack pointer from sp save memory")
        AsmLogger.asm(f"ld {tmp_reg}, 0({sp})", comment="Pop saved PC from stack")
        AsmLogger.asm(f"jalr {get_tmp_or_x0_reg()}, {tmp_reg}, 0", comment="Jump to saved PC")

# Factory function to retrieve or create the PrivilegeManager instance
def get_privilege_manager():
    """
    Factory function to retrieve the PrivilegeManager instance.
    """

    privilege_manager_instance = SingletonManager.get("privilege_manager_instance", default=None)
    if privilege_manager_instance is None:
        privilege_manager_instance = PrivilegeManager()
        SingletonManager.set("privilege_manager_instance", privilege_manager_instance)
    return privilege_manager_instance
