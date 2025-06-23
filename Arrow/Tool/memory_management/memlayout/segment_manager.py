import random
from typing import List, Dict

from Arrow.Tool.memory_management.memory_logger import get_memory_logger
from Arrow.Tool.memory_management.memlayout.segment import MemorySegment, CodeSegment, DataSegment
from Arrow.Utils.configuration_management import Configuration

class SegmentManager:
    def __init__(self, page_table):
        """
        Memory manager class to manage a pool of memory segments.
        """
        logger = get_memory_logger()
        logger.info(f"============ initializing SegmentManager for {page_table.execution_context.value} context")


        self.page_table = page_table
        self.memory_segments: List[MemorySegment] = []
        self.pool_type_mapping: Dict[Configuration.Memory_types, List[MemorySegment]] = {}  # To map pool types to blocks


    def allocate_memory_segment(self, name: str, byte_size:int, memory_type:Configuration.Memory_types, alignment_bits:int=None, VA_eq_PA:bool=False, force_address:int=None, exclusive_segment:bool=True)->MemorySegment:
        """
        Allocate a segment of memory for either code or data
        :param name:ste: name of the segment
        :param byte_size: Size of the segment.
        :param memory_type:Memory_types: type of the segment.
        :param alignment_bits:int: alignment of the segment.
        :param VA_eq_PA:bool: If True, the virtual address must equal the physical address.
        :param exclusive_segment:bool: If True, the segment is exclusive to a specific use-case.
        :return: Allocated memory segment.
        """
        logger = get_memory_logger()
        logger.info("")
        logger.info(f"==================== allocate_memory_segment: {name}, size: {byte_size}, type: {memory_type}")
        if force_address:
            logger.info(f"==================== allocate_memory_segment: using force_address: {hex(force_address)} for allocation")
            if not VA_eq_PA or memory_type != Configuration.Memory_types.BSP_BOOT_CODE:
                raise ValueError("force_address is only supported when VA_eq_PA is True and memory_type is BSP_BOOT_CODE")

        for segment in self.memory_segments:
            if segment.name == name:
                raise ValueError(f"Memory segment with name '{name}' already exists.")

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
        all_intervals = self.page_table.non_allocated_va_intervals
        if page_type == Configuration.Page_types.TYPE_CODE:
            pool = all_intervals.get_intervals(criteria={"page_type": Configuration.Page_types.TYPE_CODE})
            pool_name = "CODE"
        else:
            pool = all_intervals.get_intervals(criteria={"page_type": Configuration.Page_types.TYPE_DATA})
            pool_name = "DATA"

        if len(pool) == 0:
            logger.error(f"No available {pool_name} regions before allocation")
            raise ValueError(f"No available {pool_name} regions before allocation")
        
        try:
            if force_address:
                logger.info(f"Requesting allocation with force_address constraint at {hex(force_address)}")
            elif VA_eq_PA:
                logger.info(f"Requesting allocation with VA=PA constraint")
            
            allocation = self.page_table.allocate_segment(size=byte_size, page_type=page_type, alignment_bits=alignment_bits, VA_eq_PA=VA_eq_PA, force_address=force_address)
            segment_start = allocation.va_start
            segment_size = allocation.size
            segment_pa_start = allocation.pa_start

            # Log detailed information about the allocation, including covered pages
            if hasattr(allocation, 'covered_pages') and allocation.covered_pages:
                num_pages = len(allocation.covered_pages)
                logger.info(f"Allocated memory segment at VA:{hex(segment_start)}:{hex(segment_start+segment_size-1)}, PA:{hex(segment_pa_start)}:{hex(segment_pa_start+segment_size-1)}, size:0x{segment_size:x}, type:{page_type}, " 
                           f"spanning {num_pages} {'page' if num_pages == 1 else 'pages'}")
                
                # If VA_eq_PA, verify that the allocation satisfies this constraint
                if VA_eq_PA:
                    for page in allocation.covered_pages:
                        logger.info(f"  Page: VA:{hex(page.va)}:{hex(page.va+page.size-1)}, PA:{hex(page.pa)}:{hex(page.pa+page.size-1)}")
                        if page.va != page.pa:
                            logger.error(f"Page does not satisfy VA=PA constraint (VA:0x{page.va:x} ≠ PA:0x{page.pa:x})")
                            raise ValueError(f"Page does not satisfy VA=PA constraint (VA:0x{page.va:x} ≠ PA:0x{page.pa:x})")
            else:
                logger.info(f"Allocated memory segment at VA:{hex(segment_start)}:{hex(segment_start+segment_size-1)}, PA:{hex(segment_pa_start)}:{hex(segment_pa_start+segment_size-1)}, size:0x{segment_size:x}, type:{page_type}")
        except ValueError as e:
            logger.error(f"Failed to allocate memory: {e}")
            raise ValueError(f"Could not allocate memory segment '{name}' of size {byte_size} with type {page_type}. "
                             f"Make sure you have pre-allocated pages of the correct type.")
        ##########################################################################################

        if (memory_type == Configuration.Memory_types.CODE) \
            or (memory_type == Configuration.Memory_types.BOOT_CODE) \
            or (memory_type == Configuration.Memory_types.BSP_BOOT_CODE):
            memory_segment = CodeSegment(name=name, page_table=self.page_table, address=segment_start, pa_address=segment_pa_start, byte_size=segment_size, memory_type=memory_type, exclusive_segment=exclusive_segment)
        else:
            memory_segment = DataSegment(name=name, page_table=self.page_table, address=segment_start, pa_address=segment_pa_start, byte_size=segment_size, memory_type=memory_type, is_cross_core=False, exclusive_segment=exclusive_segment)

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


    @staticmethod
    def allocate_cross_core_data_memory_segment():
        """
        Allocate a cross-core segment of data memory, making sure same physical address is used for all MMUs (while VA may be different) 
        All Segments are create at once, same size and offset from thier respective cross-core page.
        """
        name = "cross_core_data_segment"
        byte_size = 2048 # 2KB
        memory_type = Configuration.Memory_types.DATA_PRESERVE
        page_type = Configuration.Page_types.TYPE_DATA

        memory_logger = get_memory_logger()
        from Arrow.Tool.memory_management.memlayout.page_table_manager import get_page_table_manager
        page_table_manager = get_page_table_manager()
        
        # First, find a suitable cross-core page with shared physical memory
        # NOTE: Different cores may map this physical memory to different virtual addresses
        random_page_table = random.choice(page_table_manager.get_all_page_tables())
        memory_logger.info("")
        memory_logger.info(f"==================== {random_page_table.page_table_name} - Finding suitable cross-core memory interval")
              
        # Find all cross-core data pages in the first state
        all_pages = random_page_table.get_pages_by_type(Configuration.Page_types.TYPE_DATA)
        cross_core_pages = []
        for page in all_pages:
            if page.is_cross_core:
                cross_core_pages.append(page)
                
        if len(cross_core_pages) == 0:
            memory_logger.error(f"No cross-core page found in state {random_page_table.page_table_name}", level="error")
            raise ValueError(f"No cross-core page found in state {random_page_table.page_table_name}")
        
        # Select a cross-core page
        cross_core_page = random.choice(cross_core_pages)
        memory_logger.info(f"Selected cross-core page: VA={hex(cross_core_page.va)}:{hex(cross_core_page.va+cross_core_page.size-1)}, PA={hex(cross_core_page.pa)}:{hex(cross_core_page.pa+cross_core_page.size-1)}")
        
        # Find available (unallocated) intervals within this page
        
        # Get all available intervals within this page
        all_non_allocated_data_intervals = random_page_table.non_allocated_va_intervals.get_intervals(criteria={"page_type": Configuration.Page_types.TYPE_DATA})
        contained_intervals = []
        
        for interval in all_non_allocated_data_intervals:
            int_start, int_size = interval.start, interval.size
            int_end = int_start + int_size - 1
            
            # Calculate intersection with page
            if int_end >= cross_core_page.va and int_start <= cross_core_page.va+cross_core_page.size-1:
                # There is some overlap - calculate the contained portion
                contained_start = max(int_start, cross_core_page.va)
                contained_end = min(int_end, cross_core_page.va+cross_core_page.size-1)
                contained_size = contained_end - contained_start + 1
                
                # Only include if the interval is big enough
                if contained_size >= byte_size:
                    contained_intervals.append((contained_start, contained_size))
                    memory_logger.info(f"Found suitable interval: VA:{hex(contained_start)}-{hex(contained_end)}, size:0x{contained_size:x}")
        
        if len(contained_intervals) == 0:
            memory_logger.error(f"No suitable unallocated interval found in cross-core page in state {random_page_table.page_table_name}", level="error")
            raise ValueError(f"No suitable unallocated interval found in cross-core page in state {random_page_table.page_table_name}")
        
        # Choose a random interval from available unallocated intervals
        selected_interval = random.choice(contained_intervals)
        interval_start, interval_size = selected_interval
        memory_logger.info(f"Selected unallocated interval: VA:{hex(interval_start)}-{hex(interval_start+interval_size-1)}, size:0x{interval_size:x}")
        
        # Now randomly select a position within this interval, respecting alignment
        alignment_bits = 4  # 16-byte alignment
        alignment = 1 << alignment_bits
        
        # Calculate the maximum possible start address that ensures the sub-interval fits
        max_start = interval_start + interval_size - byte_size
        
        # Calculate the minimum aligned start address
        min_start = (interval_start + alignment - 1) & ~(alignment - 1)
        
        # Check if there's room after alignment
        if min_start > max_start:
            memory_logger.error(f"No valid aligned position found in the selected interval", level="error")
            raise ValueError(f"No valid aligned position found in the selected interval")
        
        # Choose a random aligned position
        available_positions = ((max_start - min_start) // alignment) + 1
        if available_positions > 1:
            random_position = random.randrange(available_positions)
            chosen_va_start = min_start + (random_position * alignment)
        else:
            chosen_va_start = min_start
        
        # Calculate offset from page start (needed to find corresponding VA in other cores)
        page_offset = chosen_va_start - cross_core_page.va
        

        # The addresses will be used for all cores, and will be shared across cores
        shared_pa = cross_core_page.pa
        shared_pa_start = shared_pa + page_offset
        shared_interval_offset_from_page_start = chosen_va_start - cross_core_page.va
        shared_interval_size = byte_size

        memory_logger.info(f"Chosen position in interval: VA:{hex(chosen_va_start)}:{hex(chosen_va_start+byte_size-1)}, size:{hex(byte_size)}, offset from page start: 0x{page_offset:x}")
        memory_logger.info(f"This corresponds to PA:{hex(shared_pa+page_offset)}:{hex(shared_pa+page_offset+byte_size-1)}")
        
        # Pre-allocate the exact PA region to prevent overlaps across cores
        # This ensures that when each core allocates within the shared page, they coordinate PA usage
        page_table_manager.allocated_pa_intervals.add_region(shared_pa_start, byte_size, metadata={"page_type": Configuration.Page_types.TYPE_DATA, "cross_core": True, "page_table_name": "SHARED"})
        page_table_manager.non_allocated_pa_intervals.remove_region(shared_pa_start, byte_size)
        
        memory_logger.info(f"Pre-allocated shared PA region: {hex(shared_pa_start)}-{hex(shared_pa_start+byte_size-1)} to prevent overlaps")

        # Now allocate in each state using the corresponding VA mapping
        created_segments = []

        all_page_tables = page_table_manager.get_all_page_tables()
        for page_table in all_page_tables:
            memory_logger.info(f"")
            memory_logger.info(f"==================== {page_table.page_table_name} - Allocating cross-core memory segment with PA:{hex(shared_pa+page_offset)}")
            
            segment_manager = page_table.segment_manager
            
            # Find the corresponding cross-core page in this state
            # It should have the same physical address as the first state's cross-core page
            all_pages = page_table.get_pages_by_type(Configuration.Page_types.TYPE_DATA)
            matching_cross_core_page = None
            
            for page in all_pages:
                if page.is_cross_core and page.pa == shared_pa:
                    matching_cross_core_page = page
                    break           
            if not matching_cross_core_page:
                memory_logger.error(f"No matching cross-core page found in state {page_table.page_table_name} with PA={hex(shared_pa)}", level="error")
                raise ValueError(f"No matching cross-core page found in state {page_table.page_table_name} with PA={hex(shared_pa)}")
            
            memory_logger.info(f"Found matching cross-core page: VA={hex(matching_cross_core_page.va)}:{hex(matching_cross_core_page.va+matching_cross_core_page.size-1)}, PA={hex(matching_cross_core_page.pa)}:{hex(matching_cross_core_page.pa+matching_cross_core_page.size-1)}")
            
            segment_size = byte_size
            segment_va_start = matching_cross_core_page.va+shared_interval_offset_from_page_start
            segment_pa_start = shared_pa_start
            segment_va_end = segment_va_start + shared_interval_size - 1
            memory_logger.info(f"Current page interval: VA={hex(segment_va_start)}:{hex(segment_va_end)}, size={hex(shared_interval_size)}")

            # Mark as allocated for this specific page table's VA space (add to allocated, remove from non-allocated)
            page_table.allocated_va_intervals.add_region(segment_va_start, byte_size, metadata={"page_type": Configuration.Page_types.TYPE_DATA, "page_table_name": page_table.page_table_name})
            page_table.non_allocated_va_intervals.remove_region(segment_va_start, byte_size)
    
            # Create MemoryAllocation object with all the details
            from Arrow.Tool.memory_management.memlayout.page_table import MemoryAllocation
            allocation = MemoryAllocation(
                va_start=segment_va_start,
                pa_start=segment_pa_start,
                size=byte_size,
                page_mappings=[matching_cross_core_page],
                page_type=Configuration.Page_types.TYPE_DATA,
                covered_pages=[matching_cross_core_page]
            )
            page_table.allocations.append(allocation)

            memory_logger.info(f"Created allocation: VA={hex(segment_va_start)}:{hex(segment_va_end)}, PA={hex(shared_pa_start)}:{hex(shared_pa_start+byte_size-1)}, size={byte_size}")
                        
            # Log allocation information
            memory_logger.info(f"Allocated memory segment at VA:{hex(segment_va_start)}:{hex(segment_va_end)}, PA:{hex(segment_pa_start)}:{hex(segment_pa_start+segment_size-1)}, size:{hex(segment_size)}, type:{page_type}, is_cross_core:True")
            
            memory_segment = DataSegment(name=name, page_table=page_table, address=segment_va_start, pa_address=segment_pa_start, byte_size=segment_size, memory_type=memory_type, is_cross_core=True, exclusive_segment=False)
            
            # Store the allocation with the segment for future reference (e.g., for freeing)
            memory_segment.allocation = allocation
            
            # Store page information in the memory segment for better tracking
            if hasattr(allocation, 'covered_pages'):
                memory_segment.covered_pages = allocation.covered_pages
            
            segment_manager.memory_segments.append(memory_segment)
            
            # Map the segment to the pool type
            if memory_type not in segment_manager.pool_type_mapping:
                segment_manager.pool_type_mapping[memory_type] = []
            segment_manager.pool_type_mapping[memory_type].append(memory_segment)
            
            created_segments.append(memory_segment)

        # Return the first segment for backward compatibility
        memory_logger.info(f"Created cross-core memory segments at fixed PA={hex(shared_pa+page_offset)} across {len(created_segments)} cores")
        return created_segments[0] if created_segments else None


    def _is_code_page_type(self, page_type):
        """Helper to determine if a page type is code"""
        return page_type == Configuration.Page_types.TYPE_CODE

    def get_segments(self, pool_type:[Configuration.Memory_types | list[Configuration.Memory_types]], non_exclusive_only:bool=False) -> List[MemorySegment]:
        """
        Retrieve memory segments based on specific attributes.

        Args:
            pool_type [Memory_types|list[Memory_types]]: Filter segments by pool type, can receive one or list of many.
            non_exclusive_only [bool]: If True, only return non-exclusive segments. those that are not exclusive to a specific use-case.

        Returns:
            List[MemorySegment]: A list of memory segments that match the criteria.
        """
        memory_logger = get_memory_logger()
        # If `pool_type` is not a list, wrap it in a single-element list
        if not isinstance(pool_type, list):
            pool_types = [pool_type]
        else:
            pool_types = pool_type

        filtered_segments = []
        for pool_type in pool_types:
            if not isinstance(pool_type, Configuration.Memory_types):
                memory_logger.warning(f"ID of pool_type's type:", id(type(pool_type)))
                memory_logger.warning(f"ID of Memory_types:", id(Configuration.Memory_types))
                raise ValueError(f"Invalid pool type {pool_type}.")
            # Filter blocks based on pool_type
            if pool_type in self.pool_type_mapping:
                for segment in self.memory_segments:
                    if (segment in self.pool_type_mapping[pool_type]):
                        if non_exclusive_only:
                            if segment.exclusive_segment:
                                continue
                        filtered_segments.append(segment)

        if not filtered_segments:
            memory_logger.error("No segments available to match the query request.")
            raise ValueError("No segments available to match the query request.")

        return filtered_segments

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


    # def get_segment_dataUnit_list(self, segments_name:str) -> list[DataUnit]:
    #     """
    #     Retrieve DataUnit list of memory segment based on given segment name.

    #     Returns:
    #         list[DataUnit]: A list of the memory segment DataUnits
    #     """
    #     segment = self.get_segment(segments_name)
    #     if segment.memory_type is not Memory_types.DATA_SHARED and segment.memory_type is not Memory_types.DATA_PRESERVE and segment.memory_type is not Memory_types.STACK:
    #         raise ValueError(f"Invalid segment type {segment.memory_type}. Segment need to be of type DATA_SHARED or DATA_PRESERVE or STACK.")
    #     return segment.data_units_list


    def get_stack_data_start_address(self) -> int:
        """
        Retrieve the start address of the stack data segment.
        """
        memory_logger = get_memory_logger()
        stack_blocks = self.get_segments(pool_type=Configuration.Memory_types.STACK)
        if len(stack_blocks) != 1:
            for segment in stack_blocks:
                memory_logger.info(f"Stack segment: {segment.name}, VA:0x{segment.address:x}-0x{segment.address+segment.byte_size-1:x}, size:0x{segment.byte_size:x}")
                memory_logger.info(f"segment: {segment}")
            raise ValueError(
                "stack_blocks must contain exactly one element, but it contains: {}".format(len(stack_blocks)))
        stack_block = stack_blocks[0]
        stack_data_start_address = stack_block.address
        return stack_data_start_address
    
    def print_memory_summary(self, verbose=False):
        """
        Print a summary of all memory structures across all states.
        This is a convenience method that delegates to MemorySpaceManager.

        :param verbose: If True, prints more detailed information
        """
        self.mmu_manager.print_memory_summary(verbose)
        
        # Also print a summary of segments managed by this SegmentManager
        memory_log("\n==== MEMORY SEGMENTS SUMMARY ====")
        memory_log(f"Total segments: {len(self.memory_segments)}")
        
        # Use the utility function to print segments by type
        print_segments_by_type(self.memory_segments, "", verbose)
                    
        memory_log("==== END SEGMENTS SUMMARY ====")
        
