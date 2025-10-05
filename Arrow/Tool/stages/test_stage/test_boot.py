from Arrow.Utils.logger_management import get_logger
from Arrow.Utils.configuration_management import Configuration, get_config_manager
from Arrow.Tool.state_management import get_state_manager, get_current_state
from Arrow.Tool.state_management.switch_state import switch_code
#from Arrow.Tool.memory_management.memory_space_manager import get_mmu_manager
from Arrow.Tool.asm_libraries.asm_logger import AsmLogger
from Arrow.Tool.asm_libraries.branch_to_segment import branch_to_segment
from Arrow.Tool.asm_libraries.label import Label
from Arrow.Tool.asm_libraries.barrier.barrier import Barrier
from Arrow.Tool.exception_management import get_exception_manager
#from Arrow.Tool.generation_management.generate import generate

from Arrow.Arrow_API.resources.memory_manager import MemoryManager_API as MemoryManager
from Arrow.Arrow_API.resources.register_manager import RegisterManager_API as RegisterManager
from Arrow.Arrow_API import AR
from Arrow.Utils.configuration_management.enums import PrivilegeLevel
from Arrow.Utils.APIs import choice


def do_boot():
    logger = get_logger()
    state_manager = get_state_manager()
    config_manager = get_config_manager()

    logger.info("============ do_boot")

    # TODO:: refactor this logic!!!!

    if Configuration.Architecture.arm:
        # bsp_code is the code that will be executed by all cores, and will jump to the boot code of the core
        bsp_boot_blocks = do_bsp_boot()

        end_boot_barrier_label = Label("end_boot_barrier")

    for state in state_manager.states_dict:
        curr_state = state_manager.set_active_state(state)
        segment_manager = curr_state.get_segment_manager()

        stack_block = MemoryManager.MemoryBlock(name="stack_block", byte_size=4*1024, _is_stack=True)
        boot_blocks = segment_manager.get_segments(pool_type=Configuration.Memory_types.BOOT_CODE)
        if len(boot_blocks) != 1:
            raise ValueError(
                "boot_blocks must contain exactly one element, but it contains: {}".format(len(boot_blocks)))
        boot_block = boot_blocks[0]

        switch_code(boot_block)  # switching from a None code block into boot

        logger.debug(f"BODY:: Running boot code")
        AsmLogger.comment(f"========================= {curr_state.state_name.upper()} BOOT CODE - start =====================")

        if Configuration.Architecture.x86:
            execution_platform = config_manager.get_value('Execution_platform')
            if execution_platform == "baremetal": 
                AsmLogger.comment(
                    f"-- memory range address is {hex(curr_state.memory_range.address)} with size of {hex(curr_state.memory_range.byte_size)}")
                AsmLogger.comment(
                    f"-- setting base_register {curr_state.base_register} to address of {hex(curr_state.base_register_value)}")
                # AsmLogger.store_value_into_register(register=current_state.base_register, value=current_state.base_register_value)

        skip_boot = Configuration.Knobs.Config.skip_boot
        if not skip_boot:
            if Configuration.Architecture.arm:
                enable_arm_page_tables()
                enable_arm_exception_tables()
                set_arm_init_system_registers()
                set_arm_privilege_level()
                #generate(instruction_count=10)
                logger.debug("============ Boot end barrier")
                Barrier(end_boot_barrier_label)


        AsmLogger.comment(f"Stack segment generated at {stack_block.get_address()} with size {stack_block.byte_size}")

        if Configuration.Architecture.x86:
            AsmLogger.comment(f"TODO: stack initialization for x86")
        elif Configuration.Architecture.riscv:
            # TODO pick random stack pointer register instead of ABI sp
            sp = RegisterManager.get(reg_name='sp')
            sp.set_reserve()
            #stack_mem = MemoryManager.Memory(name='stack_memory', memory_block=stack_block, byte_size=stack_block.byte_size, memory_block_offset=0)
            Configuration.RiscvConfig.register_stack_memory(curr_state.privilege_level, stack_block)
            if curr_state.privilege_level == PrivilegeLevel.RISCV.MACHINE:
                AsmLogger.asm(f"la sp, {stack_block.unique_label} + {stack_block.byte_size - 8}", comment="Load the value of the stack")
                tmp_reg = RegisterManager.get()
                
                # Set up PMP hole for access fault testing using NAPOT mode
                # NAPOT is better for creating a specific hole without affecting other memory
                pmp_hole_base = 0x80000000
                pmp_hole_size = 0x1000  # 4KB hole
                # For NAPOT: address = base | (size-1) >> 1, then >> 2 for PMP format
                napot_addr = pmp_hole_base | ((pmp_hole_size - 1) >> 1)
                AsmLogger.asm(f"li {tmp_reg}, 0x{napot_addr:08x}", comment="PMP hole NAPOT address")
                AsmLogger.asm(f"srli {tmp_reg}, {tmp_reg}, 2", comment="Convert to PMP address format (>>2)")
                AsmLogger.asm(f"csrw pmpaddr0, {tmp_reg}", comment="Set pmpaddr0 for access fault hole")
                
                # Configure PMP entry 0: NAPOT mode, locked, no permissions (R=W=X=0)
                pmp_hole_cfg = 0x80 | (3 << 3)  # L=1 (locked), A=3 (NAPOT), R=W=X=0 (no access)
                AsmLogger.asm(f"li {tmp_reg}, {pmp_hole_cfg}", comment="PMP hole config: NAPOT, locked, no RWX")
                AsmLogger.asm(f"csrw pmpcfg0, {tmp_reg}", comment="Create PMP hole for access faults")
                
                # Initialize PMP15 for general protection (existing code)
                AsmLogger.asm(f"li {tmp_reg}, 0x3fffffffffff", comment="Initialize PMP15")
                AsmLogger.asm(f"csrw pmpaddr15, {tmp_reg}")
                AsmLogger.asm(f"li {tmp_reg}, 0x1f00000000000000")
                AsmLogger.asm(f"csrw pmpcfg2, {tmp_reg}")
                AsmLogger.asm(f"sfence.vma x0, x0")

        elif Configuration.Architecture.arm:
            AsmLogger.comment(f"TODO: stack initialization for ARM")
        else:
            raise ValueError(f"Unsupported architecture")

        # selecting random block to jump to for test body
        # requesting current_page again, as the set_privilege_level might have changed it
        curr_state = state_manager.get_active_state()
        segment_manager = curr_state.get_segment_manager()
        available_blocks = segment_manager.get_segments(pool_type=Configuration.Memory_types.CODE, non_exclusive_only=True)
        selected_block = choice.choice(values=available_blocks)
        branch_to_segment.BranchToSegment(selected_block).one_way_branch()

        # setting back to boot code for the print, later return to selected block

        curr_state.current_code_block = boot_block
        AsmLogger.comment(f"========================= {curr_state.state_name.upper()} BOOT CODE - end =====================")
        curr_state.current_code_block = selected_block
        switch_code(selected_block)

    # # Create a new list with blocks in the desired order
    # all_code_blocks = []
    # all_code_blocks.extend(bsp_boot_blocks)  # BSP boot code first
    # all_code_blocks.extend(boot_blocks)  # Then boot code
    # all_code_blocks.extend(available_blocks)  # Finally regular code blocks


def set_arm_init_system_registers():

    AsmLogger.comment("Setting initial system registers")
    from Arrow.Tool.asm_libraries.sysreg import SysReg

    # in order to enable FIQ, we need to clear the DAIF bits, and set the SCR_EL3 to 0x6
    SysReg.write(register=Configuration.SystemRegister.DAIF, value=0x0)
    SysReg.write(register=Configuration.SystemRegister.SCR_EL3, value=0x6)

    # Set CPACR_EL1.FPEN to 3 (no trapping of FP/SIMD)
    SysReg.write_field(Configuration.SystemRegisterBitField.CPACR_EL1_FPEN, value=3)


def set_arm_privilege_level():
    logger = get_logger()
    if Configuration.Architecture.arm:
        exception_level = Configuration.Knobs.Config.exception_level.get_value()
        current_state = get_current_state()
        current_el_level = current_state.current_el_level
        if current_el_level != 3:
            raise ValueError(f"Current EL level is {current_el_level}, but expected to be 3")
        if exception_level != 3:
            from Arrow.Tool.asm_libraries.switch_el import switch_EL
            logger.info(f"================ Switching to EL{exception_level}")
            switch_EL(target_el_level=exception_level)
    else:
        privilege_level = Configuration.Knobs.Config.privilege_level.get_value()
        logger.warning(f"Setting privilege level to {privilege_level} is currently not supported for {Configuration.Architecture} architecture")


def enable_arm_page_tables():
    # TODO:: refactor this !!! 
    enable_EL3_page_table()
    enable_EL1_page_table()

def enable_EL3_page_table():
    curr_state = get_current_state()
    register_manager = curr_state.register_manager
    tmp_reg = register_manager.get_and_reserve(reg_type="gpr")
    AsmLogger.comment("First disable the MMU")
    AsmLogger.asm(f"mrs {tmp_reg}, sctlr_el3")
    AsmLogger.asm(f"bic {tmp_reg}, {tmp_reg}, #1", comment="Clear bit 0 (MMU enable)")
    AsmLogger.asm(f"msr sctlr_el3, {tmp_reg}") 

    AsmLogger.comment("Load translation table base register with the address of our L0 table")
    AsmLogger.asm(f"ldr {tmp_reg}, =LABEL_TTBR0_EL3_{curr_state.state_name}", comment="read value of LABEL_TTBR0_EL3 from memory")
    AsmLogger.asm(f"ldr {tmp_reg}, [{tmp_reg}]", comment="load the value of LABEL_TTBR0_EL3")    
    AsmLogger.asm(f"msr ttbr0_el3, {tmp_reg}")

    AsmLogger.comment("Set up TCR_EL3 (Translation Control Register)")
    AsmLogger.asm(f"ldr {tmp_reg}, =LABEL_TCR_EL3_{curr_state.state_name}", comment="read value of LABEL_TCR_EL3 from memory") 
    AsmLogger.asm(f"ldr {tmp_reg}, [{tmp_reg}]", comment="load the value of LABEL_TCR_EL3")    
    AsmLogger.asm(f"msr tcr_el3, {tmp_reg}")

    AsmLogger.comment("Set up MAIR_EL1 (Memory Attribute Indirection Register)")
    AsmLogger.asm(f"ldr {tmp_reg}, =LABEL_MAIR_EL3_{curr_state.state_name}", comment="read value of LABEL_MAIR_EL3 from memory")
    AsmLogger.asm(f"ldr {tmp_reg}, [{tmp_reg}]", comment="load the value of LABEL_MAIR_EL3")    
    AsmLogger.asm(f"msr mair_el3, {tmp_reg}")

    AsmLogger.comment("Enable MMU")
    AsmLogger.asm(f"mrs {tmp_reg}, sctlr_el3")
    AsmLogger.asm(f"orr {tmp_reg}, {tmp_reg}, #1", comment="Set bit 0 (MMU enable)")
    AsmLogger.asm(f"orr {tmp_reg}, {tmp_reg}, #(1 << 2)", comment="Set bit 2 (Data cache enable)")
    AsmLogger.asm(f"bic {tmp_reg}, {tmp_reg}, #(1 << 20)", comment="Clear bit 20 (WXN)")
    AsmLogger.asm(f"msr sctlr_el3, {tmp_reg}")
    AsmLogger.asm(f"isb", comment="Instruction Synchronization Barrier, must to ensure context-syncronization after enabling MMU")
    
    AsmLogger.comment("Now the MMU is enabled with your page tables")
    AsmLogger.comment("Code can now access virtual addresses defined in your page tables")

    register_manager.free(tmp_reg)

def enable_EL1_page_table():
    curr_state = get_current_state()
    register_manager = curr_state.register_manager
    tmp_reg = register_manager.get_and_reserve(reg_type="gpr")

    # ============= EL1 Non-Secure Setup =============
    AsmLogger.comment("Set up EL1 Non-Secure Translation Tables")
    
    # First disable EL1 MMU
    AsmLogger.comment("First disable the EL1 MMU")
    AsmLogger.asm(f"mrs {tmp_reg}, sctlr_el1")
    AsmLogger.asm(f"bic {tmp_reg}, {tmp_reg}, #1", comment="Clear bit 0 (MMU enable)")
    AsmLogger.asm(f"msr sctlr_el1, {tmp_reg}")
    
    AsmLogger.comment("Set up TTBR0_EL1 (EL1 Translation Table Base Register 0)")
    AsmLogger.asm(f"ldr {tmp_reg}, =LABEL_TTBR0_EL1NS_{curr_state.state_name}", comment="read value of LABEL_TTBR0_EL1NS from memory")
    AsmLogger.asm(f"ldr {tmp_reg}, [{tmp_reg}]", comment="load the value of LABEL_TTBR0_EL1NS")    
    AsmLogger.asm(f"msr ttbr0_el1, {tmp_reg}")

    AsmLogger.comment("Set up TTBR1_EL1 (EL1 Translation Table Base Register 1)")
    AsmLogger.asm(f"ldr {tmp_reg}, =LABEL_TTBR1_EL1NS_{curr_state.state_name}", comment="read value of LABEL_TTBR1_EL1NS from memory")
    AsmLogger.asm(f"ldr {tmp_reg}, [{tmp_reg}]", comment="load the value of LABEL_TTBR1_EL1NS")    
    AsmLogger.asm(f"msr ttbr1_el1, {tmp_reg}")

    AsmLogger.comment("Set up TCR_EL1 (EL1 Translation Control Register)")
    AsmLogger.asm(f"ldr {tmp_reg}, =LABEL_TCR_EL1NS_{curr_state.state_name}", comment="read value of LABEL_TCR_EL1NS from memory")
    AsmLogger.asm(f"ldr {tmp_reg}, [{tmp_reg}]", comment="load the value of LABEL_TCR_EL1NS")    
    AsmLogger.asm(f"msr tcr_el1, {tmp_reg}")

    AsmLogger.comment("Set up MAIR_EL1 (EL1 Memory Attribute Indirection Register)")
    AsmLogger.asm(f"ldr {tmp_reg}, =LABEL_MAIR_EL1NS_{curr_state.state_name}", comment="read value of LABEL_MAIR_EL1NS from memory")
    AsmLogger.asm(f"ldr {tmp_reg}, [{tmp_reg}]", comment="load the value of LABEL_MAIR_EL1NS")    
    AsmLogger.asm(f"msr mair_el1, {tmp_reg}")

    # Enable EL1 MMU
    AsmLogger.comment("Enable EL1 MMU")
    AsmLogger.asm(f"mrs {tmp_reg}, sctlr_el1", comment="read EL1 system control register")
    AsmLogger.asm(f"orr {tmp_reg}, {tmp_reg}, #1", comment="set MMU enable bit (M bit)")
    AsmLogger.asm(f"orr {tmp_reg}, {tmp_reg}, #(1 << 2)", comment="Set bit 2 (Data cache enable)")
    AsmLogger.asm(f"bic {tmp_reg}, {tmp_reg}, #(1 << 20)", comment="Clear bit 20 (WXN)")
    AsmLogger.asm(f"msr sctlr_el1, {tmp_reg}", comment="enable EL1 MMU")
    AsmLogger.asm(f"isb", comment="Instruction Synchronization Barrier, ensure MMU changes take effect")

    AsmLogger.comment("EL1 MMU configuration complete")
    AsmLogger.comment("Now both EL3 and EL1 page tables are configured")
    
    register_manager.free(tmp_reg)

def enable_arm_exception_tables():
    state_manager = get_state_manager()
    exception_manager = get_exception_manager()
    current_state = state_manager.get_active_state()
    exception_tables = exception_manager.get_all_exception_tables(state_name=current_state.state_name)
    for exception_table in exception_tables:
        if exception_table.page_table.execution_context == Configuration.Execution_context.EL3:
            vbar_sysreg = f"vbar_el3"
        elif exception_table.page_table.execution_context == Configuration.Execution_context.EL1_NS:
            vbar_sysreg = f"vbar_el1"
        else:
            raise ValueError(f"Invalid execution context: {exception_table.page_table.execution_context}")
        register_manager = current_state.register_manager
        address_reg = register_manager.get_and_reserve(reg_type="gpr")
        AsmLogger.asm(f"ldr {address_reg}, ={exception_table.vbar_label}", comment="load the address of the vbar label")
        AsmLogger.asm(f"msr {vbar_sysreg}, {address_reg}", comment=f"set the {vbar_sysreg} address")
        register_manager.free(address_reg)



def do_bsp_boot():
    logger = get_logger()
    state_manager = get_state_manager()
    curr_state = state_manager.set_active_state("core0_thread0")
    core_0_el3_page_table = curr_state.current_el_page_table
    if core_0_el3_page_table.execution_context != Configuration.Execution_context.EL3:
        raise ValueError(f"Current page table at this stage should be EL3 page table, but it is {core_0_el3_page_table.execution_context}")

    bsp_boot_blocks = core_0_el3_page_table.segment_manager.get_segments(pool_type=Configuration.Memory_types.BSP_BOOT_CODE)
    if len(bsp_boot_blocks) != 1:
        raise ValueError("bsp_boot_block must contain exactly one element, but it contains: {}".format(len(bsp_boot_blocks)))
    bsp_boot_block = bsp_boot_blocks[0]

    switch_code(bsp_boot_block)

    AsmLogger.comment(f"========================= BSP BOOT CODE - start =====================")
    logger.debug(f"BODY:: Running BSP boot code")
    # all threads will pass through this BSP boot code, and will jump from here to thier indevidual boot segment

    register_manager = curr_state.register_manager
    tmp_reg1 = register_manager.get_and_reserve(reg_type="gpr")
    # Load the stack pointer
    sp_reg = register_manager.get(reg_name="sp")
    register_manager.reserve(sp_reg)
    stack_data_start_address = core_0_el3_page_table.segment_manager.get_stack_data_start_address()

    AsmLogger.comment(f"Load the stack pointer (address of {stack_data_start_address})")
    AsmLogger.asm(f"ldr {tmp_reg1}, ={hex(stack_data_start_address)}")

    AsmLogger.asm(f"mov {sp_reg}, {tmp_reg1}")
    register_manager.free(sp_reg)

    # switch according to thread
    tmp_reg2 = register_manager.get_and_reserve(reg_type="gpr")
    tmp_reg3 = register_manager.get_and_reserve(reg_type="gpr")
    AsmLogger.comment("switch according to thread")
    AsmLogger.asm(f"mrs {tmp_reg1}, mpidr_el1")
    
    # Create sequential core ID mapping: 0x81000000->0, 0x81000001->1, 0x81010000->2, 0x81010001->3
    # Extract Aff0 (core within cluster) - bits [7:0]
    AsmLogger.asm(f"and {tmp_reg2.as_size(32)}, {tmp_reg1.as_size(32)}, #0xff", comment="Extract Aff0 (core within cluster)")
    
    # Extract Aff2 (cluster ID) - bits [23:16] 
    AsmLogger.asm(f"lsr {tmp_reg3}, {tmp_reg1}, #16", comment="Shift right by 16 to get Aff2 in lower bits")
    AsmLogger.asm(f"and {tmp_reg3.as_size(32)}, {tmp_reg3.as_size(32)}, #0xff", comment="Extract Aff2 (cluster ID)")
    
    # Create sequential core ID: (cluster_id * 2) + core_in_cluster
    AsmLogger.asm(f"lsl {tmp_reg3.as_size(32)}, {tmp_reg3.as_size(32)}, #1", comment="cluster_id * 2")
    AsmLogger.asm(f"add {tmp_reg2.as_size(32)}, {tmp_reg2.as_size(32)}, {tmp_reg3.as_size(32)}", comment="sequential_core_id = core_in_cluster + (cluster_id * 2)")

    curr_state = state_manager.get_active_state()

    for state in state_manager.states_dict:

        # TODO:: this is a hack, need to fix this and allow ability to get state without switching to it!!!
        tmp_state = state_manager.set_active_state(state)
        tmp_page_table = tmp_state.current_el_page_table
        boot_blocks = tmp_page_table.segment_manager.get_segments(pool_type=Configuration.Memory_types.BOOT_CODE)
        if len(boot_blocks) != 1:
            raise ValueError(
                "boot_blocks must contain exactly one element, but it contains: {}".format(len(boot_blocks)))
        boot_block = boot_blocks[0]
        boot_code_start_label = boot_block.code_label

        state_manager.set_active_state(curr_state.state_name)

        AsmLogger.asm(f"cmp {tmp_reg2}, #{tmp_state.state_id}")
        #AsmLogger.asm(f"beq {boot_code_start_label}")
        skip_label = Label(postfix=f"skip_label_{curr_state.state_id}")
        AsmLogger.asm(f"bne {skip_label}",comment=f"Skip if NOT equal (inverse of beq)")
        AsmLogger.asm(f"ldr {tmp_reg1}, ={boot_code_start_label}",comment=f"Load far address into temp register")
        AsmLogger.asm(f"br {tmp_reg1}",comment=f"Branch to register (unlimited range)")
        AsmLogger.asm(f"{skip_label}:",comment=f"Local label for the fall-through code")

    register_manager.free(tmp_reg1)
    register_manager.free(tmp_reg2)
    register_manager.free(tmp_reg3)

    return bsp_boot_blocks
