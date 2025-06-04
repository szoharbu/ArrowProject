from Tool.asm_libraries.asm_logger import AsmLogger
from Tool.asm_libraries.label import Label
from Tool.state_management import get_current_state
from Tool.memory_management.memory_memory import Memory
from Tool.asm_libraries.barrier.barrier_manager import get_barrier_manager


def switch_EL(target_el_level:int):

    '''
    Higher → Lower: Always use ERET (exception return).
    Lower → Higher: Trigger an exception (e.g., interrupt, SVC, HVC).
    Direct Jumps (e.g., EL3 → EL0): Technically allowed via ERET, but not recommended (skip initialization steps in intermediate ELs).
    '''
    current_state = get_current_state()
    current_el_level = current_state.current_el_level
    current_segment_manager = current_state.segment_manager
    stack_address = current_segment_manager.get_stack_data_start_address()
    register_manager = current_state.register_manager

    print(f"zzzzzzzzzzz switch_EL {current_el_level} to {target_el_level}")

    while current_el_level != target_el_level:
        reg = register_manager.get_and_reserve(reg_type="gpr")
        reg2 = register_manager.get_and_reserve(reg_type="gpr")

        target_el_label = Label(postfix=f"el{target_el_level}_target_address")
        AsmLogger.comment(f"Transition from EL{current_el_level} to EL{target_el_level}")

        AsmLogger.comment(f"Set the target address in ELR_EL3")
        AsmLogger.asm(f"adr {reg}, {target_el_label}")
        AsmLogger.asm(f"msr ELR_EL3, {reg}", comment="set ELR_EL3 target address")

        AsmLogger.comment(f"Configure the processor state for EL{target_el_level}")
        AsmLogger.asm(f"mrs {reg}, SPSR_el3", comment="get SPSR_el3")
        AsmLogger.asm(f"bic {reg}, {reg}, #0xf", comment="clear mode bits")
        if target_el_level == 2: SPSR_value = 0x9   # EL2h (AArch64), DAIF=0000 (interrupts enabled)
        elif target_el_level == 1: SPSR_value = 0x5 # EL1h (AArch64), DAIF=0000 (interrupts enabled)
        else: SPSR_value = 0x0                      # EL0h (AArch64), DAIF=0000 (interrupts enabled)
        AsmLogger.asm(f"mov {reg2}, #{SPSR_value}") 
        AsmLogger.asm(f"orr {reg}, {reg}, {reg2}", comment="set EL2 mode")
        AsmLogger.asm(f"msr SPSR_el3, {reg}", comment="set SPSR_el3")

        AsmLogger.comment(f"Set the stack pointer in EL{target_el_level}")
        AsmLogger.asm(f"ldr {reg}, ={hex(stack_address)}")
        AsmLogger.asm(f"msr SP_EL{target_el_level}, {reg}", comment="set SP_EL{target_el_level} stack pointer")

        AsmLogger.comment(f"Switch to a non-secure state")
        AsmLogger.asm(f"mrs x0, scr_el3", comment="Read SCR_EL3")
        AsmLogger.asm(f"orr x0, x0, #(1 << 0)", comment="Set NS bit (bit 0)")
        AsmLogger.asm(f"msr scr_el3, x0", comment="Update SCR_EL3")
        

        AsmLogger.asm("eret")
        
        AsmLogger.asm(f"{target_el_label}:")



        return
        if current_el_level == 3:
            AR.comment("Transition from EL3 to EL2")

            AR.comment(f"Configure the processor state for EL2")
            AR.asm(f"mrs {reg}, SPSR_el3", comment="get SPSR_el3")
            AR.asm(f"bic {reg}, {reg}, #0xf", comment="clear mode bits")
            AR.asm(f"mov {reg2}, #0x9") # EL2h (AArch64), DAIF=0000 (interrupts enabled)
            AR.asm(f"orr {reg}, {reg}, {reg2}", comment="set EL2 mode")
            AR.asm(f"msr SPSR_el3, {reg}", comment="set SPSR_el3")

            AR.comment(f"Set the target address in EL2")
            AR.asm(f"adr {reg}, el2_return_address")
            AR.asm(f"msr ELR_EL3, {reg}", comment="set ELR_EL3 return address")

            AR.comment(f"Set the stack pointer in EL2")
            AR.asm(f"adr {reg}, _stack_start")
            AR.asm(f"msr SP_EL2, {reg}", comment="set SP_EL2 stack pointer")

            AR.comment(f"Switch to a non-secure state")
            AR.asm(f"mrs x0, scr_el3", comment="Read SCR_EL3")
            AR.asm(f"orr x0, x0, #(1 << 0)", comment="Set NS bit (bit 0)")
            AR.asm(f"msr scr_el3, x0", comment="Update SCR_EL3")
            

            AR.asm(f"eret")
            AR.asm("el2_return_address:")
            AR.asm("nop")
            current_el_level = 2
        elif current_el_level == 2:
            if target_el_level == 1:
                AR.comment("Transition from EL2 to EL1")
                AR.asm(f"ADR {reg}, el1_return_address")
                AR.asm(f"MSR ELR_EL2, {reg}")
                AR.asm(f"MSR SPSel, #1")
                AR.asm(f"ERET")
                AR.asm("el1_return_address:")
                current_el_level = 1
            else: 
                AR.comment("Transition from EL2 to EL3")
                current_el_level = 3
        elif current_el_level == 1:
            if target_el_level == 0:
                AR.comment("Transition from EL1 to EL0")
                AR.asm(f"ADR {reg}, el0_return_address")
                AR.asm(f"MSR ELR_EL1, {reg}")
                AR.asm(f"MSR SPSel, #0")
                AR.asm(f"ERET")
                AR.asm("el0_return_address:")
                current_el_level = 0
            else: 
                AR.comment("Transition from EL1 to EL2")
                current_el_level = 2
        else:
            AR.comment("Transition from EL0 to EL1")
            current_el_level = 1



# // At EL3
# // Transition from EL3 to EL2
# MSR ELR_EL3, el2_return_address  // Set return address for EL2
# MSR SPSel, #1                    // Select SP_EL2
# ERET                             // Return to EL2

# // At EL2
# el2_return_address:
# MSR ELR_EL2, el1_return_address  // Set return address for EL1
# MSR SPSel, #1                    // Select SP_EL1
# ERET                             // Return to EL1

# // At EL1
# el1_return_address:
# MSR ELR_EL1, el0_return_address  // Set return address for EL0
# MSR SPSel, #0                    // Select SP_EL0
# ERET                             // Return to EL0

# // At EL0
# el0_return_address:
# MOV X0, X0                       // No-op instruction to indicate we are at EL0

