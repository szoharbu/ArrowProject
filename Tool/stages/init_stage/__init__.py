import os
import importlib.util
import sys
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

    core_count = Configuration.Knobs.Config.core_count.get_value()
    for i in range(core_count):
        # create a state singleton for thread i, and set it's values
        state_id = f'core_{i}'
        logger.info(f'--------------- Creating state for {state_id}')

        # allocating 2M MemoryRange per core, and set memory_manager withing this range
        core_memory_region_start, core_memory_region_size = region_intervals.allocate(Configuration.ByteSize.SIZE_2M.in_bytes())
        core_memory_range = MemoryRange(core=state_id, address=core_memory_region_start, byte_size= core_memory_region_size)

        if Configuration.Architecture.x86:
            base_register_value = core_memory_range.address
        elif Configuration.Architecture.riscv:
            # setting base_reg to point to the middle of the memory_range, to support negative offsets
            base_register_value = core_memory_range.address + (core_memory_range.byte_size // 2)
            base_register_value = base_register_value & ~0b11  # Round Down (to the nearest multiple of 4) to make it 4-byte aligned
        elif Configuration.Architecture.arm:
            # setting base_reg to point to the middle of the memory_range, to support negative offsets
            base_register_value = core_memory_range.address + (core_memory_range.byte_size // 2)
            base_register_value = base_register_value & ~0b11  # Round Down (to the nearest multiple of 4) to make it 4-byte aligned
        else:
            raise ValueError(f"Unknown Architecture requested")

        curr_state = State(
            state_name=state_id,
            processor_mode=Configuration.Knobs.Config.processor_mode,
            privilege_level=Configuration.Knobs.Config.privilege_level,
            register_manager=register_manager.RegisterManager(),
            memory_range=core_memory_range,
            memory_manager=memory_manager.MemoryManager(memory_range=core_memory_range),
            current_code=None,
            base_register=None,
            base_register_value=base_register_value,
        )
        state_manager.add_state(state_id, curr_state)

    cores = state_manager.list_states()
    for core in cores:
        state_manager.set_active_state(core)
        curr_state = state_manager.get_active_state()
        # Preserving a register to be used as base_register
        curr_state.base_register = curr_state.register_manager.get_and_reserve()
        #print(curr_state)

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

        code_block_count = Configuration.Knobs.Memory.code_block_count.get_value()
        for i in range(code_block_count):
            code_block = curr_state.memory_manager.allocate_memory_segment(name=f"code_block_{i}", byte_size=0x1000, memory_type=Configuration.Memory_types.CODE)
            logger.debug(f"init_memory: allocating code_block {code_block}")

        data_block_count = Configuration.Knobs.Memory.data_block_count.get_value()
        data_shared_count = data_block_count // 2  # First part is half of n (floored)
        data_preserve_count = data_block_count - data_shared_count  # Second part is the remainder
        for i in range(data_shared_count):
            data_block = curr_state.memory_manager.allocate_memory_segment(name=f"data_shared_block_{i}", byte_size=0x1000, memory_type=Configuration.Memory_types.DATA_SHARED)
            logger.debug(f"init_memory: allocating data_shared_block {data_block}")
        for i in range(data_preserve_count):
            data_block = curr_state.memory_manager.allocate_memory_segment(name=f"data_preserve_block_{i}", byte_size=0x1000, memory_type=Configuration.Memory_types.DATA_PRESERVE)
            logger.debug(f"init_memory: allocating data_preserve_block {data_block}")

def init_scenarios():
    logger = get_logger()
    logger.info("============ init_scenarios")
    config_manager = get_config_manager()
    content_dir = config_manager.get_value('content_dir_path')
    content_path = os.path.join(content_dir,"__init__.py")

    # Normalize the path to ensure it's correct for the operating system
    normalized_path = os.path.normpath(content_path)

    cloud_mode = config_manager.get_value('Cloud_mode')
    if cloud_mode:
        '''
        When deploy an app on Community Cloud, the only thing that gets cloned during deployment is the source repo for your app. 
        To access the content_repo submodule we need to execute a 'git submodule update' within the Python code of your app to query your second repo and copy additional files.
        '''
        ensure_submodule_initialized()

        # TODO:: failing on Streamlit cloud, need to fix. at the moment blocking this capability
        logger.warning("Skipping Content initialization, using only scenarios from main template.")
        return

    spec = importlib.util.spec_from_file_location("scenarios_path", normalized_path)
    foo = importlib.util.module_from_spec(spec)
    sys.modules["scenarios_path"] = foo
    spec.loader.exec_module(foo)

def init_section():
    logger = get_logger()
    logger.info("======== init_section")
    config_manager = get_config_manager()

    if not config_manager.is_exist("Architecture"):
        raise ValueError("Error, By this stage you must set the desired architecture (Arm, riscv, x86)")

    init_state()
    init_registers()
    init_memory()

    init_scenarios()
    # Add additional needed initialization here
    # Instruction loader
    # ...




def ensure_submodule_initialized():

    """
    Ensures that the submodule is initialized and updated.
    If the submodule directory doesn't exist, it initializes and updates the submodule.

    :param submodule_path: Path to the submodule directory.
    """
    import subprocess

    config_manager = get_config_manager()
    #submodule_path = config_manager.get_value("submodule_content_path")
    submodule_path = config_manager.get_value("content_dir_path")

    if not os.path.isdir(submodule_path):
        Tool.logger.info(f"Submodule directory '{submodule_path}' not found. Initializing submodule...")

        try:
            # Run the git submodule command
            subprocess.run(
                ["git", "submodule", "update", "--init", "--recursive"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            Tool.logger.info(f"Submodule at '{submodule_path}' has been initialized and updated.")
        except subprocess.CalledProcessError as e:
            Tool.logger.info(f"Failed to initialize the submodule: {e.stderr.decode('utf-8')}")
            raise
    else:
        Tool.logger.info(f"Submodule directory '{submodule_path}' already exists. No action needed.")


