from typing import List, Dict, Tuple, Optional
import random

from Utils.singleton_management import SingletonManager
from Tool.memory_management.memory_logger import get_memory_logger
from Tool.memory_management.memlayout.page_table import PageTable
from Tool.memory_management.memlayout.interval_lib.interval_lib import IntervalLib
from Utils.configuration_management import Configuration
from Tool.state_management import get_state_manager, get_current_state

# class MemoryAllocation:
#     """Tracks information about a memory allocation"""
#     def __init__(self, va_start, pa_start, size, page_mappings=None, page_type=None, covered_pages=None):
#         self.va_start = va_start
#         self.pa_start = pa_start
#         self.size = size
#         self.page_mappings = page_mappings or []  # List of (va_page, pa_page, size) tuples - For cross-page allocations, track all involved pages
#         self.page_type = page_type  # Track the page type (code, data, etc.)
#         self.covered_pages = covered_pages or []  # List of actual Page objects this allocation spans

#     def __str__(self):
#         """Human-readable string representation"""
#         page_str = f"{len(self.covered_pages)} pages" if self.covered_pages else "unknown pages"
#         return f"MemoryAllocation(VA:0x{self.va_start:x}, PA:0x{self.pa_start:x}, size:0x{self.size:x}, spans {page_str})"
        
#     def __repr__(self):
#         """Detailed string representation"""
#         return self.__str__()


class PageTableManager:
    """
    Manages multiple MMU contexts and coordinates with shared physical address space.
    Provides high-level allocation operations across different MMUs.
    """
    def __init__(self):
        """
        Initialize the MMU Manager with shared PA space..
        """

        logger = get_memory_logger()
        logger.info("")
        logger.info("======================== MemorySpaceManager - init")

        pa_memory_range_start_address = Configuration.ByteSize.SIZE_2G.in_bytes() + Configuration.ByteSize.SIZE_2M.in_bytes() # leaving 2MB for the MMU page table and constants
        pa_memory_range_size = 2 * Configuration.ByteSize.SIZE_4G.in_bytes()

        # va_memory_range_start_address = ByteSize.SIZE_2G.in_bytes() + ByteSize.SIZE_2M.in_bytes(), # leaving 2MB for the MMU page table and constants
        # va_memory_range_size = 2 * ByteSize.SIZE_4G.in_bytes()


        # Initialize interval trackers for PA
        self.unmapped_pa_intervals = IntervalLib(
            start_address=pa_memory_range_start_address, 
            total_size=pa_memory_range_size,
            default_metadata={"state": "unmapped", "type": "pa"}
        )
        self.mapped_pa_intervals = IntervalLib( # empty interval at start, and get filled when pages are mapped.
            default_metadata={"state": "mapped", "type": "pa"}
        )
        self.non_allocated_pa_intervals = IntervalLib(
            default_metadata={"state": "non_allocated", "type": "pa"}  # empty interval at start, and get filled when pages are mapped.
        )
        self.allocated_pa_intervals = IntervalLib( # empty interval at start, and get filled when segments are allocated.
            default_metadata={"state": "allocated", "type": "pa"}
        )

        # MMU management
        self.page_tables: Dict[str, PageTable] = {}  # page_table_name -> PageTable 
        self.core_page_tables: Dict[str, List[str]] = {}  # core_id -> [page_table_names]
        
        # Track allocations for cross-page references
        self.allocations = []  # List of MemoryAllocation objects
        
        logger.info("PageTableManager initialized")
    

    # MMU Management Methods
    def create_page_table(self, page_table_name: str, core_id: str, execution_context:Configuration.Execution_context) -> PageTable:
        
        """Create and register a new PageTable."""
        if page_table_name in self.page_tables:
            raise ValueError(f"PageTable {page_table_name} already exists")

        logger = get_memory_logger()
        logger.info(f"===== Creating PageTable: {page_table_name} for core: {core_id} with execution_context: {execution_context}")

        page_table = PageTable(page_table_name, core_id, execution_context)
        self.page_tables[page_table_name] = page_table
        
        # Initialize the core_mmus list if it doesn't exist
        if core_id not in self.core_page_tables:
            self.core_page_tables[core_id] = []
        
        self.core_page_tables[core_id].append(page_table_name)

        state_manager = get_state_manager()
        orig_state = state_manager.get_active_state()
        tmp_state = state_manager.set_active_state(core_id)
        tmp_state.enabled_page_tables.append(page_table)
        state_manager.set_active_state(orig_state.state_name)
        
        # logger.info("")
        # logger.info(f"================ PageTableManager:: Created and registered PageTable: {page_table_name} for core: {core_id}")
        return page_table
    

    def get_page_table(self, page_table_name: str) -> PageTable:
        """Get an MMU by ID."""
        if page_table_name not in self.page_tables:
            raise ValueError(f"PageTable {page_table_name} does not exist in PageTableManager")
        return self.page_tables.get(page_table_name)
    
    def get_all_page_tables(self) -> List[PageTable]:
        """Get all page tables."""
        return list(self.page_tables.values())
    
    def get_core_page_tables(self, core_id: str) -> List[PageTable]:
        """Get all MMUs for a specific core."""
        page_table_names = self.core_page_tables.get(core_id, [])
        return [self.page_tables[page_table_name] for page_table_name in page_table_names]

    # Physical Address Management
    def allocate_pa_interval(self, size: int, alignment_bits: int = None) -> Tuple[int, int]:
        """Allocate a PA interval from unmapped space."""
        return self.unmapped_pa_intervals.find_and_remove(size, alignment_bits)
    
    # Helper method to determine if a page type is code or data
    def _is_code_page_type(self, page_type):
        """Determine if a page type is code or data"""
        if page_type in [Configuration.Page_types.TYPE_CODE]:
            return True
        elif page_type in [Configuration.Page_types.TYPE_DATA, Configuration.Page_types.TYPE_DEVICE, Configuration.Page_types.TYPE_SYSTEM]:
            return False
        else:
            # Default to data for unknown types
            logger.warning(f"Unknown page type {page_type}, treating as data")
            return False
    
    # New operations for memory mapping and allocation
    def map_va_to_pa(self, page_table, va_addr, pa_addr, size, page_type):
        """
        Maps a VA region to a PA region
        - Moves the region from unmapped to mapped and non-allocated
        - Does not allocate the memory
        
        :param page_table_name: PageTable name
        :param va_addr: Virtual address to map
        :param pa_addr: Physical address to map
        :param size: Size of region in bytes
        :param page_type: Type of page (code, data, device, system)
        :return: Tuple of (va_addr, pa_addr, size)
        """
        # # Ensure the state is initialized
        # self._initialize_state(state_name)
        logger = get_memory_logger()
        logger.info(f"Mapping VA:0x{va_addr:x} to PA:0x{pa_addr:x}, size:0x{size:x}, type:{page_type}")
        
        # Update unmapped/mapped PA intervals
        self.unmapped_pa_intervals.remove_region(pa_addr, size)
        self.mapped_pa_intervals.add_region(pa_addr, size)
        self.non_allocated_pa_intervals.add_region(pa_addr, size, metadata={"page_type": page_type, "page_table": page_table.page_table_name})  # Newly mapped memory is non-allocated

        # Update unmapped/mapped VA intervals for the MMU
        page_table.unmapped_va_intervals.remove_region(va_addr, size)
        page_table.mapped_va_intervals.add_region(va_addr, size)
        page_table.non_allocated_va_intervals.add_region(va_addr, size, metadata={"page_type": page_type})
                            
        # Record the mapping
        return (va_addr, pa_addr, size)
    

    # def _find_va_eq_pa_addresses(self, page_table, size, page_type, alignment_bits=None, page_size=4096):
    #     """
    #     Find VA and PA addresses that satisfy the VA=PA constraint
        
    #     :return: (va_start, pa_start, overlapping_pages)
    #     """
    #     logger = get_memory_logger()
    #     logger.info("Searching for matching VA and PA regions where VA=PA...")
        
    #     pages = page_table.get_pages()
    #     va_eq_pa_pages = []
    #     for page in pages:
    #         if page.va == page.pa:
    #             va_eq_pa_pages.append(page)
    #     logger.info(f"Found {len(va_eq_pa_pages)} pages that satisfy VA=PA")
    #     selected_page = random.choice(va_eq_pa_pages)
    #     logger.info(f"Selected page: {selected_page}")
        
    #     # Get the available regions for both VA and PA
    #     all_va_intervals = page_table.non_allocated_va_intervals.get_intervals(criteria={"page_type": page_type})
        
    #     # Find intervals that overlap with the selected VA=PA page and create intersections
    #     # Since we're in a VA=PA page, VA and PA intervals are identical, so we only need to check VA
    #     suitable_intervals = []
        
    #     for interval in all_va_intervals:
    #         # Check if interval overlaps with the page at all
    #         if interval.start < selected_page.end_va + 1 and (interval.start + interval.size) > selected_page.va:
    #             # Calculate the intersection of the interval with the page
    #             intersection_start = max(interval.start, selected_page.va)
    #             intersection_end = min(interval.start + interval.size - 1, selected_page.end_va)
    #             intersection_size = intersection_end - intersection_start + 1
                
    #             # Check if the intersection is large enough for our allocation
    #             if intersection_size >= size:
    #                 # Create a new interval representing the intersection
    #                 from memlayout.interval_lib.interval_lib import Interval
    #                 intersection_interval = Interval(intersection_start, intersection_size, interval.metadata)
    #                 suitable_intervals.append(intersection_interval)
    #                 logger.info(f"Found suitable intersection: 0x{intersection_start:x}-0x{intersection_end:x} (size: 0x{intersection_size:x}) from interval 0x{interval.start:x}-0x{interval.start + interval.size - 1:x}")
    #             else:
    #                 logger.info(f"Intersection too small: 0x{intersection_start:x}-0x{intersection_end:x} (size: 0x{intersection_size:x}) < required 0x{size:x}")
    #         # else:
    #         #     memory_log(f"No overlap: interval 0x{interval.start:x}-0x{interval.start + interval.size - 1:x} with page 0x{selected_page.va:x}-0x{selected_page.end_va:x}")
        
    #     if len(suitable_intervals) == 0:
    #         logger.error(f"No available {page_type} regions inside VA=PA page that fit size {size}")
    #         raise ValueError(f"No available {page_type} regions inside VA=PA page that fit size {size}")
        
    #     # Select one suitable interval (could be random or first)
    #     selected_interval = random.choice(suitable_intervals)
    #     logger.info(f"Selected interval inside VA=PA page: {hex(selected_interval.start)}-{hex(selected_interval.start + selected_interval.size - 1)}, size: 0x{selected_interval.size:x}")
        
    #     # Apply alignment and find position within the selected interval
    #     if alignment_bits is not None:
    #         alignment = 1 << alignment_bits
    #         # Find the first aligned address within the interval
    #         aligned_start = (selected_interval.start + alignment - 1) & ~(alignment - 1)
            
    #         # Check if the aligned allocation fits within the interval
    #         if aligned_start + size > selected_interval.start + selected_interval.size:
    #             logger.error(f"Aligned allocation doesn't fit in interval")
    #             raise ValueError(f"Cannot fit aligned allocation of size {size} with alignment {alignment_bits} bits in selected interval")
            
    #         # Randomize position within the aligned possibilities
    #         max_aligned_offset = ((selected_interval.start + selected_interval.size - size) & ~(alignment - 1)) - aligned_start
    #         if max_aligned_offset > 0:
    #             # Calculate how many aligned positions are possible
    #             num_positions = (max_aligned_offset // alignment) + 1
    #             random_position = random.randrange(num_positions)
    #             random_offset = random_position * alignment
    #             aligned_start += random_offset
    #             logger.info(f"Randomized aligned position: offset 0x{random_offset:x} from first aligned address")
            
    #         va_start = pa_start = aligned_start
    #     else:
    #         # No alignment required, randomize position within interval
    #         max_offset = selected_interval.size - size
    #         if max_offset > 0:
    #             random_offset = random.randrange(max_offset + 1)
    #             va_start = pa_start = selected_interval.start + random_offset
    #             logger.info(f"Randomized position: offset 0x{random_offset:x} from interval start")
    #         else:
    #             va_start = pa_start = selected_interval.start
        
    #     va_end = va_start + size - 1

    #     # print(f"va_start: {hex(va_start)}, va_end: {hex(va_end)}")
    #     # print(f"pa_start: {hex(pa_start)}")

    #     logger.info(f"Final allocation: VA=PA=0x{va_start:x}-0x{va_end:x}, size=0x{size:x}")
        
    #     # Since we selected our allocation from within the selected_page boundaries,
    #     # the only overlapping page is the one we started with
    #     overlapping_pages = [selected_page]
        
    #     return va_start, pa_start, overlapping_pages


    # def _find_regular_addresses(self, mmu, size, page_type, alignment_bits=None, page_size=4096):
    #     """
    #     Find VA and PA addresses for regular allocation (not VA=PA)
        
    #     :return: (va_start, pa_start, overlapping_pages)
    #     """
    #     logger = get_memory_logger()

    #     intervals = mmu.non_allocated_va_intervals.get_intervals(criteria={"page_type": page_type})
    #     logger.info(f"Looking for {page_type.value} region of size {size}. Available {len(intervals)} regions:")
    #     for i, interval in enumerate(intervals):
    #         logger.info(f"  {page_type.value} region {i}: VA:0x{interval.start:x}-0x{interval.end:x}, size:0x{interval.size:x}")
            
    #     # Find available non-allocated VA region from the relevent pool only, with alignment
    #     va_avail = mmu.non_allocated_va_intervals.find_region(size, alignment_bits)
    #     if not va_avail:
    #         raise ValueError(f"No available non-allocated {page_type.value} VA region of size {size} with alignment {alignment_bits} for MMU {mmu.mmu_name}")
        
    #     va_start, _ = va_avail
    #     logger.info(f"Found suitable VA region starting at {hex(va_start)}")
        
    #     # Check that the region is properly aligned
    #     if alignment_bits is not None:
    #         alignment = 1 << alignment_bits
    #         if va_start % alignment != 0:
    #             logger.error(f"VA address 0x{va_start:x} is not aligned to {alignment_bits} bits!")
    #             raise ValueError(f"Failed to allocate properly aligned memory. VA:0x{va_start:x} is not aligned to {alignment_bits} bits!")
        
    #     # Find the physical address that corresponds to the VA we just found
    #     # Retrieve the page table entries from the current state
    #     page_entries = mmu.get_pages()
        
    #     # Find the page that contains this VA
    #     matching_page = None
    #     overlapping_pages = []
    #     va_end = va_start + size - 1
        
    #     # First, find all pages that overlap with this segment
    #     for page in page_entries:
    #         # Check if the page overlaps with any part of our segment
    #         if (page.va <= va_end and page.end_va >= va_start):
    #             overlapping_pages.append(page)
        
    #     # Sort pages by VA for easier sequential checking
    #     overlapping_pages.sort(key=lambda p: p.va)
        
    #     if overlapping_pages:
    #         logger.info(f"Found {len(overlapping_pages)} pages overlapping with segment VA:{hex(va_start)}-{hex(va_end)}")
            
    #         # Check if pages are sequential without gaps
    #         is_sequential = True
    #         covered_range_start = max(overlapping_pages[0].va, va_start)
    #         covered_range_end = min(overlapping_pages[0].end_va, va_end)
            
    #         for i in range(1, len(overlapping_pages)):
    #             prev_page = overlapping_pages[i-1]
    #             curr_page = overlapping_pages[i]
                
    #             # Check for a gap between pages
    #             if prev_page.end_va + 1 != curr_page.va:
    #                 logger.info(f"Gap detected between pages: {prev_page} and {curr_page}")
    #                 is_sequential = False
    #                 break
                
    #             # Update covered range
    #             if curr_page.va <= va_end:
    #                 covered_range_end = min(curr_page.end_va, va_end)
            
    #         # Verify the pages fully cover our segment
    #         if covered_range_start <= va_start and covered_range_end >= va_end and is_sequential:
    #             logger.info(f"Pages provide complete sequential coverage for the segment")
                
    #             # Calculate the physical address for the start of our segment
    #             # Find which page contains our VA start
    #             containing_page = None
    #             for page in overlapping_pages:
    #                 if page.va <= va_start <= page.end_va:
    #                     containing_page = page
    #                     break
                
    #             if containing_page:
    #                 # Calculate the offset into the page
    #                 offset = va_start - containing_page.va
    #                 # Apply the same offset to get the correct PA
    #                 pa_start = containing_page.pa + offset
    #                 logger.info(f"Found corresponding PA for VA:0x{va_start:x} -> PA:0x{pa_start:x} in page {containing_page}")
                    
    #                 # Verify PA alignment matches VA alignment
    #                 if alignment_bits is not None:
    #                     alignment = 1 << alignment_bits
    #                     if pa_start % alignment != 0:
    #                         logger.error(f"PA address 0x{pa_start:x} is not aligned to {alignment_bits} bits!")
    #                         raise ValueError(f"Failed to allocate properly aligned memory. PA:0x{pa_start:x} is not aligned to {alignment_bits} bits!")
                    
    #                 # Verify physical addresses are sequential by checking each page boundary
    #                 if len(overlapping_pages) > 1:
    #                     for i in range(len(overlapping_pages) - 1):
    #                         curr_page = overlapping_pages[i]
    #                         next_page = overlapping_pages[i+1]
                            
    #                         # Calculate expected PA at the boundary
    #                         pa_at_boundary = curr_page.pa + (curr_page.end_va - curr_page.va)
                            
    #                         # Check if next page's PA follows sequentially
    #                         if pa_at_boundary + 1 != next_page.pa:
    #                             logger.warning(f"Physical memory is not sequential between pages: "
    #                                          f"PA 0x{pa_at_boundary:x} -> 0x{next_page.pa:x}")
    #                             # We'll continue anyway since VA is what matters for allocation
    #             else:
    #                 logger.error(f"Failed to find the specific page containing VA start 0x{va_start:x}")
    #                 raise ValueError(f"Internal error: couldn't identify page containing VA start")
    #         else:
    #             if not is_sequential:
    #                 logger.error(f"Pages are not sequential, cannot allocate segment")
    #             else:
    #                 logger.error(f"Pages don't fully cover segment VA:0x{va_start:x}-0x{va_end:x}, "
    #                            f"covered: 0x{covered_range_start:x}-0x{covered_range_end:x}")
    #             # Fall back to the error case below
    #             overlapping_pages = []
                
    #     if not overlapping_pages:
    #         # If we can't find the page entries (shouldn't happen with proper page management)
    #         # fall back to the original logic as a last resort
    #         logger.error(f"CRITICAL ERROR: Cannot find pages covering VA:0x{va_start:x}-0x{va_end:x}. Page table may be inconsistent!")
    #         raise ValueError(f"CRITICAL ERROR: Cannot find pages covering VA:0x{va_start:x}-0x{va_end:x}. Page table may be inconsistent!")
    #         if is_code:
    #             pa_avail = self.non_allocated_pa_code_intervals.find_region(size, alignment_bits)
    #             if not pa_avail:
    #                 raise ValueError(f"No available non-allocated CODE PA region of size {size} with alignment {alignment_bits}")
    #         else:
    #             pa_avail = self.non_allocated_pa_data_intervals.find_region(size, alignment_bits)
    #             if not pa_avail:
    #                 raise ValueError(f"No available non-allocated DATA PA region of size {size} with alignment {alignment_bits}")
    #         pa_start, _ = pa_avail
    #         logger.warning(f"Using fallback PA allocation: 0x{pa_start:x}. THIS IS LIKELY INCORRECT!")
            
    #     logger.info(f"Using PA region starting at 0x{pa_start:x}")
        
    #     return va_start, pa_start, overlapping_pages


    # def allocate_segment(self, mmu, size, page_type, alignment_bits=None, VA_eq_PA=False, page_size=4096):
    #     """
    #     Allocates memory from mapped but non-allocated regions
    #     - Can allocate cross-page regions if pages are sequential
    #     - Returns allocation information
        
    #     :param mmu: MMU object
    #     :param size: Size in bytes to allocate
    #     :param page_type: Page type to allocate
    #     :param alignment_bits: Alignment in bits (default: None)
    #     :param VA_eq_PA: If True, the virtual address must equal the physical address (default: False)
    #     :param page_size: Page size in bytes (default: 4096)
    #     :return: MemoryAllocation object
    #     """
        
    #     logger.info(f"Allocating memory of size {size} for mmu '{mmu.mmu_name}' with page_type {page_type}, alignment_bits={alignment_bits}, VA_eq_PA={VA_eq_PA}")
        
    #     # Determine if we're allocating code or data
    #     is_code = self._is_code_page_type(page_type)
        
    #     # Find suitable VA and PA addresses based on allocation type
    #     if VA_eq_PA:
    #         va_start, pa_start, overlapping_pages = self._find_va_eq_pa_addresses(mmu, size, page_type, alignment_bits, page_size)
    #     else:
    #         va_start, pa_start, overlapping_pages = self._find_regular_addresses(mmu, size, page_type, alignment_bits, page_size)
            
    #     # From here on, the logic is the same for both allocation types
    #     # Mark as allocated (add to allocated, remove from non-allocated)
    #     mmu.allocated_va_intervals.add_region(va_start, size, metadata={"page_type": page_type, "mmu": mmu.mmu_name})
    #     mmu.non_allocated_va_intervals.remove_region(va_start, size)
        
    #     self.allocated_pa_intervals.add_region(pa_start, size, metadata={"page_type": page_type, "mmu": mmu.mmu_name})
    #     self.non_allocated_pa_intervals.remove_region(pa_start, size)
                
    #     # Create page mappings list for cross-page allocations
    #     page_mappings = []
    #     for offset in range(0, size, page_size):
    #         if offset + page_size <= size:
    #             page_size_to_add = page_size
    #         else:
    #             page_size_to_add = size - offset
                
    #         va_page = va_start + offset
    #         pa_page = pa_start + offset
    #         page_mappings.append((va_page, pa_page, page_size_to_add))
        
    #     # Create MemoryAllocation object with all the details
    #     allocation = MemoryAllocation(
    #         va_start=va_start,
    #         pa_start=pa_start,
    #         size=size,
    #         page_mappings=page_mappings,
    #         page_type=page_type,
    #         covered_pages=overlapping_pages
    #     )
        
    #     # Debug information
    #     if VA_eq_PA:
    #         logger.info(f"Created VA=PA allocation: VA=PA=0x{va_start:x}, size={size}")
    #     else:
    #         logger.info(f"Created allocation: VA=0x{va_start:x}, PA=0x{pa_start:x}, size={size}")
        
    #     self.allocations.append(allocation)
    #     return allocation


    # def free_memory(self, allocation):
    #     """
    #     Frees previously allocated memory
    #     - Keeps the mapping, just moves from allocated to non-allocated
    #     """
        
    #     # Find the state that owns this allocation (use current state if not found)
    #     state_name = get_current_state().state_name
    #     for s_name in self.state_allocated_va_intervals:
    #         if self.state_allocated_va_intervals[s_name].is_region_available(allocation.va_start, allocation.size):
    #             state_name = s_name
    #             break
        
    #     # Ensure the state is initialized
    #     self._initialize_state(state_name)
        
    #     # Move from allocated to non-allocated
    #     self.state_allocated_va_intervals[state_name].remove_region(allocation.va_start, allocation.size)
    #     self.state_non_allocated_va_intervals[state_name].add_region(allocation.va_start, allocation.size)
        
    #     self.allocated_pa_intervals.remove_region(allocation.pa_start, allocation.size)
    #     self.non_allocated_pa_intervals.add_region(allocation.pa_start, allocation.size)
        
    #     # Update type-specific pools
    #     is_code = self._is_code_page_type(allocation.page_type)
    #     if is_code:
    #         self.state_non_allocated_va_code_intervals[state_name].add_region(allocation.va_start, allocation.size)
    #         self.non_allocated_pa_code_intervals.add_region(allocation.pa_start, allocation.size)
    #     else:
    #         self.state_non_allocated_va_data_intervals[state_name].add_region(allocation.va_start, allocation.size)
    #         self.non_allocated_pa_data_intervals.add_region(allocation.pa_start, allocation.size)
        
    #     # Remove allocation record
    #     if allocation in self.allocations:
    #         self.allocations.remove(allocation)
        
    #     memory_log(f"Freed memory at VA:0x{allocation.va_start:x}, PA:0x{allocation.pa_start:x}, size:{allocation.size}")
    #     return True
    
    def is_mapped(self, addr, size=1, is_physical=False, page_type=None):
        """Check if a memory region is mapped"""
        # Determine if we're checking code or data mapping
        is_code = self._is_code_page_type(page_type) if page_type else None
        
        if is_physical:
            if is_code is None:
                return self.mapped_pa_intervals.is_region_available(addr, size)
            elif is_code:
                return self.mapped_pa_code_intervals.is_region_available(addr, size)
            else:
                return self.mapped_pa_data_intervals.is_region_available(addr, size)
        else:
            state_name = get_current_state().state_name
            self._initialize_state(state_name)
            if is_code is None:
                return self.state_mapped_va_intervals[state_name].is_region_available(addr, size)
            elif is_code:
                return self.state_mapped_va_code_intervals[state_name].is_region_available(addr, size)
            else:
                return self.state_mapped_va_data_intervals[state_name].is_region_available(addr, size)
    
    def is_allocated(self, addr, size=1, is_physical=False):
        """Check if a memory region is allocated"""
        if is_physical:
            return self.allocated_pa_intervals.is_region_available(addr, size)
        else:
            state_name = get_current_state().state_name
            self._initialize_state(state_name)
            return self.state_allocated_va_intervals[state_name].is_region_available(addr, size)

    def print_memory_summary(self, verbose=False):
        """
        Prints a summary of all memory structures per state.
        Shows mapped pages and allocated segments for each state.
        
        :param verbose: If True, prints more detailed information
        """
        logger = get_logger()
        logger.info("")
        logger.info("==== MEMORY ALLOCATION SUMMARY ====")
        

        for page_table in self.get_all_page_tables():
            page_table.print_summary()


        # # First, print summary of PA space
        # total_pa_mapped = len(self.mapped_pa_intervals.free_intervals)
        # total_pa_allocated = len(self.allocated_pa_intervals.free_intervals)
        # total_pa_code = len(self.mapped_pa_code_intervals.free_intervals)
        # total_pa_data = len(self.mapped_pa_data_intervals.free_intervals)
        
        # logger.info(f"Physical Address Space:")
        # logger.info(f"  Total mapped regions: {total_pa_mapped} ({total_pa_code} code, {total_pa_data} data)")
        # logger.info(f"  Total allocated regions: {total_pa_allocated}")
        
        # if verbose:
        #     # Print detailed PA intervals using utility function
        #     print_intervals_summary("Code", self.mapped_pa_code_intervals, verbose)
        #     print_intervals_summary("Data", self.mapped_pa_data_intervals, verbose)
        
        # # Then print per-state information
        # for page_table in self.get_all_page_tables():
        #     if page_table.execution_context not in self.state_mapped_va_intervals:
        #         logger.info(f"State {page_table.execution_context}: No memory initialized")
        #         continue
            
                
        #     total_va_mapped = len(page_table.mapped_va_intervals.free_intervals)
        #     total_va_allocated = len(page_table.allocated_va_intervals.free_intervals)
        #     total_va_code = len(page_table.mapped_va_code_intervals.free_intervals)
        #     total_va_data = len(page_table.mapped_va_data_intervals.free_intervals)
            
        #     logger.info(f"\nCore {page_table.core_id} Page Table {page_table.page_table_name}:")
        #     logger.info(f"  Virtual Address Space:")
        #     logger.info(f"    Total mapped regions: {total_va_mapped} ({total_va_code} code, {total_va_data} data)")
        #     logger.info(f"    Total allocated regions: {total_va_allocated}")
            
        #     # Get page table entries if available
        #     if hasattr(page_table, 'page_table_manager'):
        #         page_table_entries = page_table.page_table_manager.get_page_table_entries()
        #         logger.info(f"    Page Table Entries: {len(page_table_entries)}")
                
        #         if verbose:
        #             # Use utility function to print pages by type
        #             print_pages_by_type(page_table_entries, "    ", verbose)
            
        #     # Print information about allocations in this state
        #     state_allocations = [a for a in self.allocations 
        #                        if self.state_allocated_va_intervals[state_name].is_region_available(a.va_start, a.size)]
            
        #     # Use utility function to print allocations
        #     print_allocation_summary(state_allocations, "    ", verbose)
        
        logger.info("==== END MEMORY SUMMARY ====")



# Factory function to retrieve the MMUManager instance
def get_page_table_manager():
    # Access or initialize the singleton variable
    page_table_manager_instance = SingletonManager.get("page_table_manager_instance", default=None)
    if page_table_manager_instance is None:
        page_table_manager_instance = PageTableManager()
        SingletonManager.set("page_table_manager_instance", page_table_manager_instance)
    return page_table_manager_instance