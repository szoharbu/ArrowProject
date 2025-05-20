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


    def allocate_memory_segment(self, name: str, byte_size:int, memory_type:Configuration.Memory_types, alignment_bits:int=None, VA_eq_PA:bool=False)->MemorySegment:
        """
        Allocate a segment of memory for either code or data
        :param name:ste: name of the segment
        :param byte_size: Size of the segment.
        :param memory_type:Memory_types: type of the segment.
        :param alignment_bits:int: alignment of the segment.
        :param VA_eq_PA:bool: If True, the virtual address must equal the physical address.
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
        if memory_type in [Configuration.Memory_types.DATA_SHARED, Configuration.Memory_types.DATA_PRESERVE, Configuration.Memory_types.STACK]:
            page_type = Configuration.Page_types.TYPE_DATA
        elif memory_type in [Configuration.Memory_types.CODE, Configuration.Memory_types.BOOT_CODE, Configuration.Memory_types.BSP_BOOT_CODE]:
            page_type = Configuration.Page_types.TYPE_CODE
        else:
            raise ValueError(f"Invalid memory type {memory_type}, type should only be DATA_SHARED, DATA_PRESERVE or CODE.")
        #TODO:: when to use TYPE_DEVICE, TYPE_SYSTEM?   
        
        if page_type == Configuration.Page_types.TYPE_CODE:
            # As ARM is risc, and all instructions must be 8-byte aligned, we need to ensure the alignment is at least 3
            if alignment_bits is None or alignment_bits < 3:
                alignment_bits = 3
        # Debug: Check available non-allocated pools before allocation
        if page_type == Configuration.Page_types.TYPE_CODE:
            pool = self.memory_space_manager.state_non_allocated_va_code_intervals[state_name]
            for i, interval in enumerate(pool.free_intervals):
                int_start, int_size = interval
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
            if VA_eq_PA:
                memory_log(f"Requesting allocation with VA=PA constraint")
            
            allocation = self.memory_space_manager.allocate_memory(current_state, byte_size, page_type, alignment_bits, VA_eq_PA)
            segment_start = allocation.va_start
            segment_size = allocation.size
            segment_pa_start = allocation.pa_start

            # Log detailed information about the allocation, including covered pages
            if hasattr(allocation, 'covered_pages') and allocation.covered_pages:
                num_pages = len(allocation.covered_pages)
                memory_log(f"Allocated memory segment at VA:0x{segment_start:x}, PA:0x{segment_pa_start:x}, size:0x{segment_size:x}, type:{page_type}, " 
                           f"spanning {num_pages} {'page' if num_pages == 1 else 'pages'}")
                
                # If VA_eq_PA, verify that the allocation satisfies this constraint
                if VA_eq_PA:
                    for page in allocation.covered_pages:
                        memory_log(f"  Page: VA=0x{page.va:x}, PA=0x{page.pa:x}")
                        if page.va != page.pa:
                            memory_log(f"Page does not satisfy VA=PA constraint (VA:0x{page.va:x} ≠ PA:0x{page.pa:x})", level="error")
                            raise ValueError(f"Page does not satisfy VA=PA constraint (VA:0x{page.va:x} ≠ PA:0x{page.pa:x})")
            else:
                memory_log(f"Allocated memory segment at VA:0x{segment_start:x}, PA:0x{segment_pa_start:x}, size:0x{segment_size:x}, type:{page_type}")
        except ValueError as e:
            memory_log(f"Failed to allocate memory: {e}", level="error")
            raise ValueError(f"Could not allocate memory segment '{name}' of size {byte_size} with type {page_type}. "
                             f"Make sure you have pre-allocated pages of the correct type.")
        ##########################################################################################

        if (memory_type == Configuration.Memory_types.CODE) \
            or (memory_type == Configuration.Memory_types.BOOT_CODE) \
            or (memory_type == Configuration.Memory_types.BSP_BOOT_CODE):
            memory_segment = CodeSegment(name=name, address=segment_start, pa_address=segment_pa_start, byte_size=segment_size, memory_type=memory_type)
        else:
            memory_segment = DataSegment(name=name, address=segment_start, pa_address=segment_pa_start, byte_size=segment_size, memory_type=memory_type)

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
        if segment.memory_type is not Configuration.Memory_types.DATA_SHARED and segment.memory_type is not Configuration.Memory_types.DATA_PRESERVE and segment.memory_type is not Configuration.Memory_types.STACK:
            raise ValueError(f"Invalid segment type {segment.memory_type}. Segment need to be of type DATA_SHARED or DATA_PRESERVE or STACK.")
        return segment.data_units_list

    def get_stack_data_start_address(self) -> int:
        """
        Retrieve the start address of the stack data segment.
        """
        stack_block = self.get_segments(pool_type=Configuration.Memory_types.STACK)
        if len(stack_block) != 1:
            raise ValueError(
                "stack_block must contain exactly one element, but it contains: {}".format(len(stack_block)))
        stack_block = stack_block[0]
        stack_data_start_address = stack_block.address
        return stack_data_start_address
    
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
        
    # def print_memory_blocks_summary(self):
    #     """
    #     Print a summary of all memory blocks within segments.
    #     This helps understand which memory blocks belong to which segments.
    #     """
    #     memory_log("\n==== MEMORY BLOCKS BY SEGMENT SUMMARY ====")
        
    #     for segment in self.memory_segments:
    #         memory_log(f"Segment '{segment.name}' (Type: {segment.memory_type}, Address: 0x{segment.address:x}, Size: 0x{segment.byte_size:x}):")
            
    #         # Print data units in the segment
    #         if hasattr(segment, 'data_units_list') and segment.data_units_list:
    #             memory_log(f"  Data Units ({len(segment.data_units_list)}):")
    #             for idx, data_unit in enumerate(segment.data_units_list):
    #                 memory_log(f"    {idx+1}. DataUnit '{data_unit.name}', Block ID: '{data_unit.memory_block_id}', Address: 0x{data_unit.address:x if data_unit.address is not None else 0}, Size: {data_unit.byte_size}")
    #         else:
    #             memory_log("  No Data Units")
                
    #         # Print memory blocks in the segment
    #         if hasattr(segment, 'memory_block_list') and segment.memory_block_list:
    #             memory_log(f"  Memory Blocks ({len(segment.memory_block_list)}):")
    #             for idx, mem_block in enumerate(segment.memory_block_list):
    #                 memory_log(f"    {idx+1}. Block ID: '{mem_block.memory_block_id}', Address: 0x{mem_block.address:x if mem_block.address is not None else 0}, Size: {mem_block.byte_size}")
    #         else:
    #             memory_log("  No Memory Blocks")
                
    #     memory_log("==== END MEMORY BLOCKS SUMMARY ====")

    def allocate_data_memory(self, name:str, memory_block_id:str, pool_type:Configuration.Memory_types, byte_size:int=8, init_value_byte_representation:list[int]=None, alignment:int=None) -> DataUnit:
        """
        Retrieve data memory operand from the given pools.

        Args:
            pool_type (Memory_types): either 'share' or 'preserve'.
            byte_size (int): size of the memory operand.
        Returns:
            memory: A memory operand from a random data block.
        """
        memory_log(f"==================== allocate_data_memory: {name}, memory_block_id: {memory_block_id}, type: {pool_type}, size: {byte_size}")
        config_manager = get_config_manager()
        execution_platform = config_manager.get_value('Execution_platform')

        if pool_type not in [Configuration.Memory_types.DATA_SHARED, Configuration.Memory_types.DATA_PRESERVE]:
            raise ValueError(f"Invalid memory type {pool_type}, type should only be DATA_SHARED or DATA_PRESERVE")

        if pool_type is Configuration.Memory_types.DATA_SHARED and init_value_byte_representation is not None:
            raise ValueError(f"Can't initialize value in a shared memory")

        data_segments = self.get_segments(pool_type)
        memory_log(f"Found {len(data_segments)} segments of type {pool_type}:")
        for i, segment in enumerate(data_segments):
            memory_log(f"  {i+1}. Segment '{segment.name}' VA:0x{segment.address:x}-0x{segment.address+segment.byte_size-1:x}, size:0x{segment.byte_size:x}")
        
        selected_segment = random.choice(data_segments)
        memory_log(f"Selected segment '{selected_segment.name}' VA:0x{selected_segment.address:x}-0x{selected_segment.address+selected_segment.byte_size-1:x}, size:0x{selected_segment.byte_size:x}")

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
                segment_offset = address - selected_segment.address
                pa_address = selected_segment.pa_address + segment_offset
                memory_log(f"DATA_SHARED allocation in segment '{selected_segment.name}' at VA:{hex(address)}, PA:{hex(pa_address)}, size:{byte_size}, type:{page_type}")
            else: # pool_type is Configuration.Memory_types.DATA_PRESERVE:
                '''
                When DATA_PRESERVE is asked, the heuristic is as following:
                - Extract interval from the inner interval_lib
                '''
                try:
                    # Use the current state's memory space manager to allocate within this segment
                    current_state = get_current_state()
                    state_name = current_state.state_name
                    memory_log(f"DATA_PRESERVE allocation in state '{state_name}', segment '{selected_segment.name}'")
                    
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
                        memory_log(f"Using alignment {alignment} (1<<{alignment}={alignment_value})")
                        memory_log(f"Aligned range: 0x{start_offset:x} to 0x{max_offset:x}")
                    
                    if max_offset < start_offset:
                        memory_log(f"Not enough space in segment for aligned allocation", level="error")
                        raise ValueError(f"Not enough space in segment {selected_segment.name} for aligned allocation")
                        
                    address = random.randint(start_offset, max_offset)
                    if alignment:
                        # Ensure address is aligned
                        alignment_value = 1 << alignment
                        address = (address + alignment_value - 1) & ~(alignment_value - 1)

                    segment_offset = address - selected_segment.address
                    pa_address = selected_segment.pa_address + segment_offset
                    memory_log(f"DATA_PRESERVE allocation in segment '{selected_segment.name}' at VA:{hex(address)}, PA:{hex(pa_address)}, size:{byte_size}, type:{page_type}")
                except Exception as e:
                    memory_log(f"Failed to allocate data memory: {e}", level="error")
                    raise ValueError(f"Could not allocate data memory in segment {selected_segment.name}")
        else:  # 'linked_elf'
            address = None
            pa_address = None
            segment_offset = None
            memory_log(f"Using 'linked_elf' execution platform, address will be determined at link time")

        data_unit = DataUnit(name=name, memory_block_id=memory_block_id, 
                             address=address, pa_address=pa_address, segment_offset=segment_offset, byte_size=byte_size,
                             memory_segment=selected_segment, memory_segment_id=selected_segment.name, 
                             init_value_byte_representation=init_value_byte_representation, 
                             alignment=alignment)
        selected_segment.data_units_list.append(data_unit)
        memory_log(f"Created DataUnit '{name}' in memory block '{memory_block_id}', segment '{selected_segment.name}'")

        return data_unit


    def get_used_memory_block(self, byte_size:int=8) -> [MemoryBlock|None]:
        """
        Retrieve data memory operand from the existing pools.

        Args:
            byte_size (int): size of the memory operand.
        Returns:
            DataUnit: A memory operand from a random data block.
        """
        memory_log(f"==================== get_used_memory_block: requested size: {byte_size} bytes")

        # extract all shared memory-blocks with byte_size bigger than 'byte-size'
        valid_memory_blocks = []

        data_shared_segments = self.get_segments(Configuration.Memory_types.DATA_SHARED)
        memory_log(f"Searching through {len(data_shared_segments)} DATA_SHARED segments")
        
        for segment in data_shared_segments:
            memory_log(f"Checking segment '{segment.name}' at address 0x{segment.address:x}, size: 0x{segment.byte_size:x}")
            for mem_block in segment.memory_block_list:
                print(f"mem_block: {mem_block}")
                if mem_block.byte_size >= byte_size:
                    memory_log(f"  Found valid memory block '{mem_block.name}' in segment '{segment.name}', "
                               f"size: {mem_block.byte_size} bytes, address: {hex(mem_block.address if mem_block.address is not None else 0)}")
                    valid_memory_blocks.append((segment, mem_block))

        if not valid_memory_blocks:
            memory_log("No valid memory blocks found that meet the size requirement", level="warning")
            return None

        # Select a random memory block
        selected_segment, selected_memory_block = random.choice(valid_memory_blocks)
        memory_log(f"Selected memory block '{selected_memory_block.name}' from segment '{selected_segment.name}', "
                   f"address: {hex(selected_memory_block.address if selected_memory_block.address is not None else 0)}, "
                   f"size: {selected_memory_block.byte_size} bytes")

        return selected_memory_block
