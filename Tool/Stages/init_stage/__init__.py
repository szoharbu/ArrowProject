import random

from Utils.configuration_management import get_config_manager
from Utils.logger_management import get_logger
from Tool.state_management import get_state_manager, State

def init_state():
    logger = get_logger()
    logger.info("============ init_state")
    state_manager = get_state_manager()

    core_count = 4
    for i in range(core_count):
        # create a state singleton for thread i, and set it's values
        state_id = f'core_{i}'
        logger.info(f'--------------- Creating state for {state_id}')

        curr_state = State(
            state_name=state_id,
            processor_mode="64bit",
            privilege_level=random.randint(0,3),
            register_manager=register_manager.RegisterManager(),
        )
        state_manager.add_state(state_id, curr_state)


def init_section():
    logger = get_logger()
    logger.info("======== init_section")
    config_manager = get_config_manager()

    if not config_manager.is_exist("Architecture"):
        raise ValueError("Error, By this stage you must set the desired architecture (Arm, riscv, x86)")

    init_state()
    # Add additional needed initialization here
    # Instruction loader
    # ...
