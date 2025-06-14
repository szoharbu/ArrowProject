from Tool.asm_libraries.asm_logger import AsmLogger
from Tool.asm_libraries.label import Label
from Tool.state_management import get_current_state
from Tool.memory_management.memory_operand import Memory
from Tool.asm_libraries.barrier.barrier_manager import get_barrier_manager
from Utils.APIs import choice
from Utils.configuration_management import Configuration
from Tool.state_management.switch_state import switch_code

def switch_EL_to_higher(target_el_level: int):
    """
    Switch from lower EL to higher EL (e.g., EL1 → EL3)
    Uses SMC instruction to trigger exception handled at EL3
    """
    current_state = get_current_state()
    current_el_level = current_state.current_el_level
    
    if current_el_level >= target_el_level:
        raise ValueError(f"Cannot switch from EL{current_el_level} to EL{target_el_level} - use switch_EL_to_lower instead")
    
    if target_el_level != 3:
        raise ValueError(f"Can only switch to EL3 from lower levels, not EL{target_el_level}")
    

    el3_page_table = [pt for pt in current_state.enabled_page_tables if pt.execution_context == Configuration.Execution_context.EL3][0]
    available_blocks = el3_page_table.segment_manager.get_segments(pool_type=Configuration.Memory_types.CODE)
    selected_target_block = choice.choice(values=available_blocks)

    register_manager = current_state.register_manager
    reg = register_manager.get_and_reserve(reg_type="gpr")
    
    AsmLogger.comment(f"Transition from EL{current_el_level} to EL{target_el_level} using SMC")
    
    # Set up parameters for the SMC call (function ID, etc.)
    # You might want to pass specific values to identify the call
    AsmLogger.asm(f"mov {reg}, #0x0", comment="SMC function ID (customize as needed)")
    AsmLogger.asm(f"smc #0", comment="Secure Monitor Call - triggers exception to EL3")
    
    current_state.current_code_block = selected_target_block
    current_state.current_el_level = target_el_level
    current_state.execution_context = Configuration.Execution_context.EL3
    current_state.current_el_page_table = el3_page_table

    # Note: Code after SMC will not execute immediately
    # Execution continues in EL3 exception handler, then returns here
    AsmLogger.comment("Execution continues here after EL3 handler returns")

def switch_EL_to_lower(target_el_level: int):
    """
    Switch from higher EL to lower EL (e.g., EL3 → EL1)
    Uses ERET instruction - this is the existing logic
    """
    current_state = get_current_state()
    current_el_level = current_state.current_el_level
    current_el_page_table = current_state.current_el_page_table
    current_segment_manager = current_el_page_table.segment_manager

    if current_el_level <= target_el_level:
        raise ValueError(f"Cannot switch from EL{current_el_level} to EL{target_el_level} - use switch_EL_to_higher instead")

    register_manager = current_state.register_manager

    stack_address = current_segment_manager.get_stack_data_start_address()

    el1_page_table = [pt for pt in current_state.enabled_page_tables if pt.execution_context == Configuration.Execution_context.EL1_NS][0]
    available_blocks = el1_page_table.segment_manager.get_segments(pool_type=Configuration.Memory_types.CODE)
    selected_target_block = choice.choice(values=available_blocks)

    reg = register_manager.get_and_reserve(reg_type="gpr")
    reg2 = register_manager.get_and_reserve(reg_type="gpr")

    target_el_label = Label(postfix=f"el{target_el_level}_target_address")
    AsmLogger.comment(f"Transition from EL{current_el_level} to EL{target_el_level}")

    AsmLogger.comment(f"Set the target address in ELR_EL3")
    AsmLogger.asm(f"ldr {reg}, ={target_el_label}")
    AsmLogger.asm(f"msr ELR_EL3, {reg}", comment="set ELR_EL3 target address")

    AsmLogger.comment(f"Configure the processor state for EL{target_el_level}")
    AsmLogger.asm(f"mrs {reg}, SPSR_el3", comment="get SPSR_el3")
    AsmLogger.asm(f"bic {reg}, {reg}, #0xf", comment="clear mode bits")
    if target_el_level == 2: 
        SPSR_value = 0x9   # EL2h (AArch64), DAIF=0000 (interrupts enabled)
    elif target_el_level == 1: 
        SPSR_value = 0x5   # EL1h (AArch64), DAIF=0000 (interrupts enabled)
    else: 
        SPSR_value = 0x0   # EL0h (AArch64), DAIF=0000 (interrupts enabled)
    AsmLogger.asm(f"mov {reg2}, #{SPSR_value}") 
    AsmLogger.asm(f"orr {reg}, {reg}, {reg2}", comment=f"set EL{target_el_level} mode")
    AsmLogger.asm(f"msr SPSR_el3, {reg}", comment="set SPSR_el3")

    AsmLogger.comment(f"Set the stack pointer in EL{target_el_level}")
    AsmLogger.asm(f"ldr {reg}, ={hex(stack_address)}")
    AsmLogger.asm(f"msr SP_EL{target_el_level}, {reg}", comment=f"set SP_EL{target_el_level} stack pointer")

    AsmLogger.comment(f"Configure SCR_EL3 for transition to EL{target_el_level}")
    AsmLogger.asm(f"mrs {reg}, scr_el3", comment="Read SCR_EL3")
    AsmLogger.asm(f"orr {reg}, {reg}, #(1 << 0)", comment="Set NS bit (bit 0) - Non-secure state")
    
    if target_el_level == 1:
        AsmLogger.asm(f"orr {reg}, {reg}, #(1 << 8)", comment="Set HCE bit (bit 8) - HVC instruction enable")
        AsmLogger.comment("EL2 is bypassed for direct EL3→EL1 transition")
    
    AsmLogger.asm(f"msr scr_el3, {reg}", comment="Update SCR_EL3")
    AsmLogger.asm(f"isb")
    AsmLogger.comment(f"Execute transition to EL{target_el_level}")
    AsmLogger.asm("eret")
    
    current_state.current_code_block = selected_target_block
    current_state.current_el_level = target_el_level
    current_state.execution_context = Configuration.Execution_context.EL1_NS
    current_state.current_el_page_table = el1_page_table

    AsmLogger.asm(f"{target_el_label}:")
    AsmLogger.comment(f"Now running at EL{target_el_level}")


def switch_EL(target_el_level:int):
    '''
    Unified function to switch between Exception Levels
    Higher → Lower: Always use ERET (exception return).
    Lower → Higher: Trigger an exception (e.g., SMC for EL3).
    '''
    current_state = get_current_state()
    current_el_level = current_state.current_el_level

    if current_el_level == target_el_level:
        print(f"zzzzzzzzzzz switch_EL {current_el_level} to {target_el_level} - already at target EL")
        return  # Already at target EL
    
    AsmLogger.comment(f"Switch_EL:: Switching from EL{current_el_level} to EL{target_el_level}")
    if current_el_level < target_el_level:
        # Going from lower to higher EL
        switch_EL_to_higher(target_el_level)
    else:
        # Going from higher to lower EL  
        switch_EL_to_lower(target_el_level)

