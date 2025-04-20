from Utils.logger_management import get_logger
from Utils.configuration_management import Configuration, get_config_manager
from Tool.state_management import get_state_manager
from Tool.state_management.switch_state import switch_code
from Tool.asm_libraries.asm_logger import AsmLogger
from Tool.asm_libraries.branch_to_segment import branch_to_segment
from Tool.generation_management.generate import generate

from Utils.APIs import choice


def do_boot():
    logger = get_logger()
    state_manager = get_state_manager()
    config_manager = get_config_manager()

    logger.info("============ do_boot")

    # TODO:: refactor this logic!!!!

    # Allocate BSP boot block. a single block that act as trampoline for all cores
    state_manager.set_active_state("core_0")
    curr_state = state_manager.get_active_state()
    bsp_boot_blocks = curr_state.memory_manager.get_segments(pool_type=Configuration.Memory_types.BSP_BOOT_CODE)
    if len(bsp_boot_blocks) != 1:
        raise ValueError(
            "bsp_boot_block must contain exactly one element, but it contains: {}".format(len(bsp_boot_blocks)))
    bsp_boot_block = bsp_boot_blocks[0]

    switch_code(bsp_boot_block)
    AsmLogger.comment(f"========================= BSP BOOT CODE - start =====================")
    logger.debug(f"BODY:: Running BSP boot code")
    # all threads will pass through this BSP boot code, and will jump from here to thier indevidual boot segment

    boot_blocks = curr_state.memory_manager.get_segments(pool_type=Configuration.Memory_types.BOOT_CODE)

    # TODO:: need to add a logic that query which core is running and jump to the corresponding boot block
    # TEMP WA, I'm jumping to the first boot block for now
    boot_block = boot_blocks[0]
    branch_to_segment.BranchToSegment(boot_block).one_way_branch()

    # setting back to boot code for the print, later return to selected block
    switch_code(bsp_boot_block)
    AsmLogger.comment(f"========================= BSP BOOT CODE - end =====================")
    switch_code(boot_block)

    for state in state_manager.states_dict:
        state_manager.set_active_state(state)
        current_state = state_manager.get_active_state()

        boot_blocks = current_state.memory_manager.get_segments(pool_type=Configuration.Memory_types.BOOT_CODE)
        if len(boot_blocks) != 1:
            raise ValueError(
                "boot_blocks must contain exactly one element, but it contains: {}".format(len(boot_blocks)))
        boot_block = boot_blocks[0]

        switch_code(boot_block)  # switching from a None code block into boot

        logger.debug(f"BODY:: Running boot code")
        AsmLogger.comment(f"========================= BOOT CODE - start =====================")

        execution_platform = config_manager.get_value('Execution_platform')
        if execution_platform == "baremetal":
            AsmLogger.comment(
                f"-- memory range address is {hex(current_state.memory_range.address)} with size of {hex(current_state.memory_range.byte_size)}")
            AsmLogger.comment(
                f"-- setting base_register {current_state.base_register} to address of {hex(current_state.base_register_value)}")
            # AsmLogger.store_value_into_register(register=current_state.base_register, value=current_state.base_register_value)

        skip_boot = Configuration.Knobs.Config.skip_boot
        if not skip_boot:
            generate(instruction_count=10)

        # selecting random block to jump to for test body
        available_blocks = current_state.memory_manager.get_segments(pool_type=Configuration.Memory_types.CODE)
        selected_block = choice.choice(values=available_blocks)
        branch_to_segment.BranchToSegment(selected_block).one_way_branch()

        # setting back to boot code for the print, later return to selected block
        switch_code(boot_block)
        AsmLogger.comment(f"========================= BOOT CODE - end =====================")
        switch_code(selected_block)

    # Create a new list with blocks in the desired order
    all_code_blocks = []
    all_code_blocks.extend(bsp_boot_blocks)  # BSP boot code first
    all_code_blocks.extend(boot_blocks)  # Then boot code
    all_code_blocks.extend(available_blocks)  # Finally regular code blocks
