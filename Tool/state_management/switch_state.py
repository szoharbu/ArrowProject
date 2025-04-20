from Tool.state_management import get_state_manager
from Tool.memory_management.memory_segments import CodeSegment
from Utils.configuration_management import Configuration
from Utils.logger_management import get_logger

def switch_state(state_id:str):
    """
    Set a state as the active state.
    :param state_id: Unique identifier for the state to set as active
    """

    state_manager = get_state_manager()
    logger = get_logger()

    if state_id in state_manager.states_dict:
        current_state = state_manager.active_state_id

        if current_state == state_id:
            #print(f"No need to switch state, already in {state_id}")
            return

        state_manager.set_active_state(state_id)
        active_state = state_manager.get_active_state()
        logger.debug(f"Switching state: from {current_state} to {state_id}")

    else:
        raise ValueError(f"State with ID {state_id} does not exist.")


def switch_code(new_code:CodeSegment):
    """
    switch to a new code block.
    """
    state_manager = get_state_manager()
    logger = get_logger()

    if not isinstance(new_code, CodeSegment):
        raise ValueError(f"Cannot switch to block '{new_code}', not of CodeBlock type.")

    curr_state = state_manager.get_active_state()

    all_code_blocks = curr_state.memory_manager.get_segments(
        pool_type=[Configuration.Memory_types.BOOT_CODE,
                   Configuration.Memory_types.BSP_BOOT_CODE,
                   Configuration.Memory_types.CODE])
    if not new_code in all_code_blocks:
        raise ValueError(f"new code block {new_code} doesn't exist in the current state")

    curr_state.current_code_block = new_code

    logger = get_logger()
    logger.debug(f"Switched to code block: {new_code.name} (start address: {hex(new_code.address)}, byte_size: {hex(new_code.byte_size)})")

