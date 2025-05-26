from typing import List, Dict, Tuple, Optional
import random

from Utils.configuration_management import Configuration, get_config_manager
from Tool.state_management import get_state_manager, get_current_state
from Utils.logger_management import get_logger
from Utils.singleton_management import SingletonManager

from Tool.memory_management.memory_segments import MemoryRange
from Tool.memory_management import interval_lib
from Tool.memory_management.utils import memory_log

class MemoryAllocation:
    """Tracks information about a memory allocation"""
    def __init__(self, va_start, pa_start, size, page_mappings=None, page_type=None, covered_pages=None):
        self.va_start = va_start
        self.pa_start = pa_start
        self.size = size
        self.page_mappings = page_mappings or []  # List of (va_page, pa_page, size) tuples - For cross-page allocations, track all involved pages
        self.page_type = page_type  # Track the page type (code, data, etc.)
        self.covered_pages = covered_pages or []  # List of actual Page objects this allocation spans

    def __str__(self):
        """Human-readable string representation"""
        page_str = f"{len(self.covered_pages)} pages" if self.covered_pages else "unknown pages"
        return f"MemoryAllocation(VA:0x{self.va_start:x}, PA:0x{self.pa_start:x}, size:0x{self.size:x}, spans {page_str})"
        
    def __repr__(self):
        """Detailed string representation"""
        return self.__str__()

class MemorySpaceManager:
    '''
    MemorySpaceManager
    responsible for managing the memory space across the entire test. 
    any SegmentManager or PageTableManager will use this class to manage the memory space.
    '''
    def __init__(self):
        """
        MemorySpaceManager class to manage the memory space across the entire test.
        """
        memory_log("\n")
        memory_log("======================== MemorySpaceManager - init", "info")

        # TODO:: Need to extract the PA space from the configuration
        self.pa_memory_range = MemoryRange(core="PA", 
                                      address=Configuration.ByteSize.SIZE_2G.in_bytes() + Configuration.ByteSize.SIZE_2M.in_bytes(), # leaving 2MB for the MMU page table and constants
                                      byte_size=2 * Configuration.ByteSize.SIZE_4G.in_bytes())
        
        self.va_memory_range = MemoryRange(core="VA", 
                                      address=Configuration.ByteSize.SIZE_2G.in_bytes() + Configuration.ByteSize.SIZE_2M.in_bytes(), # leaving 2MB for the MMU page table and constants
                                      byte_size=2 * Configuration.ByteSize.SIZE_4G.in_bytes())


        # Initialize interval trackers for PA
        self.unmapped_pa_intervals = interval_lib.IntervalLib(
            start_address=self.pa_memory_range.address, 
            total_size=self.pa_memory_range.byte_size
        )
        self.mapped_pa_intervals = interval_lib.IntervalLib(
            start_address=self.pa_memory_range.address, 
            total_size=self.pa_memory_range.byte_size,
            is_empty=True
        )
        self.allocated_pa_intervals = interval_lib.IntervalLib(
            start_address=self.pa_memory_range.address, 
            total_size=self.pa_memory_range.byte_size,
            is_empty=True
        )
        self.non_allocated_pa_intervals = interval_lib.IntervalLib(
            start_address=self.pa_memory_range.address, 
            total_size=self.pa_memory_range.byte_size,
            is_empty=True   # it should start empty, and get filled when pages are mapped.
        )
        
        # Track code and data pages separately
        self.mapped_pa_code_intervals = interval_lib.IntervalLib(
            start_address=self.pa_memory_range.address, 
            total_size=self.pa_memory_range.byte_size,
            is_empty=True
        )
        self.mapped_pa_data_intervals = interval_lib.IntervalLib(
            start_address=self.pa_memory_range.address, 
            total_size=self.pa_memory_range.byte_size,
            is_empty=True
        )
        self.non_allocated_pa_code_intervals = interval_lib.IntervalLib(
            start_address=self.pa_memory_range.address, 
            total_size=self.pa_memory_range.byte_size,
            is_empty=True  # it should start empty, and get filled when pages are mapped.
        )
        self.non_allocated_pa_data_intervals = interval_lib.IntervalLib(
            start_address=self.pa_memory_range.address, 
            total_size=self.pa_memory_range.byte_size,
            is_empty=True  # it should start empty, and get filled when pages are mapped.
        )
        
        # Initialize per-state VA space (Virtual Address)
        self.state_unmapped_va_intervals = {}
        self.state_mapped_va_intervals = {}
        self.state_allocated_va_intervals = {}
        self.state_non_allocated_va_intervals = {}
        
        # Add type-specific tracking for VA intervals
        self.state_mapped_va_code_intervals = {}
        self.state_mapped_va_data_intervals = {}
        self.state_non_allocated_va_code_intervals = {}
        self.state_non_allocated_va_data_intervals = {}
        
        # Track allocations for cross-page references
        self.allocations = []  # List of MemoryAllocation objects
        
        # Don't initialize states here - they don't exist yet!
        # States will be initialized when they're added via force_initialize_state()
        memory_log("MemorySpaceManager initialized - states will be initialized when added")
    
    def _initialize_all_states(self):
        """Initialize intervals for all known states"""
        
        state_manager = get_state_manager()
        
        # Initialize all existing states
        for state_name in state_manager.get_all_states():
            self._initialize_state(state_name)
            memory_log(f"Initialized memory intervals for state: {state_name}")
    
    def _initialize_state(self, state_name):
        """Initialize interval tracking for a specific state"""
        
        # Check if already initialized
        if state_name in self.state_unmapped_va_intervals:
            #memory_log(f"State {state_name} already initialized")
            return
        
        
        # Unmapped starts as full range
        self.state_unmapped_va_intervals[state_name] = interval_lib.IntervalLib(
            start_address=self.va_memory_range.address, 
            total_size=self.va_memory_range.byte_size
        )
        
        # Mapped and allocation tracking start empty
        self.state_mapped_va_intervals[state_name] = interval_lib.IntervalLib(
            start_address=self.va_memory_range.address, 
            total_size=self.va_memory_range.byte_size,
            is_empty=True
        )
        self.state_allocated_va_intervals[state_name] = interval_lib.IntervalLib(
            start_address=self.va_memory_range.address, 
            total_size=self.va_memory_range.byte_size,
            is_empty=True
        )
        self.state_non_allocated_va_intervals[state_name] = interval_lib.IntervalLib(
            start_address=self.va_memory_range.address, 
            total_size=self.va_memory_range.byte_size,
            is_empty=True
        )
        
        # Initialize type-specific interval trackers
        self.state_mapped_va_code_intervals[state_name] = interval_lib.IntervalLib(
            start_address=self.va_memory_range.address, 
            total_size=self.va_memory_range.byte_size,
            is_empty=True
        )
        self.state_mapped_va_data_intervals[state_name] = interval_lib.IntervalLib(
            start_address=self.va_memory_range.address, 
            total_size=self.va_memory_range.byte_size,
            is_empty=True
        )
        self.state_non_allocated_va_code_intervals[state_name] = interval_lib.IntervalLib(
            start_address=self.va_memory_range.address, 
            total_size=self.va_memory_range.byte_size,
            is_empty=True
        )
        self.state_non_allocated_va_data_intervals[state_name] = interval_lib.IntervalLib(
            start_address=self.va_memory_range.address, 
            total_size=self.va_memory_range.byte_size,
            is_empty=True
        )
        
        memory_log(f"Created new memory intervals for state: {state_name}")
    
    # Legacy accessors (for backward compatibility)
    def get_PA_interval_lib(self):
        return self.unmapped_pa_intervals
    
    def get_VA_interval_lib(self):
        current_state = get_current_state()
        return self.state_unmapped_va_intervals[current_state.state_name]
    
    # Allocation methods
    def allocate_VA_interval(self, size, alignment_bits=None, state=None, page_type=None):
        """Legacy method for allocating VA intervals"""
        current_state = state if state is not None else get_current_state()
        state_name = current_state.state_name
        
        # Ensure the state is initialized
        self._initialize_state(state_name)
        
        # Use the state's unmapped VA interval to allocate
        return self.state_unmapped_va_intervals[state_name].allocate(size, alignment_bits)
    
    def allocate_PA_interval(self, size, alignment_bits=None):
        """Legacy method for allocating PA intervals"""
        return self.unmapped_pa_intervals.allocate(size, alignment_bits)
    
    # Helper method to determine if a page type is code or data
    def _is_code_page_type(self, page_type):
        """Determine if a page type is code or data"""
        if page_type in [Configuration.Page_types.TYPE_CODE]:
            return True
        elif page_type in [Configuration.Page_types.TYPE_DATA, Configuration.Page_types.TYPE_DEVICE, Configuration.Page_types.TYPE_SYSTEM]:
            return False
        else:
            # Default to data for unknown types
            memory_log(f"Unknown page type {page_type}, treating as data", "warning")
            return False
    
    # New operations for memory mapping and allocation
    def map_va_to_pa(self, state_name, va_addr, pa_addr, size, page_type):
        """
        Maps a VA region to a PA region
        - Moves the region from unmapped to mapped and non-allocated
        - Does not allocate the memory
        
        :param state_name: State name
        :param va_addr: Virtual address to map
        :param pa_addr: Physical address to map
        :param size: Size of region in bytes
        :param page_type: Type of page (code, data, device, system)
        :return: Tuple of (va_addr, pa_addr, size)
        """
        # Ensure the state is initialized
        self._initialize_state(state_name)
        
        memory_log(f"Mapping VA:0x{va_addr:x} to PA:0x{pa_addr:x}, size:0x{size:x}, type:{page_type}")
        
        # Update unmapped/mapped PA intervals
        self.unmapped_pa_intervals.remove_region(pa_addr, size)
        self.mapped_pa_intervals.add_region(pa_addr, size)
        self.non_allocated_pa_intervals.add_region(pa_addr, size)  # Newly mapped memory is non-allocated
        
        # Update unmapped/mapped VA intervals for the state
        self.state_unmapped_va_intervals[state_name].remove_region(va_addr, size)
        self.state_mapped_va_intervals[state_name].add_region(va_addr, size)
        self.state_non_allocated_va_intervals[state_name].add_region(va_addr, size)  # Newly mapped memory is non-allocated
        
        # Update type-specific intervals
        is_code = self._is_code_page_type(page_type)
        if is_code:
            memory_log(f"Adding CODE region VA:0x{va_addr:x} to mapped and non-allocated pools")
            self.mapped_pa_code_intervals.add_region(pa_addr, size)
            self.non_allocated_pa_code_intervals.add_region(pa_addr, size)
            self.state_mapped_va_code_intervals[state_name].add_region(va_addr, size)
            self.state_non_allocated_va_code_intervals[state_name].add_region(va_addr, size)
            
        else:
            memory_log(f"Adding DATA region VA:0x{va_addr:x} to mapped and non-allocated pools")
            self.mapped_pa_data_intervals.add_region(pa_addr, size)
            self.non_allocated_pa_data_intervals.add_region(pa_addr, size)
            self.state_mapped_va_data_intervals[state_name].add_region(va_addr, size)
            self.state_non_allocated_va_data_intervals[state_name].add_region(va_addr, size)
                    
        # Record the mapping
        return (va_addr, pa_addr, size)
    
    def _find_va_eq_pa_addresses(self, state_name, size, page_type, alignment_bits=None, page_size=4096):
        """
        Find VA and PA addresses that satisfy the VA=PA constraint
        
        :return: (va_start, pa_start, overlapping_pages)
        """
        memory_log("Searching for matching VA and PA regions where VA=PA...")
        is_code = self._is_code_page_type(page_type)
        
        # Get the available regions for both VA and PA
        if is_code:
            va_intervals = self.state_non_allocated_va_code_intervals[state_name].free_intervals
            pa_intervals = self.non_allocated_pa_code_intervals.free_intervals
        else:
            va_intervals = self.state_non_allocated_va_data_intervals[state_name].free_intervals
            pa_intervals = self.non_allocated_pa_data_intervals.free_intervals
        
        # Find overlapping regions where VA can equal PA
        matching_regions = []
        for va_interval in va_intervals:
            va_start, va_size = va_interval
            for pa_interval in pa_intervals:
                pa_start, pa_size = pa_interval
                
                # Calculate the intersection of the VA and PA intervals
                # For VA=PA, we need addresses that are available in both spaces
                overlap_start = max(va_start, pa_start)
                overlap_end = min(va_start + va_size - 1, pa_start + pa_size - 1)
                
                if overlap_start <= overlap_end:
                    # There is an overlap
                    overlap_size = overlap_end - overlap_start + 1
                    if overlap_size >= size:
                        # This overlapping region is big enough
                        memory_log(f"Found matching region at 0x{overlap_start:x}, size: 0x{overlap_size:x}")
                        matching_regions.append((overlap_start, overlap_size))
        
        if not matching_regions:
            memory_log(f"Could not find any region where VA=PA is possible for size {size}", "error")
            raise ValueError(f"Could not find any region where VA=PA is possible for size {size}")
        
        # Apply alignment if needed
        aligned_regions = []
        if alignment_bits is not None:
            alignment = 1 << alignment_bits
            for region_start, region_size in matching_regions:
                # Calculate the aligned start address
                aligned_start = (region_start + alignment - 1) & ~(alignment - 1)
                if aligned_start + size <= region_start + region_size:
                    # The aligned region fits
                    aligned_regions.append((aligned_start, region_size - (aligned_start - region_start)))
        else:
            aligned_regions = matching_regions
            
        if not aligned_regions:
            memory_log(f"Could not find any aligned region where VA=PA is possible for size {size}", "error")
            raise ValueError(f"Could not find any aligned region where VA=PA is possible for size {size}")
            
        # Choose a random aligned region instead of always the first one
        if len(aligned_regions) > 1:
            chosen_idx = random.randrange(len(aligned_regions))
            memory_log(f"Multiple regions available, randomly selected region {chosen_idx} of {len(aligned_regions)}")
        else:
            chosen_idx = 0
            
        va_start, region_size = aligned_regions[chosen_idx]
        
        # Additionally, randomize the position within the chosen region
        if alignment_bits is not None:
            alignment = 1 << alignment_bits
            # Calculate how many alignment-sized blocks fit in the region
            max_blocks = (region_size - size) // alignment
            if max_blocks > 0:
                # Choose random aligned position
                random_blocks = random.randrange(max_blocks + 1)
                random_offset = random_blocks * alignment
                va_start += random_offset
                memory_log(f"Randomizing within region, chose offset 0x{random_offset:x} from base")
        else:
            # For unaligned allocations
            max_offset = region_size - size
            if max_offset > 0:
                random_offset = random.randrange(max_offset + 1)
                va_start += random_offset
                memory_log(f"Randomizing within region, chose offset 0x{random_offset:x} from base")
        
        pa_start = va_start  # Since VA=PA
        
        memory_log(f"Selected VA=PA region at address 0x{va_start:x}")
        
        # Now we need to check if this region is already mapped in the page tables
        # If it's not mapped, we'll need to create the mapping
        current_state = get_current_state()
        page_table_manager = current_state.page_table_manager
        
        # Check if the region is already mapped correctly
        va_end = va_start + size - 1
        page_entries = page_table_manager.get_page_table_entries()
        
        overlapping_pages = []
        for page in page_entries:
            if (page.va <= va_end and page.end_va >= va_start):
                overlapping_pages.append(page)
                
                # Check if the page has VA=PA mapping
                if page.va != page.pa:
                    memory_log(f"Existing page mapping doesn't satisfy VA=PA: VA=0x{page.va:x}, PA=0x{page.pa:x}", "error")
                    raise ValueError(f"Existing page mapping doesn't satisfy VA=PA: VA=0x{page.va:x}, PA=0x{page.pa:x}")
        
        # If no existing pages cover this region, create the mapping
        if not overlapping_pages:
            # We need to create the mapping from scratch
            memory_log(f"Creating new VA=PA mapping at 0x{va_start:x}")
            # Create pages as needed to cover the entire region
            current_va = va_start
            current_pa = pa_start
            remaining_size = size
            
            while remaining_size > 0:
                # Calculate the size for this page
                current_page_size = min(page_size, remaining_size)
                
                # Map the VA to the PA with VA=PA
                # THIS NEEDS TO CALL THE LOCAL map_va_to_pa METHOD, NOT page_table_manager's
                self.map_va_to_pa(current_state.state_name, current_va, current_pa, current_page_size, page_type)
                
                # Move to the next page
                current_va += current_page_size
                current_pa += current_page_size
                remaining_size -= current_page_size
                
            # Fetch the newly created pages
            page_entries = page_table_manager.get_page_table_entries()
            overlapping_pages = []
            for page in page_entries:
                if (page.va <= va_end and page.end_va >= va_start):
                    overlapping_pages.append(page)
                    
        return va_start, pa_start, overlapping_pages

    def _find_regular_addresses(self, state_name, size, page_type, alignment_bits=None, page_size=4096):
        """
        Find VA and PA addresses for regular allocation (not VA=PA)
        
        :return: (va_start, pa_start, overlapping_pages)
        """
        is_code = self._is_code_page_type(page_type)
        
        # Debug: Check what's in the non-allocated pools
        if is_code:
            code_intervals = self.state_non_allocated_va_code_intervals[state_name].free_intervals
            memory_log(f"Looking for CODE region of size {size}. Available {len(code_intervals)} code regions:")
            for i, interval in enumerate(code_intervals):
                int_start, int_size = interval
                memory_log(f"  Code region {i}: VA:0x{int_start:x}-0x{int_start+int_size-1:x}, size:0x{int_size:x}")
                
            # Find available non-allocated VA region from the CODE pool only, with alignment
            va_avail = self.state_non_allocated_va_code_intervals[state_name].find_region(size, alignment_bits)
            if not va_avail:
                raise ValueError(f"No available non-allocated CODE VA region of size {size} with alignment {alignment_bits} for state {state_name}")
        else:
            data_intervals = self.state_non_allocated_va_data_intervals[state_name].free_intervals
            memory_log(f"Looking for DATA region of size {size}. Available {len(data_intervals)} data regions:")
            for i, interval in enumerate(data_intervals):
                int_start, int_size = interval
                memory_log(f"  Data region {i}: VA:0x{int_start:x}-0x{int_start+int_size-1:x}, size:0x{int_size:x}")
                
            # Find available non-allocated VA region from the DATA pool only, with alignment
            va_avail = self.state_non_allocated_va_data_intervals[state_name].find_region(size, alignment_bits)
            if not va_avail:
                memory_log(f"No available non-allocated DATA VA region of size {size} with alignment {alignment_bits} for state {state_name}", "error")
                raise ValueError(f"No available non-allocated DATA VA region of size {size} with alignment {alignment_bits} for state {state_name}")
        
        va_start, _ = va_avail
        memory_log(f"Found suitable VA region starting at 0x{va_start:x}")
        
        # Check that the region is properly aligned
        if alignment_bits is not None:
            alignment = 1 << alignment_bits
            if va_start % alignment != 0:
                memory_log(f"VA address 0x{va_start:x} is not aligned to {alignment_bits} bits!", "error")
                raise ValueError(f"Failed to allocate properly aligned memory. VA:0x{va_start:x} is not aligned to {alignment_bits} bits!")
        
        # Find the physical address that corresponds to the VA we just found
        # Retrieve the page table entries from the current state
        current_state = get_current_state()
        page_table_manager = current_state.page_table_manager
        page_entries = page_table_manager.get_page_table_entries()
        
        # Find the page that contains this VA
        matching_page = None
        overlapping_pages = []
        va_end = va_start + size - 1
        
        # First, find all pages that overlap with this segment
        for page in page_entries:
            # Check if the page overlaps with any part of our segment
            if (page.va <= va_end and page.end_va >= va_start):
                overlapping_pages.append(page)
        
        # Sort pages by VA for easier sequential checking
        overlapping_pages.sort(key=lambda p: p.va)
        
        if overlapping_pages:
            memory_log(f"Found {len(overlapping_pages)} pages overlapping with segment VA:0x{va_start:x}-0x{va_end:x}")
            
            # Check if pages are sequential without gaps
            is_sequential = True
            covered_range_start = max(overlapping_pages[0].va, va_start)
            covered_range_end = min(overlapping_pages[0].end_va, va_end)
            
            for i in range(1, len(overlapping_pages)):
                prev_page = overlapping_pages[i-1]
                curr_page = overlapping_pages[i]
                
                # Check for a gap between pages
                if prev_page.end_va + 1 != curr_page.va:
                    memory_log(f"Gap detected between pages: {prev_page} and {curr_page}")
                    is_sequential = False
                    break
                
                # Update covered range
                if curr_page.va <= va_end:
                    covered_range_end = min(curr_page.end_va, va_end)
            
            # Verify the pages fully cover our segment
            if covered_range_start <= va_start and covered_range_end >= va_end and is_sequential:
                memory_log(f"Pages provide complete sequential coverage for the segment")
                
                # Calculate the physical address for the start of our segment
                # Find which page contains our VA start
                containing_page = None
                for page in overlapping_pages:
                    if page.va <= va_start <= page.end_va:
                        containing_page = page
                        break
                
                if containing_page:
                    # Calculate the offset into the page
                    offset = va_start - containing_page.va
                    # Apply the same offset to get the correct PA
                    pa_start = containing_page.pa + offset
                    memory_log(f"Found corresponding PA for VA:0x{va_start:x} -> PA:0x{pa_start:x} in page {containing_page}")
                    
                    # Verify PA alignment matches VA alignment
                    if alignment_bits is not None:
                        alignment = 1 << alignment_bits
                        if pa_start % alignment != 0:
                            memory_log(f"PA address 0x{pa_start:x} is not aligned to {alignment_bits} bits!", "error")
                            raise ValueError(f"Failed to allocate properly aligned memory. PA:0x{pa_start:x} is not aligned to {alignment_bits} bits!")
                    
                    # Verify physical addresses are sequential by checking each page boundary
                    if len(overlapping_pages) > 1:
                        for i in range(len(overlapping_pages) - 1):
                            curr_page = overlapping_pages[i]
                            next_page = overlapping_pages[i+1]
                            
                            # Calculate expected PA at the boundary
                            pa_at_boundary = curr_page.pa + (curr_page.end_va - curr_page.va)
                            
                            # Check if next page's PA follows sequentially
                            if pa_at_boundary + 1 != next_page.pa:
                                memory_log(f"Physical memory is not sequential between pages: "
                                             f"PA 0x{pa_at_boundary:x} -> 0x{next_page.pa:x}", "warning")
                                # We'll continue anyway since VA is what matters for allocation
                else:
                    memory_log(f"Failed to find the specific page containing VA start 0x{va_start:x}", "error")
                    raise ValueError(f"Internal error: couldn't identify page containing VA start")
            else:
                if not is_sequential:
                    memory_log(f"Pages are not sequential, cannot allocate segment", "error")
                else:
                    memory_log(f"Pages don't fully cover segment VA:0x{va_start:x}-0x{va_end:x}, "
                               f"covered: 0x{covered_range_start:x}-0x{covered_range_end:x}", "error")
                # Fall back to the error case below
                overlapping_pages = []
                
        if not overlapping_pages:
            # If we can't find the page entries (shouldn't happen with proper page management)
            # fall back to the original logic as a last resort
            memory_log(f"CRITICAL ERROR: Cannot find pages covering VA:0x{va_start:x}-0x{va_end:x}. Page table may be inconsistent!", "error")
            raise ValueError(f"CRITICAL ERROR: Cannot find pages covering VA:0x{va_start:x}-0x{va_end:x}. Page table may be inconsistent!")
            if is_code:
                pa_avail = self.non_allocated_pa_code_intervals.find_region(size, alignment_bits)
                if not pa_avail:
                    raise ValueError(f"No available non-allocated CODE PA region of size {size} with alignment {alignment_bits}")
            else:
                pa_avail = self.non_allocated_pa_data_intervals.find_region(size, alignment_bits)
                if not pa_avail:
                    raise ValueError(f"No available non-allocated DATA PA region of size {size} with alignment {alignment_bits}")
            pa_start, _ = pa_avail
            memory_log(f"Using fallback PA allocation: 0x{pa_start:x}. THIS IS LIKELY INCORRECT!", "warning")
            
        memory_log(f"Using PA region starting at 0x{pa_start:x}")
        
        return va_start, pa_start, overlapping_pages


    def allocate_memory(self, state_name, size, page_type, alignment_bits=None, VA_eq_PA=False, page_size=4096):
        """
        Allocates memory from mapped but non-allocated regions
        - Can allocate cross-page regions if pages are sequential
        - Returns allocation information
        
        :param state_name: State name or State object
        :param size: Size in bytes to allocate
        :param page_type: Page type to allocate
        :param alignment_bits: Alignment in bits (default: None)
        :param VA_eq_PA: If True, the virtual address must equal the physical address (default: False)
        :param page_size: Page size in bytes (default: 4096)
        :return: MemoryAllocation object
        """
        # Handle both state objects and state names
        if hasattr(state_name, 'state_name'):
            state_name = state_name.state_name
            
        # Ensure the state is initialized
        self._initialize_state(state_name)
        
        memory_log(f"Allocating memory of size {size} for state {state_name} with page_type {page_type}, "
                   f"alignment_bits={alignment_bits}, VA_eq_PA={VA_eq_PA}")
        
        # Determine if we're allocating code or data
        is_code = self._is_code_page_type(page_type)
        
        # Find suitable VA and PA addresses based on allocation type
        if VA_eq_PA:
            va_start, pa_start, overlapping_pages = self._find_va_eq_pa_addresses(
                state_name, size, page_type, alignment_bits, page_size)
        else:
            va_start, pa_start, overlapping_pages = self._find_regular_addresses(
                state_name, size, page_type, alignment_bits, page_size)
            
        # From here on, the logic is the same for both allocation types
        # Mark as allocated (add to allocated, remove from non-allocated)
        self.state_allocated_va_intervals[state_name].add_region(va_start, size)
        self.state_non_allocated_va_intervals[state_name].remove_region(va_start, size)
        
        self.allocated_pa_intervals.add_region(pa_start, size)
        self.non_allocated_pa_intervals.remove_region(pa_start, size)
        
        # Update type-specific allocation tracking
        if is_code:
            self.state_non_allocated_va_code_intervals[state_name].remove_region(va_start, size)
            self.non_allocated_pa_code_intervals.remove_region(pa_start, size)
        else:
            self.state_non_allocated_va_data_intervals[state_name].remove_region(va_start, size)
            self.non_allocated_pa_data_intervals.remove_region(pa_start, size)
        
        # Create page mappings list for cross-page allocations
        page_mappings = []
        for offset in range(0, size, page_size):
            if offset + page_size <= size:
                page_size_to_add = page_size
            else:
                page_size_to_add = size - offset
                
            va_page = va_start + offset
            pa_page = pa_start + offset
            page_mappings.append((va_page, pa_page, page_size_to_add))
        
        # Create MemoryAllocation object with all the details
        allocation = MemoryAllocation(
            va_start=va_start,
            pa_start=pa_start,
            size=size,
            page_mappings=page_mappings,
            page_type=page_type,
            covered_pages=overlapping_pages
        )
        
        # Debug information
        if VA_eq_PA:
            memory_log(f"Created VA=PA allocation: VA=PA=0x{va_start:x}, size={size}")
        else:
            memory_log(f"Created allocation: VA=0x{va_start:x}, PA=0x{pa_start:x}, size={size}")
        
        self.allocations.append(allocation)
        return allocation


    # def allocate_data_memory_from_given_page(self, page, state_name, byte_size, alignment_bits=None, va_start=None):
    #     """
    #     Allocates data memory from mapped but non-allocated regions, from a given page.
    #     If va_start is provided, tries to allocate exactly at that address.
        
    #     :param page: The page to allocate from
    #     :param state_name: State name or object 
    #     :param byte_size: Size in bytes to allocate
    #     :param alignment_bits: Alignment requirements in bits
    #     :param va_start: Specific virtual address to start allocation (if None, one is chosen randomly)
    #     :return: MemoryAllocation object
    #     """
    #     # Handle both state objects and state names
    #     if hasattr(state_name, 'state_name'):
    #         state_name = state_name.state_name
        
    #     memory_log(f"Allocating data memory of size {byte_size} from page {page} in state {state_name}")
        
    #     all_non_allocated_data_intervals = self.state_non_allocated_va_data_intervals[state_name]
    #     # Find intervals that are fully or partially within the page
    #     contained_intervals = []
    #     for interval in all_non_allocated_data_intervals.free_intervals:
    #         int_start, int_size = interval
    #         int_end = int_start + int_size - 1
    #         memory_log(f"Checking interval: VA:{hex(int_start)}-{hex(int_end)}, size:0x{int_size:x}")
            
    #         # Calculate intersection with page
    #         if int_end >= page.va and int_start <= page.va+page.size-1:
    #             # There is some overlap - calculate the contained portion
    #             contained_start = max(int_start, page.va)
    #             contained_end = min(int_end, page.va+page.size-1)
    #             contained_size = contained_end - contained_start + 1
                
    #             contained_intervals.append((contained_start, contained_size))
    #             memory_log(f"Found contained interval: VA:{hex(contained_start)}-{hex(contained_end)}, size:0x{contained_size:x}")
        
    #     if len(contained_intervals) == 0:
    #         memory_log(f"No contained interval found in state {state_name}", level="error")
    #         raise ValueError(f"No contained interval found in state {state_name}")
        
    #     memory_log(f"Available intervals before allocation:")
    #     for i, interval in enumerate(contained_intervals):
    #         int_start, int_size = interval  
    #         memory_log(f"  interval {i}: VA:{hex(int_start)}-{hex(int_start+int_size-1)}, size:0x{int_size:x}")

    #     # If va_start is provided, use that specific address instead of randomly selecting an interval
    #     if va_start is not None:
    #         va_start_end = va_start + byte_size - 1
    #         memory_log(f"Attempting to allocate fixed interval VA:{hex(va_start)}-{hex(va_start_end)}, size:0x{byte_size:x}")
            
    #         # Check if the requested interval is within the page
    #         if va_start < page.va or va_start_end > page.va + page.size - 1:
    #             memory_log(f"Requested interval VA:{hex(va_start)}-{hex(va_start_end)} is not fully contained in page VA:{hex(page.va)}-{hex(page.va+page.size-1)}", level="error")
    #             raise ValueError(f"Requested interval is not fully contained in the specified page")
            
    #         # Check if the requested interval is available (not allocated)
    #         is_available = False
    #         for int_start, int_size in contained_intervals:
    #             if (va_start >= int_start) and (va_start_end <= int_start + int_size - 1):
    #                 is_available = True
    #                 break
            
    #         if not is_available:
    #             memory_log(f"Requested interval VA:{hex(va_start)}-{hex(va_start_end)} is not available for allocation", level="error")
    #             raise ValueError(f"Requested interval VA:{hex(va_start)}-{hex(va_start_end)} is not available for allocation")
            
    #         # Check alignment if specified
    #         if alignment_bits is not None:
    #             alignment = 1 << alignment_bits
    #             if va_start % alignment != 0:
    #                 memory_log(f"Requested address 0x{va_start:x} is not aligned to {alignment_bits} bits", level="error")
    #                 raise ValueError(f"Requested address 0x{va_start:x} is not aligned to {alignment_bits} bits")
            
    #         interval_start = va_start
    #         chosen_start = va_start
    #     else:
    #         # Original random selection logic when no fixed address is provided
    #         selected_interval = random.choice(contained_intervals)
    #         memory_log(f"Selected interval: VA:{hex(selected_interval[0])}-{hex(selected_interval[0]+selected_interval[1]-1)}, size:0x{selected_interval[1]:x}")

    #         interval_start, interval_size = selected_interval

    #         # find a valid interval space, based on given size and alignment, in the given interval
    #         alignment = 1 if alignment_bits is None else (1 << alignment_bits)
            
    #         # Calculate the maximum possible start address to ensures the sub-interval fits entirely in the larger interval
    #         max_start = interval_start + interval_size - byte_size
            
    #         # Calculate the minimum aligned start address - Round up interval_start to the next aligned address
    #         min_start = (interval_start + alignment - 1) & ~(alignment - 1)
            
    #         # Check if there's still room after alignment
    #         if min_start > max_start:
    #             raise ValueError(f"No valid interval found in the given interval")
            
    #         # Calculate how many aligned positions are available
    #         if alignment > 1:
    #             # For aligned addresses, we need to calculate how many alignment-sized steps fit between min_start and max_start
    #             available_positions = ((max_start - min_start) // alignment) + 1
                
    #             # Choose a random position
    #             if available_positions == 1:
    #                 chosen_start = min_start
    #             else:
    #                 random_offset = random.randrange(0, available_positions) * alignment
    #                 chosen_start = min_start + random_offset
    #         else:
    #             # No alignment required, any position between min_start and max_start is valid
    #             chosen_start = random.randint(min_start, max_start)
        
    #     va_start = chosen_start
    #     pa_start = page.pa + (va_start - page.va)
            
    #     # Mark as allocated (add to allocated, remove from non-allocated)
    #     self.state_allocated_va_intervals[state_name].add_region(va_start, byte_size)
    #     self.state_non_allocated_va_intervals[state_name].remove_region(va_start, byte_size)
        
    #     self.allocated_pa_intervals.add_region(pa_start, byte_size)
    #     self.non_allocated_pa_intervals.remove_region(pa_start, byte_size)
        
    #     # Update type-specific allocation tracking
    #     self.state_non_allocated_va_data_intervals[state_name].remove_region(va_start, byte_size)
    #     self.non_allocated_pa_data_intervals.remove_region(pa_start, byte_size)
        
    #     # Create MemoryAllocation object with all the details
    #     allocation = MemoryAllocation(
    #         va_start=va_start,
    #         pa_start=pa_start,
    #         size=byte_size,
    #         page_mappings=[page],
    #         page_type=Configuration.Page_types.TYPE_DATA,
    #         covered_pages=[page]
    #     )
        
    #     memory_log(f"Created allocation: VA=0x{va_start:x}, PA=0x{pa_start:x}, size={byte_size}")
        
    #     self.allocations.append(allocation)
    #     return allocation







    def free_memory(self, allocation):
        """
        Frees previously allocated memory
        - Keeps the mapping, just moves from allocated to non-allocated
        """
        
        # Find the state that owns this allocation (use current state if not found)
        state_name = get_current_state().state_name
        for s_name in self.state_allocated_va_intervals:
            if self.state_allocated_va_intervals[s_name].is_region_available(allocation.va_start, allocation.size):
                state_name = s_name
                break
        
        # Ensure the state is initialized
        self._initialize_state(state_name)
        
        # Move from allocated to non-allocated
        self.state_allocated_va_intervals[state_name].remove_region(allocation.va_start, allocation.size)
        self.state_non_allocated_va_intervals[state_name].add_region(allocation.va_start, allocation.size)
        
        self.allocated_pa_intervals.remove_region(allocation.pa_start, allocation.size)
        self.non_allocated_pa_intervals.add_region(allocation.pa_start, allocation.size)
        
        # Update type-specific pools
        is_code = self._is_code_page_type(allocation.page_type)
        if is_code:
            self.state_non_allocated_va_code_intervals[state_name].add_region(allocation.va_start, allocation.size)
            self.non_allocated_pa_code_intervals.add_region(allocation.pa_start, allocation.size)
        else:
            self.state_non_allocated_va_data_intervals[state_name].add_region(allocation.va_start, allocation.size)
            self.non_allocated_pa_data_intervals.add_region(allocation.pa_start, allocation.size)
        
        # Remove allocation record
        if allocation in self.allocations:
            self.allocations.remove(allocation)
        
        memory_log(f"Freed memory at VA:0x{allocation.va_start:x}, PA:0x{allocation.pa_start:x}, size:{allocation.size}")
        return True
    
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
        state_manager = get_state_manager()
        
        memory_log("\n")
        memory_log("==== MEMORY ALLOCATION SUMMARY ====")
        
        # First, print summary of PA space
        total_pa_mapped = len(self.mapped_pa_intervals.free_intervals)
        total_pa_allocated = len(self.allocated_pa_intervals.free_intervals)
        total_pa_code = len(self.mapped_pa_code_intervals.free_intervals)
        total_pa_data = len(self.mapped_pa_data_intervals.free_intervals)
        
        memory_log(f"Physical Address Space:")
        memory_log(f"  Total mapped regions: {total_pa_mapped} ({total_pa_code} code, {total_pa_data} data)")
        memory_log(f"  Total allocated regions: {total_pa_allocated}")
        
        if verbose:
            # Print detailed PA intervals using utility function
            print_intervals_summary("Code", self.mapped_pa_code_intervals, verbose)
            print_intervals_summary("Data", self.mapped_pa_data_intervals, verbose)
        
        # Then print per-state information
        for state_name, state in state_manager.states_dict.items():
            if state_name not in self.state_mapped_va_intervals:
                memory_log(f"State {state_name}: No memory initialized")
                continue
                
            total_va_mapped = len(self.state_mapped_va_intervals[state_name].free_intervals)
            total_va_allocated = len(self.state_allocated_va_intervals[state_name].free_intervals)
            total_va_code = len(self.state_mapped_va_code_intervals[state_name].free_intervals)
            total_va_data = len(self.state_mapped_va_data_intervals[state_name].free_intervals)
            
            memory_log(f"\nState {state_name}:")
            memory_log(f"  Virtual Address Space:")
            memory_log(f"    Total mapped regions: {total_va_mapped} ({total_va_code} code, {total_va_data} data)")
            memory_log(f"    Total allocated regions: {total_va_allocated}")
            
            # Get page table entries if available
            if hasattr(state, 'page_table_manager'):
                page_table_entries = state.page_table_manager.get_page_table_entries()
                memory_log(f"    Page Table Entries: {len(page_table_entries)}")
                
                if verbose:
                    # Use utility function to print pages by type
                    print_pages_by_type(page_table_entries, "    ", verbose)
            
            # Print information about allocations in this state
            state_allocations = [a for a in self.allocations 
                               if self.state_allocated_va_intervals[state_name].is_region_available(a.va_start, a.size)]
            
            # Use utility function to print allocations
            print_allocation_summary(state_allocations, "    ", verbose)
        
        memory_log("==== END MEMORY SUMMARY ====")

    def force_initialize_state(self, state_name):
        """Force initialization of a specific state"""
        memory_log(f"Force initializing state: {state_name}")
        self._initialize_state(state_name)


# Factory function to retrieve the MemorySpaceManager instance
def get_memory_space_manager():
    # Access or initialize the singleton variable
    memory_space_manager_instance = SingletonManager.get("memory_space_manager_instance", default=None)
    if memory_space_manager_instance is None:
        memory_space_manager_instance = MemorySpaceManager()
        SingletonManager.set("memory_space_manager_instance", memory_space_manager_instance)
    return memory_space_manager_instance