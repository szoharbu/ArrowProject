import random
from typing import List, Dict

from Utils.configuration_management import Configuration, get_config_manager
from Tool.memory_management.memory_logger import get_memory_logger
from Utils.logger_management import get_logger
from Tool.asm_blocks import DataUnit
from Tool.state_management import get_current_state, get_state_manager
from Tool.memory_management.memlayout.segment import MemorySegment, CodeSegment, DataSegment
from Tool.memory_management.memlayout.segment_manager import SegmentManager
from Tool.memory_management.memory_block import MemoryBlock

def allocate_data_memory(segment_manager: SegmentManager,
                        name:str, 
                        memory_block_id:str, 
                        pool_type:Configuration.Memory_types, 
                        byte_size:int=8, 
                        init_value_byte_representation:list[int]=None, 
                        alignment:int=None,
                        cross_core:bool=False) -> DataUnit:
    """
    Retrieve data memory operand from the given pools.

    Args:
        pool_type (Memory_types): either 'share' or 'preserve'.
        byte_size (int): size of the memory operand.
        cross_core (bool): if True, the memory operand will be allocated from a cross-core segment and across all cores' segments.
    Returns:
        memory: A memory operand from a random data block.
    """
    memory_logger = get_memory_logger()
    memory_logger.info(f"==================== allocate_data_memory: {name}, memory_block_id: {memory_block_id}, type: {pool_type}, size: {hex(byte_size)}, cross_core: {cross_core}, page_table: {segment_manager.page_table.page_table_name}")
    config_manager = get_config_manager()
    execution_platform = config_manager.get_value('Execution_platform')


    if pool_type not in [Configuration.Memory_types.DATA_SHARED, Configuration.Memory_types.DATA_PRESERVE]:
        raise ValueError(f"Invalid memory type {pool_type}, type should only be DATA_SHARED or DATA_PRESERVE")

    if pool_type is Configuration.Memory_types.DATA_SHARED and init_value_byte_representation is not None:
        raise ValueError(f"Can't initialize value in a shared memory")

    data_segments = segment_manager.get_segments(pool_type)

    if cross_core:
        if pool_type is not Configuration.Memory_types.DATA_PRESERVE:
            raise ValueError(f"Cross-core memory can only be allocated from DATA_PRESERVE segments")
        
        # filter data_segments to only include cross-core segments
        data_segments = [segment for segment in data_segments if segment.is_cross_core]
    else:  
        #NOTE:: we DONT allow non-cross-core memory to be allocated inside cross-core segments. as later in Linker we only map a single PA block! 
        # filter out all cross-core segments
        data_segments = [segment for segment in data_segments if not segment.is_cross_core]

    memory_logger.info(f"Found {len(data_segments)} segments of type {pool_type}:")
    for i, segment in enumerate(data_segments):
        memory_logger.info(f"  {i+1}. Segment '{segment.name}' VA:0x{segment.address:x}-0x{segment.address+segment.byte_size-1:x}, size:0x{segment.byte_size:x}, is_cross_core: {segment.is_cross_core}")
    
    selected_segment = random.choice(data_segments)
    memory_logger.info(f"Selected segment '{selected_segment.name}' VA:0x{selected_segment.address:x}-0x{selected_segment.address+selected_segment.byte_size-1:x}, size:0x{selected_segment.byte_size:x}")

    if execution_platform == 'baremetal':
        # Always use DATA page type for data memory allocations
        page_type = Configuration.Page_types.TYPE_DATA

        current_state = get_current_state()
        state_name = current_state.state_name

        if pool_type is Configuration.Memory_types.DATA_SHARED:
            '''
            When DATA_SHARED is asked, the heuristic is as following:
            - randomly select a block
            - randomly select an offset inside that block
            '''
            start_block = selected_segment.address
            end_block = selected_segment.address + selected_segment.byte_size

            max_offset = end_block - start_block - byte_size
            
            # Ensure offset maintains alignment requirement
            if alignment and alignment > 1:
                # Calculate max number of aligned positions within the offset range
                max_aligned_positions = max_offset // alignment
                if max_aligned_positions > 0:
                    # Choose random aligned position
                    aligned_position = random.randint(0, max_aligned_positions)
                    segment_offset = aligned_position * alignment
                else:
                    segment_offset = 0
            else:
                segment_offset = random.randint(0, max_offset) if max_offset > 0 else 0
            
            address = start_block + segment_offset
            pa_address = selected_segment.pa_address + segment_offset
            memory_logger.info(f"DATA_SHARED allocation {state_name} - Segment '{selected_segment.name}' at VA:{hex(address)}, PA:{hex(pa_address)}, size:{byte_size}, type:{page_type}")
        else: # pool_type is Memory_types.DATA_PRESERVE:
            '''
            When DATA_PRESERVE is asked, the heuristic is as following:
            - Extract interval from the inner interval_lib
            '''
            try:
                # Use the current state's memory space manager to allocate within this segment
                #memory_log(f"DATA_PRESERVE allocation in state '{state_name}', segment '{selected_segment.name}'")

                if selected_segment.interval_tracker is None:
                    raise ValueError(f"No interval tracker found in segment {selected_segment.name}")

                # Find an available region with proper alignment
                allocation = selected_segment.interval_tracker.find_region(byte_size, alignment)
                if not allocation:
                    memory_logger.error(f"No available space in segment for allocation", level="error")
                    raise ValueError(f"No available space in segment {selected_segment.name}")
                        
                address, _ = allocation
                
                # Remove the allocated region from the available pool
                selected_segment.interval_tracker.remove_region(address, byte_size)
                
                segment_offset = address - selected_segment.address
                pa_address = selected_segment.pa_address + segment_offset
                memory_logger.info(f"DATA_PRESERVE allocation {state_name} - Segment '{selected_segment.name}' at VA:{hex(address)}, PA:{hex(pa_address)}, size:{byte_size}")
                    
            except Exception as e:
                memory_logger.error(f"Failed to allocate data memory: {e}", level="error")
                raise ValueError(f"Could not allocate data memory in segment {selected_segment.name}")
    else:  # 'linked_elf'
        address = None
        pa_address = None
        segment_offset = None
        memory_logger.info(f"Using 'linked_elf' execution platform, address will be determined at link time")

    data_unit = DataUnit(name=name, memory_block_id=memory_block_id, 
                            address=address, pa_address=pa_address, segment_offset=segment_offset, byte_size=byte_size,
                            memory_segment=selected_segment, memory_segment_id=selected_segment.name, 
                            init_value_byte_representation=init_value_byte_representation, 
                            alignment=alignment)
    selected_segment.data_units_list.append(data_unit)
    memory_logger.info(f"Created DataUnit '{name}' in memory block '{memory_block_id}', segment '{selected_segment.name}'")

    per_page_table_data_units = {segment_manager.page_table.page_table_name: data_unit}

    if cross_core:
        from Tool.memory_management.memlayout.page_table_manager import get_page_table_manager

        # when a cross-core memory is allocated, we need to allocate the same memory in all other states.
        current_state = get_current_state()
        current_page_table = current_state.current_el_page_table
        page_table_manager = get_page_table_manager()
        page_tables = page_table_manager.get_all_page_tables()

        all_other_page_tables = [page_table for page_table in page_tables if page_table != current_page_table]

        for other_page_table in all_other_page_tables:
            #find matching cross-core segment, should have the same PA and size as the original segment
            other_segments = other_page_table.segment_manager.get_segments(pool_type)
            other_cross_core_segment = None
            for segment in other_segments:
                if segment.pa_address == selected_segment.pa_address and segment.byte_size == selected_segment.byte_size:
                    other_cross_core_segment = segment
                    break
            if other_cross_core_segment is None:
                raise ValueError(f"No matching cross-core segment found in page table {other_page_table.page_table_name}")

            other_state_block_va_address = other_cross_core_segment.address+segment_offset

            # Remove the allocated region from the available pool
            other_cross_core_segment.interval_tracker.remove_region(other_state_block_va_address, byte_size)
            memory_logger.info(f"DATA_PRESERVE allocation {other_page_table.page_table_name} - Segment '{other_cross_core_segment.name}' at VA:{hex(other_state_block_va_address)}, PA:{hex(pa_address)}, size:{byte_size}")

            other_name = f"{name}__{other_page_table.page_table_name}"
            other_memory_block_id = f"{memory_block_id}__{other_page_table.page_table_name}"
            other_state_data_unit = DataUnit(name=other_name, memory_block_id=other_memory_block_id,  
                                address=other_state_block_va_address, pa_address=pa_address, segment_offset=segment_offset, byte_size=byte_size,
                                memory_segment=other_cross_core_segment, memory_segment_id=other_cross_core_segment.name, 
                                init_value_byte_representation=init_value_byte_representation, 
                                alignment=alignment)
            other_cross_core_segment.data_units_list.append(other_state_data_unit)

            memory_logger.info(f"Created DataUnit '{name}' in memory block '{memory_block_id}', segment '{other_cross_core_segment.name}'")

            per_page_table_data_units[other_page_table.page_table_name] = other_state_data_unit

    return per_page_table_data_units



def get_used_memory_block(segment_manager: SegmentManager, byte_size:int=8, alignment:int=None) -> [MemoryBlock|None]:
    """
    Retrieve data memory operand from the existing pools.

    Args:
        byte_size (int): size of the memory operand.
    Returns:
        DataUnit: A memory operand from a random data block.
    """
    memory_logger = get_memory_logger()
    memory_logger.info(f"==================== get_used_memory_block: requested size: {byte_size} bytes")

    # extract all shared memory-blocks with byte_size bigger than 'byte-size'
    valid_memory_blocks = []

    data_shared_segments = segment_manager.get_segments(Configuration.Memory_types.DATA_SHARED)
    memory_logger.info(f"Searching through {len(data_shared_segments)} DATA_SHARED segments")
    
    for segment in data_shared_segments:
        memory_logger.info(f"Checking segment '{segment.name}' at address 0x{segment.address:x}, size: 0x{segment.byte_size:x}")
        for mem_block in segment.memory_block_list:
            #print(f"mem_block: {mem_block}")
            if mem_block.byte_size >= byte_size:
                # Check if this block can provide the required alignment
                block_address = mem_block.get_address()
                alignment_compatible = True
                
                if alignment and alignment > 1 and block_address is not None:
                    # Check if we can find an aligned position within this block
                    if (block_address % alignment) == 0:
                        # Block itself is aligned, we can use it
                        alignment_compatible = True
                    else:
                        # Block not aligned, find first aligned address within block
                        first_aligned_addr = ((block_address + alignment - 1) // alignment) * alignment
                        block_end = block_address + mem_block.byte_size
                        
                        # Check if aligned position + required size fits within block
                        if first_aligned_addr + byte_size <= block_end:
                            alignment_compatible = True
                            memory_logger.info(f"  Block '{mem_block.name}' can provide alignment: first_aligned=0x{first_aligned_addr:x}, block_end=0x{block_end:x}")
                        else:
                            alignment_compatible = False
                            memory_logger.info(f"  Block '{mem_block.name}' rejected: first_aligned=0x{first_aligned_addr:x} + size={byte_size} > block_end=0x{block_end:x}")
                
                if alignment_compatible:
                    memory_logger.info(f"  Found valid memory block '{mem_block.name}' in segment '{segment.name}', "
                                f"size: {mem_block.byte_size} bytes, address: {hex(block_address if block_address is not None else 0)}, alignment-compatible: {alignment_compatible}")
                    valid_memory_blocks.append((segment, mem_block))

    if not valid_memory_blocks:
        memory_logger.warning("No valid memory blocks found that meet the size requirement")
        return None

    # Select a random memory block
    selected_segment, selected_memory_block = random.choice(valid_memory_blocks)
    memory_logger.info(f"Selected memory block '{selected_memory_block.name}' from segment '{selected_segment.name}', "
                f"address: {hex(selected_memory_block.get_address() if selected_memory_block.get_address() is not None else 0)}, "
                f"size: {selected_memory_block.byte_size} bytes")

    return selected_memory_block
