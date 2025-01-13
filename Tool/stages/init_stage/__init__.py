import random

from Utils.configuration_management import get_config_manager, Configuration
from Utils.logger_management import get_logger
from Tool.state_management import get_state_manager
from Tool.state_management.state_manager import State
from Tool.register_management import register_manager
from Tool.memory_management import memory_manager, MemoryRange
from Tool.memory_management.interval_lib import IntervalLib

def init_state():
    logger = get_logger()
    logger.info("============ init_state")
    state_manager = get_state_manager()

    # Initialize the memory library with a 4GB space # TODO:: remove this hard-coded limitation
    region_intervals = IntervalLib(start_address=0, total_size=Configuration.ByteSize.SIZE_4G.in_bytes())

    core_count = 4
    for i in range(core_count):
        # create a state singleton for thread i, and set it's values
        state_id = f'core_{i}'
        logger.info(f'--------------- Creating state for {state_id}')

        # allocating 2M MemoryRange per core, and set memory_manager withing this range
        core_memory_region_start, core_memory_region_size = region_intervals.allocate(Configuration.ByteSize.SIZE_2M.in_bytes())
        core_memory_range = MemoryRange(core=state_id, address=core_memory_region_start, byte_size= core_memory_region_size)

        curr_state = State(
            state_name=state_id,
            processor_mode="64bit",
            privilege_level=random.randint(0,3),
            register_manager=register_manager.RegisterManager(),
            memory_manager=memory_manager.MemoryManager(memory_range=core_memory_range)
        )
        state_manager.add_state(state_id, curr_state)

    cores = state_manager.list_states()
    for core in cores:
        state_manager.set_active_state(core)
        state = state_manager.get_active_state()
        print(state)

    state_manager.set_active_state('core_0')

def init_registers():
    logger = get_logger()
    logger.info("============ init_registers")
    state_manager = get_state_manager()
    states = state_manager.states_dict

    for state_id in states.keys():
        state_manager.set_active_state(state_id)
        curr_state = state_manager.get_active_state()
        # Preserving a register to be used as base_register
        curr_state.base_register = curr_state.register_manager.get_and_reserve()

def init_memory():
    logger = get_logger()
    logger.info("============ init_memory")
    state_manager = get_state_manager()
    states = state_manager.states_dict

    for state_id in states.keys():
        state_manager.set_active_state(state_id)
        curr_state = state_manager.get_active_state()

        boot_block = curr_state.memory_manager.allocate_memory_segment(name=f"boot_block", byte_size=0x1000, memory_type=Configuration.Memory_types.BOOT_CODE)
        logger.debug(f"init_memory: allocating boot_block {boot_block}")

        code_block_count = 3
        for i in range(code_block_count):
            code_block = curr_state.memory_manager.allocate_memory_segment(name=f"code_block_{i}", byte_size=0x1000, memory_type=Configuration.Memory_types.CODE)
            logger.debug(f"init_memory: allocating code_block {code_block}")

        data_block_count = 8
        data_shared_count = data_block_count // 2  # First part is half of n (floored)
        data_preserve_count = data_block_count - data_shared_count  # Second part is the remainder
        for i in range(data_shared_count):
            data_block = curr_state.memory_manager.allocate_memory_segment(name=f"data_shared_block_{i}", byte_size=0x1000, memory_type=Configuration.Memory_types.DATA_SHARED)
            logger.debug(f"init_memory: allocating data_shared_block {data_block}")
        for i in range(data_preserve_count):
            data_block = curr_state.memory_manager.allocate_memory_segment(name=f"data_preserve_block_{i}", byte_size=0x1000, memory_type=Configuration.Memory_types.DATA_PRESERVE)
            logger.debug(f"init_memory: allocating data_preserve_block {data_block}")

def init_section():
    logger = get_logger()
    logger.info("======== init_section")
    config_manager = get_config_manager()

    if not config_manager.is_exist("Architecture"):
        raise ValueError("Error, By this stage you must set the desired architecture (Arm, riscv, x86)")

    init_state()
    init_registers()
    init_memory()
    # Add additional needed initialization here
    # Instruction loader
    # ...
