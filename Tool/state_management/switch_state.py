from Tool.state_management.state_manager import State
from Tool.state_management import get_state_manager
from Tool.memory_management.memlayout.segment import CodeSegment
from Tool.memory_management.memlayout.page_table import PageTable
from Utils.configuration_management import Configuration
from Utils.logger_management import get_logger


class SwitchState:
    def __init__(
            self,
            state_name: str,
    ):
        """
        Constructor for the SwitchState class.

        Parameters:
        - state_name (str): Defines the state name to switch into

        Initializes and validates the input parameters.
        """
        state_manager = get_state_manager()
        if state_name not in state_manager.states_dict:
            raise ValueError(f"State {state_name} does not exist.")

        self.initial_state = state_manager.get_active_state()
        self.requested_state_name = state_name

    def __enter__(self):
        state_manager = get_state_manager()
        logger = get_logger()
        current_state = state_manager.get_active_state()
        state_manager.set_active_state(self.requested_state_name)
        logger.debug(f"Switching state: from {current_state.state_name} to {self.requested_state_name}")

    def __exit__(self, exc_type, exc_val, exc_tb):
        state_manager = get_state_manager()
        logger = get_logger()
        current_state = state_manager.get_active_state()
        state_manager.set_active_state(self.initial_state.state_name)
        logger.debug(f"Switching state: from {current_state.state_name} to {self.initial_state.state_name}")

    def one_way_switch(self):
        state_manager = get_state_manager()
        logger = get_logger()

        current_state = state_manager.get_active_state()
        state_manager.set_active_state(self.requested_state_name)
        logger.debug(f"Switching state: from {current_state.state_name} to {self.requested_state_name}")

#
# def switch_state(state_id:str):
#     """
#     Set a state as the active state.
#     :param state_id: Unique identifier for the state to set as active
#     """
#     state_manager = get_state_manager()
#     logger = get_logger()
#
#     if state_id in state_manager.states_dict:
#         current_state = state_manager.active_state_id
#
#         if current_state == state_id:
#             #print(f"No need to switch state, already in {state_id}")
#             return
#
#         state_manager.set_active_state(state_id)
#         active_state = state_manager.get_active_state()
#         logger.debug(f"Switching state: from {current_state} to {state_id}")
#
#     else:
#         raise ValueError(f"State with ID {state_id} does not exist.")
#

def switch_code(new_code:CodeSegment):
    """
    switch to a new code segment.
    """
    state_manager = get_state_manager()
    logger = get_logger()

    if not isinstance(new_code, CodeSegment):
        raise ValueError(f"Cannot switch to segment '{new_code}', not of CodeSegment type.")

    curr_state = state_manager.get_active_state()
    curr_page_table = curr_state.current_el_page_table

    all_code_blocks = curr_page_table.segment_manager.get_segments(
        pool_type=[Configuration.Memory_types.BOOT_CODE,
                   Configuration.Memory_types.BSP_BOOT_CODE,
                   Configuration.Memory_types.CODE])
    if not new_code in all_code_blocks:
        raise ValueError(f"new code block {new_code} doesn't exist in the current state")

    curr_state.current_code_block = new_code

    logger = get_logger()
    logger.debug(f"Switched to code block: {new_code.name} (start address: {hex(new_code.address)}, byte_size: {hex(new_code.byte_size)})")


def switch_exception_level(new_el:int, new_code:CodeSegment, new_page_table:PageTable):
    """
    switch to a new exception level.
    """
    logger = get_logger()
    state_manager = get_state_manager()
    current_state = state_manager.get_active_state()


    logger.debug(f"Switching EL: from {current_state.current_el_level} to {new_el}")

    logger.debug(f"zzzzz before state: {current_state}")

    current_state.per_el_code_block[current_state.current_el_level] = current_state.current_code_block
    current_state.per_el_code_block[new_el] = new_code
    current_state.current_code_block = new_code
    current_state.current_el_level = new_el
    current_state.execution_context = new_page_table.execution_context
    current_state.current_el_page_table = new_page_table

    logger.debug(f"zzzzz after state: {current_state}")

    logger.debug(f"Switched to code block: {new_code.name} (start address: {hex(new_code.address)}, byte_size: {hex(new_code.byte_size)})")
