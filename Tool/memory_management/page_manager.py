import random
from typing import List, Dict

from Utils.configuration_management import Configuration, get_config_manager
from Utils.logger_management import get_logger
from Tool.state_management import get_current_state, get_state_manager

from Tool.memory_management.memory_space_manager import get_memory_space_manager
from Tool.memory_management.memory_segments import MemoryRange
from Tool.memory_management.memory_page import Page
from Tool.memory_management import interval_lib
from Tool.memory_management.utils import memory_log


class PageTableManager:
    '''
    PageTableManager
    VA Space Management: Track and allocate virtual address ranges
    Page Table Generation: Create and maintain page table structures
    Mapping Operations: Create VA→PA mappings with attributes
    MMU Configuration: Generate register values (TTBR, TCR, MAIR)
    Attribute Management: Support different memory permissions/cacheability
    '''

    def __init__(self):
        logger = get_logger()
        logger.info("==================== PageTableManager")

        self.page_table_entries = []
        # Initialize dictionary with all possible page types
        self.page_table_entries_by_type = {
            Configuration.Page_types.TYPE_CODE: [],
            Configuration.Page_types.TYPE_DATA: [],
            Configuration.Page_types.TYPE_DEVICE: [],
            Configuration.Page_types.TYPE_SYSTEM: []
        }

    def _find_va_eq_pa_unmapped_region(self, memory_space_manager, current_state, state_name, size_bytes, alignment_bits, page_type):
        """
        Find a region that is available at the same address in both VA and PA unmapped spaces
        
        Returns: (va_start, pa_start, size) - where va_start == pa_start
        """
        memory_log(f"Searching for unmapped region where VA=PA is possible, size: {size_bytes}, alignment: {alignment_bits}")
        
        # Get the unmapped VA and PA intervals
        va_intervals = memory_space_manager.state_unmapped_va_intervals[state_name].free_intervals
        pa_intervals = memory_space_manager.unmapped_pa_intervals.free_intervals
        
        memory_log(f"Found {len(va_intervals)} unmapped VA regions and {len(pa_intervals)} unmapped PA regions")
        
        # Find overlapping regions where VA can equal PA
        matching_regions = []
        for va_interval in va_intervals:
            va_start, va_size = va_interval
            for pa_interval in pa_intervals:
                pa_start, pa_size = pa_interval
                
                # Calculate the intersection of the VA and PA intervals
                # For VA=PA, we need the same address to be available in both spaces
                overlap_start = max(va_start, pa_start)
                overlap_end = min(va_start + va_size - 1, pa_start + pa_size - 1)
                
                if overlap_start <= overlap_end:
                    # There is an overlap
                    overlap_size = overlap_end - overlap_start + 1
                    if overlap_size >= size_bytes:
                        # This overlapping region is big enough
                        #memory_log(f"Found matching unmapped region at 0x{overlap_start:x}, size: 0x{overlap_size:x}")
                        matching_regions.append((overlap_start, overlap_size))
        
        if not matching_regions:
            memory_log(f"Could not find any unmapped region where VA=PA is possible for size {size_bytes}", "error")
            raise ValueError(f"Could not find any unmapped region where VA=PA is possible for size {size_bytes}")
        
        # Apply alignment if needed
        aligned_regions = []
        if alignment_bits is not None:
            alignment = 1 << alignment_bits
            for region_start, region_size in matching_regions:
                # Calculate the aligned start address
                aligned_start = (region_start + alignment - 1) & ~(alignment - 1)
                if aligned_start + size_bytes <= region_start + region_size:
                    # The aligned region fits
                    aligned_regions.append((aligned_start, aligned_start, size_bytes))
        else:
            # No alignment needed, just use the start of each region
            aligned_regions = [(start, start, size_bytes) for start, size in matching_regions]
                
        if not aligned_regions:
            memory_log(f"Could not find any aligned unmapped region where VA=PA is possible for size {size_bytes}", "error")
            raise ValueError(f"Could not find any aligned unmapped region where VA=PA is possible for size {size_bytes}")
        
        # Choose the first matching region
        va_start, pa_start, region_size = aligned_regions[0]
        memory_log(f"Selected VA=PA unmapped region at address 0x{va_start:x} (VA=PA), size: {region_size}")
        
        return va_start, pa_start, region_size

    def allocate_page(self, size:Configuration.Page_sizes=None, alignment_bits:int=None, page_type:Configuration.Page_types=None, permissions:int=None, cacheable:str=None, shareable:str=None, security:str=None, custom_attributes:dict=None, sequential_page_count:int=1, VA_eq_PA:bool=False):
        memory_log("\n")
        memory_log("======================== PageTableManager - allocate_page")
        memory_log(f"==== size: {size}, alignment_bits: {alignment_bits}, page_type: {page_type}, permissions: {permissions}, cacheable: {cacheable}, shareable: {shareable}, security: {security}, custom_attributes: {custom_attributes}, sequential_page_count: {sequential_page_count}, VA_eq_PA: {VA_eq_PA}")

        if size is None:
            size = random.choice([Configuration.Page_sizes.SIZE_4K, Configuration.Page_sizes.SIZE_2M])#, Configuration.Page_sizes.SIZE_1G])
        else:
            if size not in [Configuration.Page_sizes.SIZE_4K, Configuration.Page_sizes.SIZE_2M]:#, Configuration.Page_sizes.SIZE_1G]:
                raise ValueError(f"Size must be 4KB or 2MB. {size} is not valid. 1GB is still not supported.")

        #For a 4 KB page size, you need 12-bit alignment (i.e., addresses must be aligned to 2^12 bytes).
        #For a 2 MB page size, you need 21-bit alignment (i.e., addresses must be aligned to 2^21 bytes).
        #For a 1 GB page size, you need 30-bit alignment (i.e., addresses must be aligned to 2^30 bytes).
        if alignment_bits is None:
            if size == Configuration.Page_sizes.SIZE_4K:
                alignment_bits = 12
            elif size == Configuration.Page_sizes.SIZE_2M:
                alignment_bits = 21
            elif size == Configuration.ByteSize.SIZE_1G.in_bytes():
                alignment_bits = 30
        else:
            if size == Configuration.Page_sizes.SIZE_4K and alignment_bits < 12:
                raise ValueError(f"4KB page size requires at least 12-bit alignment. {alignment_bits} is not valid.")
            elif size == Configuration.Page_sizes.SIZE_2M and alignment_bits < 21:
                raise ValueError(f"2MB page size requires at least 21-bit alignment. {alignment_bits} is not valid.")
            elif size == Configuration.Page_sizes.SIZE_1G and alignment_bits < 30:
                raise ValueError(f"1GB page size requires at least 30-bit alignment. {alignment_bits} is not valid.")

        if page_type is None:
            raise ValueError("page_type is required")
        if permissions is None:
            permissions = Page.PERM_READ | Page.PERM_WRITE | Page.PERM_EXECUTE
        if cacheable is None:
            cacheable = Page.CACHE_WB
        if shareable is None:
            shareable = Page.SHARE_NONE
        if security is None:
            security = "non-secure"
        if custom_attributes is None:
            custom_attributes = {}

        if sequential_page_count > 1:
            full_size = size.value * sequential_page_count
        else:
            full_size = size.value
            
        # Convert enum sizes to integers for interval operations
        # Explicit conversion to handle all possible cases
        if isinstance(size, Configuration.Page_sizes):
            # Access the Enum value directly
            size_bytes = size.value
        else:
            size_bytes = size  # Assume it's already an integer
            
        if sequential_page_count > 1:
            full_size_bytes = size_bytes * sequential_page_count
        else:
            full_size_bytes = size_bytes
            
        # Get current state and memory space manager
        memory_space_manager = get_memory_space_manager()
        current_state = get_current_state()
        state_name = current_state.state_name
        
        # Step 1: Find and allocate regions from unmapped space
        try:
            if VA_eq_PA:
                memory_log(f"Allocating unmapped memory with VA=PA constraint, size: {full_size_bytes}, alignment: {alignment_bits}")
                
                # Find a region that is available at the same address in both VA and PA unmapped spaces
                va_start, pa_start, size = self._find_va_eq_pa_unmapped_region(
                    memory_space_manager, 
                    current_state, 
                    state_name, 
                    full_size_bytes, 
                    alignment_bits, 
                    page_type
                )
                
                # Allocate the region from unmapped space
                # First, update the unmapped intervals
                memory_space_manager.state_unmapped_va_intervals[state_name].remove_region(va_start, size)
                memory_space_manager.unmapped_pa_intervals.remove_region(pa_start, size)
                
                # Map the VA to PA with equal addresses
                memory_space_manager.map_va_to_pa(state_name, va_start, pa_start, size, page_type)
                
                va_size = size
                memory_log(f"Successfully allocated and mapped VA=PA memory at 0x{va_start:x}, size: {size}")
                
            else:
                # Original implementation for non-VA_eq_PA case
                # Use the allocate_VA_interval and allocate_PA_interval methods which handle state initialization
                va_allocation = memory_space_manager.allocate_VA_interval(full_size_bytes, alignment_bits=alignment_bits, state=current_state, page_type=page_type)
                pa_allocation = memory_space_manager.allocate_PA_interval(full_size_bytes, alignment_bits=alignment_bits)
                
                va_start, va_size = va_allocation
                pa_start, pa_size = pa_allocation
                
                # Step 2: Add the allocated regions to mapped pools
                # First, add to mapped intervals pool, specifying the page type
                memory_space_manager.map_va_to_pa(state_name, va_start, pa_start, va_size, page_type)
                
        except (ValueError, MemoryError) as e:
            memory_log(f"Failed to allocate page memory: {e}", level="error")
            raise ValueError(f"Could not allocate memory regions of size {full_size_bytes} with alignment {alignment_bits}")
        
        # Create the page objects for each page in the sequence
        result = []
        for i in range(sequential_page_count):
            page = Page(
                va=va_start + i * size_bytes, 
                pa=pa_start + i * size_bytes, 
                size=size_bytes, 
                page_type=page_type, 
                permissions=permissions, 
                cacheable=cacheable, 
                shareable=shareable, 
                security=security, 
                custom_attributes=custom_attributes
            )
            
            # Add to our tracking collections
            self.page_table_entries.append(page)
            self.page_table_entries_by_type[page.page_type].append(page)
            result.append(page)
            
            memory_log(f"Created page: {page}")
            
        # Return result based on sequential_page_count
        if sequential_page_count == 1:
            return result[0]  
        else:
            return result


    def allocate_cross_core_page(self):
        memory_log("\n")
        memory_log("======================== PageTableManager - allocate_cross_core_page")

        # from the cross_core_page all is hard-coded for now. TODO:: consider making it configurable in the future.
        size = Configuration.Page_sizes.SIZE_2M # setting big space, as this pages can also be used for non-cross segments 

        if size == Configuration.Page_sizes.SIZE_4K:
            alignment_bits = 12
        elif size == Configuration.Page_sizes.SIZE_2M:
            alignment_bits = 21
        elif size == Configuration.ByteSize.SIZE_1G.in_bytes():
            alignment_bits = 30

        page_type = Configuration.Page_types.TYPE_DATA
        permissions = Page.PERM_READ | Page.PERM_WRITE | Page.PERM_EXECUTE
        cacheable = Page.CACHE_WB
        shareable = Page.SHARE_NONE
        security = "non-secure"
        custom_attributes = {}

        memory_log(f"==== size: {size}, alignment_bits: {alignment_bits}, page_type: {page_type}, permissions: {permissions}, cacheable: {cacheable}, shareable: {shareable}, security: {security}, custom_attributes: {custom_attributes}")

        size_bytes = size.value

        # Get current state and memory space manager
        memory_space_manager = get_memory_space_manager()
        state_manager = get_state_manager()

        
        try:
              # Step 1: Find and allocate regions from unmapped space
            pa_allocation = memory_space_manager.allocate_PA_interval(size_bytes, alignment_bits=alignment_bits)
            pa_start, pa_size = pa_allocation

            orig_state = state_manager.get_active_state()
            for state in state_manager.states_dict:
                state_manager.set_active_state(state)
                curr_state = state_manager.get_active_state()
                state_name = curr_state.state_name

                va_allocation = memory_space_manager.allocate_VA_interval(size_bytes, alignment_bits=alignment_bits, state=curr_state, page_type=page_type)
                va_start, va_size = va_allocation
            
                # Step 2: Add the allocated regions to mapped pools
                # First, add to mapped intervals pool, specifying the page type
                memory_space_manager.map_va_to_pa(state_name, va_start, pa_start, va_size, page_type)
                
                # Create the page objects for each page in the sequence
                page = Page(
                    va=va_start, 
                    pa=pa_start, 
                    size=size_bytes, 
                    page_type=page_type, 
                    permissions=permissions, 
                    cacheable=cacheable, 
                    shareable=shareable, 
                    security=security, 
                    custom_attributes=custom_attributes,
                    is_cross_core=True
                )

                # Add to our tracking collections
                current_page_table_manager = curr_state.page_table_manager
                current_page_table_manager.page_table_entries.append(page)
                current_page_table_manager.page_table_entries_by_type[page.page_type].append(page)
                
                # self.page_table_entries.append(page)
                # self.page_table_entries_by_type[page.page_type].append(page)
                
                memory_log(f"Created Cross-Core page {curr_state.state_name}: {page}")

            state_manager.set_active_state(orig_state.state_name)

        except (ValueError, MemoryError) as e:
            memory_log(f"Failed to allocate page memory: {e}", level="error")
            raise ValueError(f"Could not allocate memory regions of size {size} with alignment {alignment_bits}")
        
           
    def get_page_table_entries(self):
        return self.page_table_entries
        
    def get_page_table_entries_by_type(self, type):
        return self.page_table_entries_by_type[type]
    
    def print_page_tables(self):
        current_state = get_current_state()
        memory_log(f"==================== PageTableManager - print_page_tables {current_state.state_name}")
        for page in self.page_table_entries:
            memory_log(f"Page: {page}")
    