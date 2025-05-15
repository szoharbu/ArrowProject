
from Arrow.Utils.logger_management import get_logger
from Arrow.Utils.configuration_management import Configuration, get_config_manager
from Arrow.Tool.state_management import get_state_manager
from Arrow.Tool.state_management.switch_state import switch_code
from Arrow.Tool.asm_libraries.asm_logger import AsmLogger
from Arrow.Tool.asm_libraries.branch_to_segment import branch_to_segment
from Arrow.Tool.generation_management.generate import generate

from Arrow.Utils.APIs import choice


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
        AsmLogger.comment(f"========================= BOOT CODE - start =====================")

        execution_platform = config_manager.get_value('Execution_platform')
        if execution_platform == "baremetal":
            AsmLogger.comment(f"-- memory range address is {hex(current_state.memory_range.address)} with size of {hex(current_state.memory_range.byte_size)}")
            AsmLogger.comment(f"-- setting base_register {current_state.base_register} to address of {hex(current_state.base_register_value)}")
            #AsmLogger.store_value_into_register(register=current_state.base_register, value=current_state.base_register_value)

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
