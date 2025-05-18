import random
from typing import List, Dict

from Utils.configuration_management import Configuration, get_config_manager
from Utils.logger_management import get_logger
from Tool.asm_blocks import DataUnit
from Tool.state_management import get_current_state
from Tool.memory_management.memory_segments import MemorySegment, CodeSegment, DataSegment, MemoryRange
from Tool.memory_management.memory_block import MemoryBlock
from Tool.memory_management import interval_lib
from Tool.memory_management.memory_space_manager import get_memory_space_manager
from Tool.memory_management.utils import memory_log, print_segments_by_type

class MemoryManager:
    def __init__(self, memory_range:MemoryRange):
        """
        Memory manager class to manage a pool of memory segments.
        """
        logger = get_logger()
        memory_log("==================== MemoryManager")

        self.memory_range = memory_range

        # Keep a reference to the memory space manager for allocations
        self.memory_space_manager = get_memory_space_manager()
        
        # Legacy interval_lib - kept for backward compatibility with existing code
        #self.interval_lib = interval_lib.IntervalLib(start_address=self.memory_range.address, total_size=self.memory_range.byte_size)
        
        self.memory_segments: List[MemorySegment] = []
        self.pool_type_mapping: Dict[Configuration.Memory_types, List[MemorySegment]] = {}  # To map pool types to blocks


    def allocate_memory_segment(self, name: str, byte_size:int, memory_type:Configuration.Memory_types, alignment_bits:int=None)->MemorySegment:
        """
        Allocate a segment of memory for either code or data
        :param name:ste: name of the segment
        :param byte_size: Size of the segment.
        :param memory_type:Memory_types: type of the segment.
        :param alignment_bits:int: alignment of the segment.
        :return: Allocated memory segment.
        """
        memory_log(f"==================== allocate_memory_segment: {name}, size: {byte_size}, type: {memory_type}")

        for segment in self.memory_segments:
            if segment.name == name:
                raise ValueError(f"Memory segment with name '{name}' already exists.")

        current_state = get_current_state()
        state_name = current_state.state_name
        page_table_manager = current_state.page_table_manager
        
        # Determine the page type based on memory type
        if memory_type in [Configuration.Memory_types.DATA_SHARED, Configuration.Memory_types.DATA_PRESERVE]:
            page_type = Configuration.Page_types.TYPE_DATA
        elif memory_type in [Configuration.Memory_types.CODE, Configuration.Memory_types.BOOT_CODE, Configuration.Memory_types.BSP_BOOT_CODE]:
            page_type = Configuration.Page_types.TYPE_CODE
        else:
            raise ValueError(f"Invalid memory type {memory_type}, type should only be DATA_SHARED, DATA_PRESERVE or CODE.")
        #TODO:: when to use TYPE_DEVICE, TYPE_SYSTEM?   
        
        # Debug: Check available non-allocated pools before allocation
        if page_type == Configuration.Page_types.TYPE_CODE:
            pool = self.memory_space_manager.state_non_allocated_va_code_intervals[state_name]
            pool_name = "CODE"
        else:
            pool = self.memory_space_manager.state_non_allocated_va_data_intervals[state_name]
            pool_name = "DATA"
            
        memory_log(f"Available {pool_name} regions before allocation:")
        for i, interval in enumerate(pool.free_intervals):
            int_start, int_size = interval
            memory_log(f"  {pool_name} region {i}: VA:0x{int_start:x}-0x{int_start+int_size-1:x}, size:0x{int_size:x}")

        ##########################################################################################
        # Directly attempt to allocate memory from the appropriate type-specific pool
        # No fallbacks - just throw errors if allocation fails
        try:
            allocation = self.memory_space_manager.allocate_memory(current_state, byte_size, page_type, alignment_bits)
            segment_start = allocation.va_start
            segment_size = allocation.size
            
            # Log detailed information about the allocation, including covered pages
            if hasattr(allocation, 'covered_pages') and allocation.covered_pages:
                num_pages = len(allocation.covered_pages)
                memory_log(f"Allocated memory segment at VA:0x{segment_start:x}, size:0x{segment_size:x}, type:{page_type}, " 
                           f"spanning {num_pages} {'page' if num_pages == 1 else 'pages'}")
            else:
                memory_log(f"Allocated memory segment at VA:0x{segment_start:x}, size:0x{segment_size:x}, type:{page_type}")
        except ValueError as e:
            memory_log(f"Failed to allocate memory: {e}", level="error")
            raise ValueError(f"Could not allocate memory segment '{name}' of size {byte_size} with type {page_type}. "
                             f"Make sure you have pre-allocated pages of the correct type.")
        ##########################################################################################

        if (memory_type == Configuration.Memory_types.CODE) \
            or (memory_type == Configuration.Memory_types.BOOT_CODE) \
            or (memory_type == Configuration.Memory_types.BSP_BOOT_CODE):
            memory_segment = CodeSegment(name=name, address=segment_start, byte_size=segment_size, memory_type=memory_type)
        else:
            memory_segment = DataSegment(name=name, address=segment_start, byte_size=segment_size, memory_type=memory_type)

        # Store the allocation with the segment for future reference (e.g., for freeing)
        memory_segment.allocation = allocation
        
        # Store page information in the memory segment for better tracking
        if hasattr(allocation, 'covered_pages'):
            memory_segment.covered_pages = allocation.covered_pages
        
        self.memory_segments.append(memory_segment)

        # Map the segment to the pool type
        if memory_type not in self.pool_type_mapping:
            self.pool_type_mapping[memory_type] = []
        self.pool_type_mapping[memory_type].append(memory_segment)

        return memory_segment

    def _is_code_page_type(self, page_type):
        """Helper to determine if a page type is code"""
        return page_type == Configuration.Page_types.TYPE_CODE

    def get_segments(self, pool_type:[Configuration.Memory_types | list[Configuration.Memory_types]]) -> List[MemorySegment]:
        """
        Retrieve memory segments based on specific attributes.

        Args:
            pool_type [Memory_types|list[Memory_types]]: Filter segments by pool type, can receive one or list of many.

        Returns:
            List[MemorySegment]: A list of memory segments that match the criteria.
        """
        logger = get_logger()
        # If `pool_type` is not a list, wrap it in a single-element list
        if not isinstance(pool_type, list):
            pool_types = [pool_type]
        else:
            pool_types = pool_type

        filtered_segmentss = []
        for pool_type in pool_types:
            if not isinstance(pool_type, Configuration.Memory_types):
                memory_log(f"ID of pool_type's type:", id(type(pool_type)), level="warning")
                memory_log(f"ID of Configuration.Memory_types:", id(Configuration.Memory_types), level="warning")
                raise ValueError(f"Invalid pool type {pool_type}.")
            # Filter blocks based on pool_type
            if pool_type in self.pool_type_mapping:
                filtered_segmentss = filtered_segmentss + [segment for segment in self.memory_segments if segment in self.pool_type_mapping[pool_type]]

        if not filtered_segmentss:
                raise ValueError("No segments available to match the query request.")

        return filtered_segmentss

    def get_segment(self, segment_name:str) -> MemorySegment:
        """
        Retrieve a memory segment based on given segment name.

        Returns:
            MemorySegment: A memory segments that match the criteria.
        """

        for segment in self.memory_segments:
            if segment.name == segment_name:
                return segment
        raise ValueError(f"No segment available to match the name requested {segment_name}.")


    def get_segment_dataUnit_list(self, segments_name:str) -> list[DataUnit]:
        """
        Retrieve DataUnit list of memory segment based on given segment name.

        Returns:
            list[DataUnit]: A list of the memory segment DataUnits
        """
        segment = self.get_segment(segments_name)
        if segment.memory_type is not Configuration.Memory_types.DATA_SHARED and segment.memory_type is not Configuration.Memory_types.DATA_PRESERVE:
            raise ValueError(f"Invalid segment type {segment.memory_type}. Segment need to be of type DATA_SHARED or DATA_PRESERVE.")
        return segment.data_units_list

    def print_memory_summary(self, verbose=False):
        """
        Print a summary of all memory structures across all states.
        This is a convenience method that delegates to MemorySpaceManager.

        :param verbose: If True, prints more detailed information
        """
        self.memory_space_manager.print_memory_summary(verbose)
        
        # Also print a summary of segments managed by this MemoryManager
        memory_log("\n==== MEMORY SEGMENTS SUMMARY ====")
        memory_log(f"Total segments: {len(self.memory_segments)}")
        
        # Use the utility function to print segments by type
        print_segments_by_type(self.memory_segments, "", verbose)
                    
        memory_log("==== END SEGMENTS SUMMARY ====")

    def allocate_data_memory(self, name:str, memory_block_id:str, pool_type:Configuration.Memory_types, byte_size:int=8, init_value_byte_representation:list[int]=None, alignment:int=None) -> DataUnit:
        """
        Retrieve data memory operand from the given pools.

        Args:
            pool_type (Memory_types): either 'share' or 'preserve'.
            byte_size (int): size of the memory operand.
        Returns:
            memory: A memory operand from a random data block.
        """
        logger = get_logger()
        config_manager = get_config_manager()
        execution_platform = config_manager.get_value('Execution_platform')

        if pool_type not in [Configuration.Memory_types.DATA_SHARED, Configuration.Memory_types.DATA_PRESERVE]:
            raise ValueError(f"Invalid memory type {pool_type}, type should only be DATA_SHARED or DATA_PRESERVE")

        if pool_type is Configuration.Memory_types.DATA_SHARED and init_value_byte_representation is not None:
            raise ValueError(f"Can't initialize value in a shared memory")

        data_segments = self.get_segments(pool_type)
        selected_segment = random.choice(data_segments)

        if execution_platform == 'baremetal':
            # Always use DATA page type for data memory allocations
            page_type = Configuration.Page_types.TYPE_DATA
            
            if pool_type is Configuration.Memory_types.DATA_SHARED:
                '''
                When DATA_SHARED is asked, the heuristic is as following:
                - randomly select a block
                - randomly select an offset inside that block
                '''
                start_block = selected_segment.address
                end_block = selected_segment.address + selected_segment.byte_size
                offset_inside_block = random.randint(start_block, end_block - byte_size)
                address = offset_inside_block
            else: # pool_type is Configuration.Memory_types.DATA_PRESERVE:
                '''
                When DATA_PRESERVE is asked, the heuristic is as following:
                - Extract interval from the inner interval_lib
                '''
                try:
                    # Use the current state's memory space manager to allocate within this segment
                    current_state = get_current_state()
                    state_name = current_state.state_name
                    
                    # TODO: This is a simplification - we should create a subsegment allocation 
                    # mechanism in memory_space_manager to properly allocate within a segment
                    
                    # For now, just randomly select a position within the segment
                    start_offset = selected_segment.address
                    max_offset = selected_segment.address + selected_segment.byte_size - byte_size
                    
                    if alignment:
                        # Align the start_offset
                        alignment_value = 1 << alignment
                        start_offset = (start_offset + alignment_value - 1) & ~(alignment_value - 1)
                        # Align the max_offset
                        max_offset = max_offset & ~(alignment_value - 1)
                    
                    if max_offset < start_offset:
                        raise ValueError(f"Not enough space in segment {selected_segment.name} for aligned allocation")
                        
                    address = random.randint(start_offset, max_offset)
                    if alignment:
                        # Ensure address is aligned
                        alignment_value = 1 << alignment
                        address = (address + alignment_value - 1) & ~(alignment_value - 1)
                        
                    memory_log(f"Allocated data memory at 0x{address:x}, size:{byte_size}, type:{page_type}")
                except Exception as e:
                    memory_log(f"Failed to allocate data memory: {e}", level="error")
                    raise ValueError(f"Could not allocate data memory in segment {selected_segment.name}")
        else:  # 'linked_elf'
            address = None

        data_unit = DataUnit(name=name, memory_block_id=memory_block_id, address=address, byte_size=byte_size,memory_segment_id=selected_segment.name, init_value_byte_representation=init_value_byte_representation, alignment=alignment)
        selected_segment.data_units_list.append(data_unit)

        return data_unit


    def get_used_memory_block(self, byte_size:int=8) -> [MemoryBlock|None]:
        """
        Retrieve data memory operand from the existing pools.

        Args:
            byte_size (int): size of the memory operand.
        Returns:
            DataUnit: A memory operand from a random data block.
        """

        # extract all shared memory-blocks with byte_size bigger than 'byte-size'
        valid_memory_blocks = []

        data_shared_segments = self.get_segments(Configuration.Memory_types.DATA_SHARED)
        for segment in data_shared_segments:
            for mem_block in segment.memory_block_list:
                if mem_block.byte_size >= byte_size:
                    valid_memory_blocks.append(mem_block)

        if not valid_memory_blocks:
            return None

        selected_memory_block = random.choice(valid_memory_blocks)

        return selected_memory_block
