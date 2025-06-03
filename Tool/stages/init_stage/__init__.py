import os
import random
import importlib.util
import sys
from Utils.configuration_management import get_config_manager, Configuration
from Utils.logger_management import get_logger
from Tool.state_management import get_state_manager, get_current_state
from Tool.state_management.state_manager import State
from Tool.register_management import register_manager
from Tool.memory_management import segment_manager, MemoryRange, page_manager
#from Tool.memory_management.mmu_manager import get_mmu_manager
from Tool.memory_management.memory_space_manager import get_mmu_manager
from Tool.memory_management.interval_lib import IntervalLib
from Utils.APIs.choice import choice
from Tool.memory_management.utils import print_memory_state

def init_state():
    logger = get_logger()
    logger.info("============ init_state")
    state_manager = get_state_manager()

    # Initialize the memory library with a 4GB space # TODO:: remove this hard-coded limitation
    region_intervals = IntervalLib(start_address=0, total_size=Configuration.ByteSize.SIZE_4G.in_bytes())

    core_count = Configuration.Knobs.Config.core_count.get_value()
    for i in range(core_count):
        # create a state singleton for thread i, and set its values
        state_id = f'core_{i}'
        logger.info(f'--------------- Creating state for {state_id}')


        if Configuration.Architecture.x86:
            # allocating 2M MemoryRange per core, and set segment_manager withing this range
            core_memory_region_start, core_memory_region_size = region_intervals.find_and_remove(Configuration.ByteSize.SIZE_2M.in_bytes())
            
            core_memory_range = MemoryRange(core=state_id, address=core_memory_region_start,
                                            byte_size=core_memory_region_size)
            base_register_value = core_memory_range.address
            privilege_level = 0
            execution_context=None
        elif Configuration.Architecture.riscv:
            # base_register_value = core_memory_range.address + (core_memory_range.byte_size // 2)
            # base_register_value = base_register_value & ~0b11  # Round Down (to the nearest multiple of 4) to make it 4-byte aligned
            core_memory_range = None
            base_register_value = None
            privilege_level = 0
            execution_context=None
        elif Configuration.Architecture.arm:
            core_memory_range = None
            base_register_value = None
            privilege_level = 3
            execution_context=Configuration.Execution_context.EL3
        else:
            raise ValueError(f"Unknown Architecture requested")

        curr_state = State(
            state_name=state_id,
            state_id=i,
            processor_mode=Configuration.Knobs.Config.processor_mode,
            privilege_level=privilege_level,
            register_manager=register_manager.RegisterManager(),
            enabled_mmus = [],
            execution_context=execution_context,
            current_el_mmu=None,
            memory_range=core_memory_range,
            segment_manager=segment_manager.SegmentManager(memory_range=core_memory_range),
            current_code=None,
            base_register=None,
            base_register_value=base_register_value,
        )
        state_manager.add_state(state_id, curr_state)
        #curr_state.page_table_manager = page_manager.PageTableManager()


    cores = state_manager.get_all_states()
    for core in cores:
        state_manager.set_active_state(core)
        curr_state = state_manager.get_active_state()
        # Preserving a register to be used as base_register
        curr_state.base_register = curr_state.register_manager.get_and_reserve()
        # print(curr_state)

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

    state_manager.set_active_state("core_0")

def init_mmus():
    logger = get_logger()
    logger.info("============ init_MMUs")

    from Tool.memory_management.utils import memory_log

    state_manager = get_state_manager()
    mmu_manager = get_mmu_manager()
    for state_name in state_manager.get_all_states():
        memory_log("")
        memory_log(f"================ init_MMUs: {state_name}")
        state_manager.set_active_state(state_name)
        current_state = get_current_state()
        memory_log(f"================ init_MMUs: {state_name} - Allocating EL3 root MMU")        
        el3r_mmu = mmu_manager.create_mmu(mmu_name=f"{state_name}_el3_root", execution_context=Configuration.Execution_context.EL3)
        current_state.current_el_mmu = el3r_mmu
        #current_state.enabled_mmus.append(el3r_mmu)
        
        memory_log(f"================ init_MMUs: {state_name} - Allocating EL1 NonSecure MMU")        
        el1_ns_mmu = mmu_manager.create_mmu(mmu_name=f"{state_name}_el1_NS", execution_context=Configuration.Execution_context.EL1_NS)
        #current_state.enabled_mmus.append(el1_ns_mmu)


    # Allocating one cross-core page, ensuring that all MMUs will have a different VA that point to a single shared PA space
    current_state = state_manager.get_active_state()
    current_mmu = current_state.current_el_mmu
    current_mmu.allocate_cross_core_page()
    memory_log(f"================ init_MMUs: {current_state.state_name} - Allocated cross-core page")

    for state_name in state_manager.get_all_states():
        #TODO:: improve page table heuristic!!!!
        #TODO:: improve page table heuristic!!!!
        #TODO:: improve page table heuristic!!!!
        state_manager.set_active_state(state_name)
        current_state = get_current_state()

        for mmu in current_state.enabled_mmus:
            if mmu.execution_context == Configuration.Execution_context.EL3:
                mmu.allocate_page(size=Configuration.Page_sizes.SIZE_2M, page_type=Configuration.Page_types.TYPE_CODE, sequential_page_count=1, VA_eq_PA=True)

            for type in [Configuration.Page_types.TYPE_CODE, Configuration.Page_types.TYPE_DATA]:
                count = random.randint(6, 8)
                for _ in range(count):
                    sequential_page_count = choice(values={1:90, 2:9, 3:1})
                    size = random.choice([Configuration.Page_sizes.SIZE_4K, Configuration.Page_sizes.SIZE_2M])
                    mmu.allocate_page(size=size, page_type=type, sequential_page_count=sequential_page_count)

    for state_name in state_manager.get_all_states():
        state_manager.set_active_state(state_name)
        current_state = get_current_state()
        for mmu in current_state.enabled_mmus:
            mmu.print_page_tables()

    state_manager.set_active_state("core_0")


def init_segments():
    logger = get_logger()
    logger.info("============ init_segments")
    state_manager = get_state_manager()
    mmu_manager = get_mmu_manager()

    from Tool.memory_management.utils import memory_log

    for state_name in state_manager.get_all_states():
        state_manager.set_active_state(state_name)
        curr_state = state_manager.get_active_state()
        memory_log("")
        memory_log(f"================ init_segments: {state_name}")

        if state_name == "core_0":
            # Allocate BSP boot segment. a single segment that act as trampoline for all cores
            EL3_mmu = next(mmu for mmu in curr_state.enabled_mmus if mmu.execution_context == Configuration.Execution_context.EL3)
            bsp_boot_segment = curr_state.segment_manager.allocate_memory_segment(mmu=EL3_mmu,
                                                                            name=f"BSP__boot_segment", 
                                                                            byte_size=0x200,
                                                                            memory_type=Configuration.Memory_types.BSP_BOOT_CODE, 
                                                                            alignment_bits=4, 
                                                                            VA_eq_PA=True)
            logger.debug(f"init_memory: allocated BSP_boot_segment {bsp_boot_segment}")

            # Allocating one cross-core page, ensuring that all core and all MMUs will have one shared PA space
            # This allocation is done here, as it is needed for all cores, and should be done before any other allocation to avoid conflicts
            cross_page_segment = curr_state.segment_manager.allocate_cross_core_data_memory_segment()
            logger.debug(f"init_memory: allocated cross_page_segment {cross_page_segment}")

        core_mmus = mmu_manager.get_core_mmus(state_name)

        for mmu in core_mmus:
            # allocating one boot_segment for each of the states EL3 MMUs
            if mmu.execution_context == Configuration.Execution_context.EL3:
                boot_segment = curr_state.segment_manager.allocate_memory_segment(mmu=mmu, 
                                                                            name=f"{state_name}__boot_segment",
                                                                            byte_size=0x200,
                                                                            memory_type=Configuration.Memory_types.BOOT_CODE, 
                                                                            alignment_bits=4, 
                                                                            VA_eq_PA=True)
                logger.debug(f"init_memory: allocating boot_segment {boot_segment} for {state_name}:{mmu.mmu_name}")

            code_segment_count = Configuration.Knobs.Memory.code_segment_count.get_value()
            for i in range(code_segment_count):
                code_segment = curr_state.segment_manager.allocate_memory_segment(mmu=mmu,
                                                                            name=f"{state_name}__code_segment_{i}",
                                                                            byte_size=0x1000,
                                                                            memory_type=Configuration.Memory_types.CODE, 
                                                                            alignment_bits=4)
                logger.debug(f"init_memory: allocating code_segment {code_segment} for {state_name}:{mmu.mmu_name}")

            data_segment_count = Configuration.Knobs.Memory.data_segment_count.get_value()
            data_shared_count = data_segment_count // 2  # First part is half of n (floored)
            data_preserve_count = data_segment_count - data_shared_count  # Second part is the remainder
            for i in range(data_shared_count):
                data_segment = curr_state.segment_manager.allocate_memory_segment(mmu=mmu,
                                                                            name=f"{state_name}__data_shared_segment_{i}",
                                                                            byte_size=0x1000,
                                                                            alignment_bits=4,
                                                                            memory_type=Configuration.Memory_types.DATA_SHARED)
                logger.debug(f"init_memory: allocating data_shared_segment {data_segment} for {state_name}:{mmu.mmu_name}")

            for i in range(data_preserve_count):
                data_segment = curr_state.segment_manager.allocate_memory_segment(mmu=mmu,
                                                                            name=f"{state_name}__data_preserve_segment_{i}", 
                                                                            byte_size=0x1000,
                                                                            alignment_bits=4,
                                                                            memory_type=Configuration.Memory_types.DATA_PRESERVE)
                logger.debug(f"init_memory: allocating data_preserve_segment {data_segment} for {state_name}:{mmu.mmu_name}")

            # Allocate stack space for each of the MMUs
            stack_segment = curr_state.segment_manager.allocate_memory_segment(mmu=mmu,
                                                                            name=f"{state_name}__stack_segment",
                                                                            byte_size=0x800,
                                                                            alignment_bits=4,
                                                                            memory_type=Configuration.Memory_types.STACK)
            logger.debug(f"init_memory: allocating stack_segment {stack_segment} for {state_name}:{mmu.mmu_name}")

    state_manager.set_active_state("core_0")
            


def init_scenarios():
    logger = get_logger()
    logger.info("============ init_scenarios")
    logger.info("================ import Internal_content")
    import Internal_content

    config_manager = get_config_manager()
    external_content_dir_path = config_manager.get_value('external_content_dir_path')
    if external_content_dir_path != "External-content-not-available":

        content_path = os.path.join(external_content_dir_path, "__init__.py")

        # Normalize the path to ensure it's correct for the operating system
        normalized_path = os.path.normpath(content_path)

        cloud_mode = config_manager.get_value('Cloud_mode')
        if cloud_mode:
            '''
            When deploy an app on Community Cloud, the only thing that gets cloned during deployment is the source repo for your app. 
            To access the content_repo submodule we need to execute a 'git submodule update' within the Python code of your app to query your second repo and copy additional files.
            '''
            # ensure_submodule_initialized()

            # # TODO:: failing on Streamlit cloud, need to fix. at the moment blocking this capability
            # logger.warning("Skipping Content initialization, using only scenarios from main template.")
            # return

        logger.info("================ import External content")
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
    init_mmus()
    init_segments()
    init_scenarios()
    print_memory_state(print_both=True)

def ensure_submodule_initialized():
    """
    Ensures that the submodule is initialized and updated.
    If the submodule directory doesn't exist, it initializes and updates the submodule.

    :param submodule_path: Path to the submodule directory.
    """
    import subprocess

    logger = get_logger()
    config_manager = get_config_manager()
    # submodule_path = config_manager.get_value("submodule_content_path")
    submodule_path = config_manager.get_value("content_dir_path")

    if not os.path.isdir(submodule_path):
        logger.info(f"Submodule directory '{submodule_path}' not found. Initializing submodule...")

        try:
            # Run the git submodule command
            subprocess.run(
                ["git", "submodule", "update", "--init", "--recursive"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            logger.info(f"Submodule at '{submodule_path}' has been initialized and updated.")
        except subprocess.CalledProcessError as e:
            logger.info(f"Failed to initialize the submodule: {e.stderr.decode('utf-8')}")
            raise
    else:
        logger.info(f"Submodule directory '{submodule_path}' already exists. No action needed.")


