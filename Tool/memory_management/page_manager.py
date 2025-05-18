import random
from typing import List, Dict

from Utils.configuration_management import Configuration, get_config_manager
from Utils.logger_management import get_logger
from Tool.state_management import get_current_state

from Tool.memory_management.memory_space_manager import get_memory_space_manager
from Tool.memory_management.memory_segments import MemoryRange
from Tool.memory_management import interval_lib
from Tool.memory_management.utils import memory_log

class Page:
    """Represents a single page mapping in the page table"""
    
    
    # Permission flags
    PERM_READ = 0x1
    PERM_WRITE = 0x2
    PERM_EXECUTE = 0x4
    
    # Cacheability options
    CACHE_NONE = "non-cacheable"
    CACHE_WT = "write-through"
    CACHE_WB = "write-back"
    
    # Shareability domains
    SHARE_NONE = "non-shareable"
    SHARE_INNER = "inner-shareable"
    SHARE_OUTER = "outer-shareable"
    
    def __init__(self, va, pa, size, page_type=Configuration.Page_types, permissions=PERM_READ, 
                 cacheable=CACHE_WB, shareable=SHARE_NONE, security="non-secure", 
                 custom_attributes=None):
        """
        Initialize a page mapping with detailed memory attributes.
        
        Args:
            va (int): Virtual address of the page
            pa (int): Physical address of the page
            size (int): Size of the page in bytes
            page_type (str): Type of memory (code, data, device, system)
            permissions (int): Combination of PERM_READ, PERM_WRITE, PERM_EXECUTE
            cacheable (str): Cacheability setting
            shareable (str): Shareability domain
            security (str): Security state (secure, non-secure, realm)
            custom_attributes (dict): Any additional custom attributes
        """
        self.va = va
        self.pa = pa
        self.size = size
        self.page_type = page_type
        self.permissions = permissions
        self.cacheable = cacheable
        self.shareable = shareable
        self.security = security
        self.custom_attributes = custom_attributes or {}
        
    @property
    def is_readable(self):
        """Check if page is readable"""
        return bool(self.permissions & self.PERM_READ)
        
    @property
    def is_writable(self):
        """Check if page is writable"""
        return bool(self.permissions & self.PERM_WRITE)
        
    @property
    def is_executable(self):
        """Check if page is executable"""
        return bool(self.permissions & self.PERM_EXECUTE)
        
    @property
    def end_va(self):
        """Virtual address of the last byte in this page"""
        return self.va + self.size - 1
        
    @property
    def end_pa(self):
        """Physical address of the last byte in this page"""
        return self.pa + self.size - 1
    
    def contains_va(self, address):
        """Check if this page contains the given virtual address"""
        return self.va <= address <= self.end_va
    
    def contains_pa(self, address):
        """Check if this page contains the given physical address"""
        return self.pa <= address <= self.end_pa
    
    def va_to_pa(self, va_address):
        """Convert a virtual address to its corresponding physical address"""
        if not self.contains_va(va_address):
            raise ValueError(f"Virtual address 0x{va_address:x} not in this page")
        offset = va_address - self.va
        return self.pa + offset
    
    def pa_to_va(self, pa_address):
        """Convert a physical address to its corresponding virtual address"""
        if not self.contains_pa(pa_address):
            raise ValueError(f"Physical address 0x{pa_address:x} not in this page")
        offset = pa_address - self.pa
        return self.va + offset
    
    def get_attributes_dict(self):
        """Get all attributes as a dictionary"""
        return {
            "type": self.page_type,
            "permissions": {
                "read": self.is_readable,
                "write": self.is_writable,
                "execute": self.is_executable
            },
            "cacheable": self.cacheable,
            "shareable": self.shareable,
            "security": self.security,
            **self.custom_attributes
        }
        
    def get_mmu_attributes(self):
        """
        Convert page attributes to MMU-specific format.
        This would be implemented based on the specific architecture (ARM, etc.)
        """
        # Example for ARM MMUs - actual implementation would be more complex
        attr = 0
        
        # Set permission bits
        if self.is_readable:
            attr |= 0x1
        if self.is_writable:
            attr |= 0x2
        if self.is_executable:
            attr &= ~0x4  # In ARM, XN bit=0 means executable
        else:
            attr |= 0x4   # XN bit=1 means non-executable
            
        # Set memory type bits (this is simplified)
        if self.cacheable == self.CACHE_WB:
            attr |= 0x8
        elif self.cacheable == self.CACHE_WT:
            attr |= 0x10
            
        # Set shareability bits
        if self.shareable == self.SHARE_INNER:
            attr |= 0x20
        elif self.shareable == self.SHARE_OUTER:
            attr |= 0x40
            
        return attr
    
    def __repr__(self):
        """String representation of the page"""
        perms = []
        if self.is_readable:
            perms.append("R")
        if self.is_writable:
            perms.append("W")
        if self.is_executable:
            perms.append("X")
            
        return (f"Page(VA:0x{self.va:x}-0x{self.end_va:x}, "
                f"PA:0x{self.pa:x}-0x{self.end_pa:x}, "
                f"0x{self.size:x} bytes, {self.page_type}, "
                f"{''.join(perms)}, {self.cacheable})")



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
                        memory_log(f"Found matching unmapped region at 0x{overlap_start:x}, size: 0x{overlap_size:x}")
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
        memory_log("======================== PageTableManager - allocate_page")

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


    def get_page_table_entries(self):
        return self.page_table_entries
        
    def get_page_table_entries_by_type(self, type):
        return self.page_table_entries_by_type[type]
    
    def print_page_tables(self):
        current_state = get_current_state()
        memory_log(f"==================== PageTableManager - print_page_tables {current_state.state_name}")
        for page in self.page_table_entries:
            memory_log(f"Page: {page}")
    