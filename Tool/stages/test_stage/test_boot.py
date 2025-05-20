from Utils.logger_management import get_logger
from Utils.configuration_management import Configuration, get_config_manager
from Tool.state_management import get_state_manager
from Tool.state_management.switch_state import switch_code
from Tool.asm_libraries.asm_logger import AsmLogger
from Tool.asm_libraries.branch_to_segment import branch_to_segment
#from Tool.generation_management.generate import generate

from Utils.APIs import choice


def do_boot():
    logger = get_logger()
    state_manager = get_state_manager()
    config_manager = get_config_manager()

    logger.info("============ do_boot")

    # TODO:: refactor this logic!!!!

    state_manager.set_active_state("core_0")
    curr_state = state_manager.get_active_state()

    # Allocate BSP boot block. a single block that act as trampoline for all cores    
    bsp_boot_blocks = curr_state.memory_manager.get_segments(pool_type=Configuration.Memory_types.BSP_BOOT_CODE)
    if len(bsp_boot_blocks) != 1:
        raise ValueError(
            "bsp_boot_block must contain exactly one element, but it contains: {}".format(len(bsp_boot_blocks)))
    bsp_boot_block = bsp_boot_blocks[0]

    switch_code(bsp_boot_block)
    AsmLogger.comment(f"========================= BSP BOOT CODE - start =====================")
    logger.debug(f"BODY:: Running BSP boot code")
    # all threads will pass through this BSP boot code, and will jump from here to thier indevidual boot segment

    register_manager = curr_state.register_manager
    tmp_reg1 = register_manager.get_and_reserve(reg_type="gpr")
    # # Load vector table
    # AsmLogger.comment("Load vector table")
    # AsmLogger.asm(f"ldr {tmp_reg1}, =vector_table_base")
    # AsmLogger.asm(f"msr vbar_el3, {tmp_reg1}")
    # AsmLogger.asm(f"msr vbar_el2, {tmp_reg1}")
    # AsmLogger.asm(f"msr vbar_el1, {tmp_reg1}")

    # Load the stack pointer
    sp_reg = register_manager.get(reg_name="sp")
    register_manager.reserve(sp_reg)
    stack_data_start_address = curr_state.memory_manager.get_stack_data_start_address()

    AsmLogger.comment(f"Load the stack pointer (address of {stack_data_start_address})")
    #AsmLogger.asm(f"ldr {tmp_reg1}, =_stack_top")
    AsmLogger.asm(f"ldr {tmp_reg1}, ={hex(stack_data_start_address)}")
    #AsmLogger.asm(f"ldr {tmp_reg1}, {hex(stack_data_start_address)}")
    # AsmLogger.asm(f"adrp {tmp_reg1}, {hex(stack_data_start_address)}", comment="read value of LABEL_TTBR0_EL3 from memory") 
    # AsmLogger.asm(f"add {tmp_reg1}, {tmp_reg1}, :lo12:{hex(stack_data_start_address)}", comment="add low 12 bits of LABEL_TTBR0_EL3") 
    # AsmLogger.asm(f"ldr x0, [x0]", comment="load the value of LABEL_TTBR0_EL3")    

    AsmLogger.asm(f"mov {sp_reg}, {tmp_reg1}")
    register_manager.free(sp_reg)

    # Configure CPU
    # AsmLogger.comment("cpu_if_cfg")
    # AsmLogger.asm("bl      cpu_if_cfg")
    # AsmLogger.comment("isb")
    # AsmLogger.asm("isb")
    # AsmLogger.comment("core_interrupt_en")
    # AsmLogger.asm("bl      core_interrupt_en")
    # AsmLogger.comment("Jump to the test")
    # AsmLogger.asm("b       test")

    # switch according to thread
    tmp_reg2 = register_manager.get_and_reserve(reg_type="gpr")
    AsmLogger.comment("switch according to thread")
    AsmLogger.asm(f"mrs {tmp_reg1}, mpidr_el1")
    AsmLogger.asm(f"ubfx {tmp_reg2}, {tmp_reg1}, #0, #1    //thread_id")

    curr_state = state_manager.get_active_state()

    for state in state_manager.states_dict:

        # TODO:: this is a hack, need to fix this and allow ability to get state without switching to it!!!
        state_manager.set_active_state(state)
        tmp_state = state_manager.get_active_state()
        boot_blocks = tmp_state.memory_manager.get_segments(pool_type=Configuration.Memory_types.BOOT_CODE)
        if len(boot_blocks) != 1:
            raise ValueError(
                "boot_blocks must contain exactly one element, but it contains: {}".format(len(boot_blocks)))
        boot_block = boot_blocks[0]
        boot_code_start_label = boot_block.code_label
        state_manager.set_active_state(curr_state.state_name)

        AsmLogger.asm(f"cmp {tmp_reg2}, #{tmp_state.state_id}")
        AsmLogger.asm(f"beq {boot_code_start_label}")

    register_manager.free(tmp_reg1)
    register_manager.free(tmp_reg2)

    # # setting back to boot code for the print, later return to selected block
    # switch_code(bsp_boot_block)
    # AsmLogger.comment(f"========================= BSP BOOT CODE - end =====================")
    # switch_code(boot_block)

    for state in state_manager.states_dict:
        state_manager.set_active_state(state)
        curr_state = state_manager.get_active_state()

        boot_blocks = curr_state.memory_manager.get_segments(pool_type=Configuration.Memory_types.BOOT_CODE)
        if len(boot_blocks) != 1:
            raise ValueError(
                "boot_blocks must contain exactly one element, but it contains: {}".format(len(boot_blocks)))
        boot_block = boot_blocks[0]

        switch_code(boot_block)  # switching from a None code block into boot

        logger.debug(f"BODY:: Running boot code")
        AsmLogger.comment(f"========================= {curr_state.state_name.upper()} BOOT CODE - start =====================")

        execution_platform = config_manager.get_value('Execution_platform')
        if execution_platform == "baremetal":
            AsmLogger.comment(
                f"-- memory range address is {hex(curr_state.memory_range.address)} with size of {hex(curr_state.memory_range.byte_size)}")
            AsmLogger.comment(
                f"-- setting base_register {curr_state.base_register} to address of {hex(curr_state.base_register_value)}")
            # AsmLogger.store_value_into_register(register=current_state.base_register, value=current_state.base_register_value)

        skip_boot = Configuration.Knobs.Config.skip_boot
        if not skip_boot:
            AsmLogger.asm("nop", comment=f"Empty boot code of {curr_state.state_name} at the moment, skipping")
            enable_pgt_page_table()
            #generate(instruction_count=10)

        # selecting random block to jump to for test body
        available_blocks = curr_state.memory_manager.get_segments(pool_type=Configuration.Memory_types.CODE)
        selected_block = choice.choice(values=available_blocks)
        branch_to_segment.BranchToSegment(selected_block).one_way_branch()

        # setting back to boot code for the print, later return to selected block
        switch_code(boot_block)
        AsmLogger.comment(f"========================= {curr_state.state_name.upper()} BOOT CODE - end =====================")
        switch_code(selected_block)

    # Create a new list with blocks in the desired order
    all_code_blocks = []
    all_code_blocks.extend(bsp_boot_blocks)  # BSP boot code first
    all_code_blocks.extend(boot_blocks)  # Then boot code
    all_code_blocks.extend(available_blocks)  # Finally regular code blocks


def enable_pgt_page_table():
    AsmLogger.comment("First disable the MMU")
    AsmLogger.asm(f"mrs x0, sctlr_el3")
    AsmLogger.asm(f"bic x0, x0, #1", comment="Clear bit 0 (MMU enable)")
    AsmLogger.asm(f"msr sctlr_el3, x0")
    AsmLogger.asm(f"isb")
    AsmLogger.asm(f"dsb sy")
    

    AsmLogger.comment("Load translation table base register with the address of our L0 table")
    #AsmLogger.asm(f"ldr x0, =0x0000000090200000", comment="Use actual value from LABEL_TTBR0_EL3")
    #AsmLogger.asm(f"ldr x0, =LABEL_TTBR0_EL3", comment="Use actual value from LABEL_TTBR0_EL3")
    AsmLogger.asm(f"adrp x0, LABEL_TTBR0_EL3", comment="read value of LABEL_TTBR0_EL3 from memory") 
    AsmLogger.asm(f"add x0, x0, :lo12:LABEL_TTBR0_EL3", comment="add low 12 bits of LABEL_TTBR0_EL3") 
    AsmLogger.asm(f"ldr x0, [x0]", comment="load the value of LABEL_TTBR0_EL3")    
    AsmLogger.asm(f"msr ttbr0_el3, x0")
    AsmLogger.asm(f"isb")
    AsmLogger.asm(f"dsb sy")

    AsmLogger.comment("Set up TCR_EL3 (Translation Control Register)")
    #AsmLogger.asm(f"ldr x0, =0x0000000080853510", comment="Use actual value from LABEL_TCR_EL3") 
    #AsmLogger.asm(f"ldr x0, =LABEL_TCR_EL3", comment="Use actual value from LABEL_TCR_EL3") 
    AsmLogger.asm(f"adrp x0, LABEL_TCR_EL3", comment="read value of LABEL_TCR_EL3 from memory") 
    AsmLogger.asm(f"add x0, x0, :lo12:LABEL_TCR_EL3", comment="add low 12 bits of LABEL_TCR_EL3") 
    AsmLogger.asm(f"ldr x0, [x0]", comment="load the value of LABEL_TCR_EL3")    
    AsmLogger.asm(f"msr tcr_el3, x0")
    AsmLogger.asm(f"isb")
    AsmLogger.asm(f"dsb sy")

    AsmLogger.comment("Set up MAIR_EL1 (Memory Attribute Indirection Register)")
    #AsmLogger.asm(f"ldr x0, =0x0000000000FF44FF", comment="Use actual value from LABEL_MAIR_EL3")
    #AsmLogger.asm(f"ldr x0, =LABEL_MAIR_EL3", comment="Use actual value from LABEL_MAIR_EL3")
    AsmLogger.asm(f"adrp x0, LABEL_MAIR_EL3", comment="read value of LABEL_MAIR_EL3 from memory") 
    AsmLogger.asm(f"add x0, x0, :lo12:LABEL_MAIR_EL3", comment="add low 12 bits of LABEL_MAIR_EL3") 
    AsmLogger.asm(f"ldr x0, [x0]", comment="load the value of LABEL_MAIR_EL3")    
    AsmLogger.asm(f"msr mair_el3, x0")
    AsmLogger.asm(f"isb")
    AsmLogger.asm(f"dsb sy")

    # TODO:: remove after testing
    # TODO:: remove after testing
    AsmLogger.asm(f"mrs x0, scr_el3")
    AsmLogger.asm(f"bic x0, x0, #(1 << 9)", comment="Clear bit 9 (SCR_EL3.SIF)")
    AsmLogger.asm(f"dsb sy")
    AsmLogger.asm(f"msr scr_el3, x0")
    AsmLogger.asm(f"isb")
    AsmLogger.asm(f"dsb sy")
    AsmLogger.asm(f"mrs x0, scr_el3")
    # TODO:: remove after testing
    # TODO:: remove after testing


    AsmLogger.comment("Enable MMU")
    AsmLogger.asm(f"mrs x0, sctlr_el3")
    AsmLogger.asm(f"orr x0, x0, #1", comment="Set bit 0 (MMU enable)")
    AsmLogger.asm(f"bic x0, x0, #(1 << 20)", comment="Clear bit 20 (WXN)")
    AsmLogger.asm(f"msr sctlr_el3, x0")
    AsmLogger.asm(f"isb")
    AsmLogger.asm(f"dsb sy")


    # AsmLogger.asm(f"// Jump to virtual address")
    # AsmLogger.asm(f"ldr x0, =0xc0000000")
    # AsmLogger.asm(f"br x0")
    
    AsmLogger.comment("Now the MMU is enabled with your page tables")
    AsmLogger.comment("Code can now access virtual addresses defined in your page tables")
