import os
import random
import importlib.util
import sys
from Arrow.Utils.configuration_management import get_config_manager, Configuration
from Arrow.Utils.logger_management import get_logger
from Arrow.Tool.state_management import get_state_manager, get_current_state
from Arrow.Tool.state_management.state_manager import State
from Arrow.Tool.register_management import register_manager
from Arrow.Tool.memory_management.memlayout.interval_lib.interval_lib import IntervalLib
from Arrow.Utils.APIs.choice import choice

from Arrow.Tool.memory_management.memlayout.page_table_manager import get_page_table_manager
from Arrow.Tool.memory_management.memory_logger import get_memory_logger, print_memory_state
from Arrow.Tool.exception_management import get_exception_manager


def init_state():
    logger = get_logger()
    logger.info("============ init_state")
    state_manager = get_state_manager()


    core_count = Configuration.Knobs.Config.core_count.get_value()
    for i in range(core_count):
        # create a state singleton for thread i, and set its values
        state_id = f'core_{i}'
        logger.info(f'--------------- Creating state for {state_id}')


        if Configuration.Architecture.x86:
            # Initialize the memory library with a 4GB space # TODO:: remove this hard-coded limitation
            region_intervals = IntervalLib(start_address=0, total_size=Configuration.ByteSize.SIZE_4G.in_bytes())

            # allocating 2M MemoryRange per core, and set segment_manager withing this range
            core_memory_region_start, core_memory_region_size = region_intervals.find_and_remove(Configuration.ByteSize.SIZE_2M.in_bytes())
            
            core_memory_range = MemoryRange(core=state_id, address=core_memory_region_start,
                                            byte_size=core_memory_region_size)
            base_register_value = core_memory_range.address
            
            curr_state = State.create_state(
                state_name=state_id,
                state_id=i,
                processor_mode=Configuration.Knobs.Config.processor_mode,
                privilege_level=0,
                register_manager=register_manager.RegisterManager(),
                enabled_page_tables = [],
                current_code_block=None,
                base_register=None,
                base_register_value=base_register_value,
            )

        elif Configuration.Architecture.riscv:
            base_register_value = core_memory_range.address + (core_memory_range.byte_size // 2)
            base_register_value = base_register_value & ~0b11  # Round Down (to the nearest multiple of 4) to make it 4-byte aligned

            curr_state = State.create_state(
                state_name=state_id,
                state_id=i,
                processor_mode=Configuration.Knobs.Config.processor_mode,
                privilege_level=0,
                register_manager=register_manager.RegisterManager(),
                enabled_page_tables = [],
                current_code_block=None,
                base_register=None,
                base_register_value=base_register_value,
            )
        elif Configuration.Architecture.arm:
            curr_state = State.create_state(
                state_name=state_id,
                state_id=i,
                exception_level=3,
                execution_context=Configuration.Execution_context.EL3,
                register_manager=register_manager.RegisterManager(),
                enabled_page_tables = [],
                current_code_block=None,
                current_el_page_table=None,
            )
        else:
            raise ValueError(f"Unknown Architecture requested")

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


def init_page_tables():

    logger = get_logger()
    logger.info("======== init_segments")
    memory_logger = get_memory_logger()
    state_manager = get_state_manager()
    page_table_manager = get_page_table_manager()

    # TODO:: make this configurable as a knob
    bsp_boot_address = 0x82000000

    for state_name in state_manager.get_all_states():
        # NOTE: Must create the page tables first before allocating pages
        el3r = page_table_manager.create_page_table(page_table_name=f"{state_name}_el3_root", core_id=state_name, execution_context=Configuration.Execution_context.EL3)
        page_table_manager.create_page_table(page_table_name=f"{state_name}_el1_ns", core_id=state_name, execution_context=Configuration.Execution_context.EL1_NS)

        curr_state = state_manager.set_active_state(state_name)
        curr_state.current_el_page_table = el3r

    state_manager.set_active_state("core_0")
    
    page_tables = page_table_manager.get_all_page_tables()

    # Allocate a cross-core page table from a random page table. preferably to allocate the cross-core page table first to avoid conflicts
    page_table_i = page_tables[0]
    page_table_i.allocate_cross_core_page()

    bsp_code_initiated = False
    for page_table in page_tables:
        memory_logger.info(f"Core: {page_table.core_id} Page Table: {page_table.page_table_name}")
        if page_table.execution_context == Configuration.Execution_context.EL3:

            if not bsp_code_initiated:
                # there is a single bsp_code 4k page, that act as the starting point of all cores before branching to thier specific boot code.
                # this page and section should be located at 0x82000000 (TODO:: hardcoded, set as knob)
                page_table.allocate_page(size=Configuration.Page_sizes.SIZE_4K, page_type=Configuration.Page_types.TYPE_CODE, sequential_page_count=1, VA_eq_PA=True, force_address=bsp_boot_address)
                bsp_code_initiated = True
            
            #Always allocate a code page table that has a VA=PA mapping, needed for boot blocks and possibly for more
            page_table.allocate_page(size=Configuration.Page_sizes.SIZE_2M, page_type=Configuration.Page_types.TYPE_CODE, sequential_page_count=1, VA_eq_PA=True)
        
        for type in [Configuration.Page_types.TYPE_CODE, Configuration.Page_types.TYPE_DATA]:
            count = random.randint(6, 8)
            for _ in range(count):
                sequential_page_count = choice(values={1:90, 2:9, 3:1})
                size = random.choice([Configuration.Page_sizes.SIZE_4K, Configuration.Page_sizes.SIZE_2M])
                page_table.allocate_page(size=size, page_type=type, sequential_page_count=sequential_page_count)


                page = page_table.allocate_page(size=size, page_type=type, sequential_page_count=sequential_page_count)


    state_manager.set_active_state("core_0")


def init_segments():
    logger = get_logger()
    logger.info("======== init_segments")
    logger = None
    memory_logger = get_memory_logger()
    state_manager = get_state_manager()
    page_table_manager = get_page_table_manager()
    page_tables = page_table_manager.get_all_page_tables()

    # TODO:: make this configurable as a knob
    bsp_boot_address = 0x82000000

    core_0_el3_page_table = next(page_table for page_table in page_tables if page_table.core_id == "core_0" and page_table.execution_context == Configuration.Execution_context.EL3)
    # Allocate BSP boot segment. a single segment that act as trampoline for all cores
    bsp_boot_segment = core_0_el3_page_table.segment_manager.allocate_memory_segment(name=f"BSP__boot_segment", 
                                                                    byte_size=0x200,
                                                                    memory_type=Configuration.Memory_types.BSP_BOOT_CODE, 
                                                                    alignment_bits=4, 
                                                                    VA_eq_PA=True,
                                                                    force_address=bsp_boot_address)
    memory_logger.info(f"============ init_segments: allocated BSP_boot_segment {bsp_boot_segment} at {hex(bsp_boot_address)}")

    # Allocating one cross-core segment, ensuring that all core and all MMUs will have one shared PA space
    # This allocation is done here, as it is needed for all cores, and should be done before any other allocation to avoid conflicts
    cross_page_segment = core_0_el3_page_table.segment_manager.allocate_cross_core_data_memory_segment()
    memory_logger.info(f"============ init_segments: allocated cross_page_segment {cross_page_segment}")

    for page_table in page_tables:
        memory_logger.info("")
        memory_logger.info(f"================ init_segments for {page_table.core_id}: {page_table.execution_context}")

        # allocating one boot_segment for each of the states EL3 MMUs
        if page_table.execution_context == Configuration.Execution_context.EL3:
            boot_segment = page_table.segment_manager.allocate_memory_segment(name=f"{page_table.page_table_name}__boot_segment",
                                                                        byte_size=0x200,
                                                                        memory_type=Configuration.Memory_types.BOOT_CODE, 
                                                                        alignment_bits=4, 
                                                                        VA_eq_PA=True)
            memory_logger.info(f"init_memory: allocating boot_segment {boot_segment} for {page_table.core_id}:{page_table.page_table_name}")

        code_segment_count = Configuration.Knobs.Memory.code_segment_count.get_value()
        for i in range(code_segment_count):
            code_segment = page_table.segment_manager.allocate_memory_segment(name=f"{page_table.page_table_name}__code_segment_{i}",
                                                                        byte_size=0x1000,
                                                                        memory_type=Configuration.Memory_types.CODE, 
                                                                        alignment_bits=4)
            memory_logger.info(f"init_memory: allocating code_segment {code_segment} for {page_table.core_id}:{page_table.page_table_name}")

        data_segment_count = Configuration.Knobs.Memory.data_segment_count.get_value()
        data_shared_count = data_segment_count // 2  # First part is half of n (floored)
        data_preserve_count = data_segment_count - data_shared_count  # Second part is the remainder
        for i in range(data_shared_count):
            data_segment = page_table.segment_manager.allocate_memory_segment(name=f"{page_table.page_table_name}__data_shared_segment_{i}",
                                                                        byte_size=0x1000,
                                                                        alignment_bits=4,
                                                                        memory_type=Configuration.Memory_types.DATA_SHARED)
            memory_logger.info(f"init_memory: allocating data_shared_segment {data_segment} for {page_table.core_id}:{page_table.page_table_name}")

        for i in range(data_preserve_count):
            data_segment = page_table.segment_manager.allocate_memory_segment(name=f"{page_table.page_table_name}__data_preserve_segment_{i}", 
                                                                        byte_size=0x1000,
                                                                        alignment_bits=4,
                                                                        memory_type=Configuration.Memory_types.DATA_PRESERVE)
            memory_logger.info(f"init_memory: allocating data_preserve_segment {data_segment} for {page_table.core_id}:{page_table.page_table_name}")

        # Allocate stack space for each of the page tables
        stack_segment = page_table.segment_manager.allocate_memory_segment(name=f"{page_table.page_table_name}__stack_segment",
                                                                        byte_size=0x800,
                                                                        alignment_bits=4,
                                                                        memory_type=Configuration.Memory_types.STACK)
        memory_logger.info(f"init_memory: allocating stack_segment {stack_segment} for {page_table.core_id}:{page_table.page_table_name}")

            
def init_exception_tables():
    logger = get_logger()
    logger.info("======== init_exception_tables")
    page_table_manager = get_page_table_manager()
    page_tables = page_table_manager.get_all_page_tables()
    exception_manager = get_exception_manager()

    from Arrow.Tool.exception_management import AArch64ExceptionVector
    for page_table in page_tables:
        exception_table = exception_manager.add_exception_table(page_table.core_id, page_table.page_table_name)

        exception_table.add_exception_callback(exception=AArch64ExceptionVector.LOWER_A64_SYNCHRONOUS, target_label="callback_label")
        exception_table.populate_exception_table()

        vbar_label = exception_table.get_vbar_label()
        logger.info(f"============ init_exception_tables: {page_table.page_table_name} vbar_label: {vbar_label}")


def init_scenarios():
    logger = get_logger()
    logger.info("============ init_scenarios")
    logger.info("================ import Internal_content")
    import Arrow.Internal_content

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
    init_page_tables()
    init_segments()
    init_exception_tables()
    print_memory_state(print_both=True)

    init_scenarios()

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
            # Create local environment with Arrow tool paths
            env = os.environ.copy()
            if 'ARROW_TOOL_PATH' in os.environ:
                env['PATH'] = os.environ['ARROW_TOOL_PATH']
                
            # Run the git submodule command
            subprocess.run(
                ["git", "submodule", "update", "--init", "--recursive"],
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env
            )
            logger.info(f"Submodule at '{submodule_path}' has been initialized and updated.")
        except subprocess.CalledProcessError as e:
            logger.info(f"Failed to initialize the submodule: {e.stderr.decode('utf-8')}")
            raise
    else:
        logger.info(f"Submodule directory '{submodule_path}' already exists. No action needed.")


