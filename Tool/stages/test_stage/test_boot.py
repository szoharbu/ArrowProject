
from Utils.logger_management import get_logger
from Utils.configuration_management import Configuration, get_config_manager
from Tool.state_management import get_state_manager
from Tool.state_management.switch_state import switch_code
from Tool.frontend.AR_API import AR

def do_boot():
    logger = get_logger()
    state_manager = get_state_manager()
    config_manager = get_config_manager()

    logger.info("============ do_boot")

    # TODO:: refactor this logic!!!!

    for state in state_manager.states_dict:
        state_manager.set_active_state(state)
        current_state = state_manager.get_active_state()

        boot_blocks = current_state.memory_manager.get_segments(pool_type=Configuration.Memory_types.BOOT_CODE)
        if len(boot_blocks) != 1:
            raise ValueError("boot_blocks must contain exactly one element, but it contains: {}".format(len(boot_blocks)))
        boot_block = boot_blocks[0]

        switch_code(boot_block) # switching from a None code block into boot

        logger.debug(f"BODY:: Running boot code")
        AR.comment(f"========================= BOOT CODE - start =====================")

        execution_platform = config_manager.get_value('Execution_platform')
        if execution_platform == "baremetal":
            AR.comment(f"-- memory range address is {hex(current_state.memory_range.address)} with size of {hex(current_state.memory_range.byte_size)}")
            AR.comment(f"-- setting base_register {current_state.base_register} to address of {hex(current_state.base_register_value)}")
            #AR.store_value_into_register(register=current_state.base_register, value=current_state.base_register_value)

        skip_boot = Configuration.Knobs.Config.skip_boot
        if not skip_boot:
             AR.generate(instruction_count=10)

        # selecting random block to jump to for test body
        available_blocks = current_state.memory_manager.get_segments(pool_type=Configuration.Memory_types.CODE)
        selected_block = AR.choice(values=available_blocks)
        AR.BranchToSegment(selected_block).one_way_branch()

        # setting back to boot code for the print, later return to selected block
        switch_code(boot_block)
        AR.comment(f"========================= BOOT CODE - end =====================")
        switch_code(selected_block)