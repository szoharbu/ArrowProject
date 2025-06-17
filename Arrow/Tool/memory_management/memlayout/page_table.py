import random
from typing import List, Dict, Optional, Tuple

from Arrow.Tool.memory_management.memory_logger import get_memory_logger
from Arrow.Tool.memory_management.memlayout.interval_lib.interval_lib import IntervalLib
from Arrow.Tool.memory_management.memlayout.page import Page
from Arrow.Tool.memory_management.memlayout.segment_manager import SegmentManager
from Arrow.Utils.configuration_management import Configuration


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


class PageTable:
    '''
    Represents a single MMU context with its own virtual address space.
    Each MMU is associated with a specific core, exception level, and security context.

    VA Space Management: Track and allocate virtual address ranges
    Page Table Generation: Create and maintain page table structures
    Mapping Operations: Create VA→PA mappings with attributes
    MMU Configuration: Generate register values (TTBR, TCR, MAIR)
    Attribute Management: Support different memory permissions/cacheability
    '''


    def __init__(self, page_table_name: str, core_id: str, execution_context: Configuration.Execution_context ):
        """
        Initialize an MMU context.
        
        Args:
            mmu_name: Unique identifier for this MMU (e.g., "c0_el3root", "c1_el1NS")
            state_name: State this MMU belongs to (e.g., "core_0", "core_1")
            execution_context: Execution context (EL3, EL1_NS, EL1_S, EL2_NS, EL2_S, etc.)
        """
        logger = get_memory_logger()
        logger.info(f"============ setting up PageTable: {page_table_name} for {core_id}")

        self.page_table_name = page_table_name
        self.core_id = core_id
        self.execution_context = execution_context

        self.va_memory_range_start_address = Configuration.ByteSize.SIZE_2G.in_bytes() + Configuration.ByteSize.SIZE_2M.in_bytes() # leaving 2MB for the MMU page table and constants
        self.va_memory_range_size = 2 * Configuration.ByteSize.SIZE_4G.in_bytes()

        # VA space management - track unmapped, mapped, and allocated regions
        self.unmapped_va_intervals = IntervalLib(
            start_address=self.va_memory_range_start_address,
            total_size=self.va_memory_range_size,
            default_metadata={"state": "unmapped", "type": "va", "page_table": page_table_name}
        )
        
        self.mapped_va_intervals = IntervalLib(
            default_metadata={"state": "mapped", "type": "va", "page_table": page_table_name}
        )
        
        self.allocated_va_intervals = IntervalLib(
            default_metadata={"state": "allocated", "type": "va", "page_table": page_table_name}
        )
        
        self.non_allocated_va_intervals = IntervalLib(
            default_metadata={"state": "non_allocated", "type": "va", "page_table": page_table_name}
        )

        # Page table entries for this MMU
        self.page_table_entries: List[Page] = []
        self.page_table_entries_by_type = {
            Configuration.Page_types.TYPE_CODE: [],
            Configuration.Page_types.TYPE_DATA: [],
            Configuration.Page_types.TYPE_DEVICE: [],
            Configuration.Page_types.TYPE_SYSTEM: []
        }
        
        # MMU-specific attributes and metadata
        self.attributes = {}
        
        # Track allocations for cross-page references
        self.allocations = []  # List of MemoryAllocation objects

        # Segment manager for this page table
        self.segment_manager = SegmentManager(page_table=self)


    def __str__(self):
        return f"PageTable({self.page_table_name}, {self.core_id}, {self.execution_context.value})"

    def _find_va_eq_pa_unmapped_region(self, page_table_manager, size_bytes, alignment_bits, page_type):
        """
        Find a region that is available at the same address in both VA and PA unmapped spaces
        Uses randomization logic similar to IntervalLib.find_region
        
        Returns: (va_start, pa_start, size) - where va_start == pa_start
        """
        logger = get_memory_logger()
        logger.info(f"Searching for unmapped region where VA=PA is possible, size: {size_bytes}, alignment: {alignment_bits}")
        
        # Get the unmapped VA and PA intervals
        #va_intervals = memory_space_manager.state_unmapped_va_intervals[state_name].free_intervals
        va_intervals = self.unmapped_va_intervals.get_intervals()
        pa_intervals = page_table_manager.unmapped_pa_intervals.get_intervals()
        
        logger.info(f"Found {len(va_intervals)} unmapped VA regions and {len(pa_intervals)} unmapped PA regions")
        
        # Find overlapping regions where VA can equal PA
        matching_regions = []
        for va_interval in va_intervals:
            va_start = va_interval.start
            va_size = va_interval.size
            for pa_interval in pa_intervals:
                pa_start = pa_interval.start
                pa_size = pa_interval.size
                
                # Calculate the intersection of the VA and PA intervals
                # For VA=PA, we need the same address to be available in both spaces
                overlap_start = max(va_start, pa_start)
                overlap_end = min(va_start + va_size - 1, pa_start + pa_size - 1)
                
                if overlap_start <= overlap_end:
                    # There is an overlap
                    overlap_size = overlap_end - overlap_start + 1
                    if overlap_size >= size_bytes:
                        # This overlapping region is big enough
                        matching_regions.append((overlap_start, overlap_size))
        
        if not matching_regions:
            logger.error(f"Could not find any unmapped region where VA=PA is possible for size {size_bytes}")
            raise ValueError(f"Could not find any unmapped region where VA=PA is possible for size {size_bytes}")
        
        # Apply alignment and find suitable intervals (similar to find_region logic)
        suitable_intervals = []
        if alignment_bits is not None:
            alignment = 1 << alignment_bits
            for region_start, region_size in matching_regions:
                # Calculate alignment boundaries
                first_aligned = (region_start + alignment - 1) & ~(alignment - 1)
                last_possible_start = region_start + region_size - size_bytes
                last_aligned = last_possible_start & ~(alignment - 1)
                
                if first_aligned <= last_aligned and first_aligned + size_bytes <= region_start + region_size:
                    # This region can accommodate aligned allocation
                    suitable_intervals.append(((region_start, region_size), first_aligned, last_aligned))
        else:
            # No alignment needed, all regions are suitable
            for region_start, region_size in matching_regions:
                suitable_intervals.append(((region_start, region_size), region_start, region_start + region_size - size_bytes))
                
        if not suitable_intervals:
            logger.error(f"Could not find any aligned unmapped region where VA=PA is possible for size {size_bytes}")
            raise ValueError(f"Could not find any aligned unmapped region where VA=PA is possible for size {size_bytes}")
        
        # Randomize interval selection (similar to find_region)
        if len(suitable_intervals) > 1:
            chosen_idx = random.randrange(0, len(suitable_intervals))
        else:
            chosen_idx = 0
            
        interval, first_aligned, last_aligned = suitable_intervals[chosen_idx]
        region_start, region_size = interval
        
        # Randomize position within the chosen interval (similar to find_region logic)
        if alignment_bits is not None and alignment_bits > 0:
            alignment = 1 << alignment_bits
            if first_aligned != last_aligned:
                # Count number of possible aligned positions
                count = ((last_aligned - first_aligned) // alignment) + 1
                # Choose a random position
                random_offset = random.randint(0, count - 1) * alignment
                va_start = first_aligned + random_offset
            else:
                # Only one aligned position possible
                va_start = first_aligned
        else:
            # No alignment, randomize within the entire suitable range
            max_start = region_start + region_size - size_bytes
            va_start = random.randint(region_start, max_start)
        
        pa_start = va_start  # VA=PA constraint
        logger.info(f"Selected VA=PA unmapped region at address 0x{va_start:x} (VA=PA), size: {size_bytes}")
        
        return va_start, pa_start, size_bytes

    def allocate_page(self, size:Configuration.Page_sizes=None, alignment_bits:int=None, page_type:Configuration.Page_types=None, permissions:int=None, cacheable:str=None, shareable:str=None, custom_attributes:dict=None, sequential_page_count:int=1, VA_eq_PA:bool=False, force_address:int=None):
        logger = get_memory_logger()
        logger.info("")
        logger.info(f"======================== PageTableManager - allocate_page for '{self.page_table_name}' PageTable")
        logger.info(f"==== size: {size}, alignment_bits: {alignment_bits}, page_type: {page_type}, permissions: {permissions}, cacheable: {cacheable}, shareable: {shareable}, custom_attributes: {custom_attributes}, sequential_page_count: {sequential_page_count}, VA_eq_PA: {VA_eq_PA}")

        if force_address is not None:
            logger.info(f"==== allocate_page - force_address: {force_address}")
            if not VA_eq_PA:
                raise ValueError("force_address is only supported when VA_eq_PA is True")

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
            elif size == Configuration.Page_sizes.SIZE_1G:
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
        from Arrow.Tool.memory_management.memlayout.page_table_manager import get_page_table_manager

        page_table_manager = get_page_table_manager()
        
        # Step 1: Find and allocate regions from unmapped space
        try:
            if force_address:
                logger.info(f"Allocating unmapped memory with force_address VA=PA={hex(force_address)}, size: {hex(full_size_bytes)}")
                va_start = force_address
                pa_start = force_address
                size = full_size_bytes
                
                # Remove the region from unmapped space (similar to VA_eq_PA path)
                va_removed = self.unmapped_va_intervals.remove_region(va_start, size)
                pa_removed = page_table_manager.unmapped_pa_intervals.remove_region(pa_start, size)
                
                # Log the results of removal attempts
                if not va_removed:
                    logger.warning(f"VA region 0x{va_start:x}-0x{va_start + size - 1:x} was not found in unmapped VA intervals - may already be mapped or have overlaps")
                else:
                    logger.info(f"Successfully removed VA region 0x{va_start:x}-0x{va_start + size - 1:x} from unmapped intervals")
                    
                if not pa_removed:
                    logger.warning(f"PA region 0x{pa_start:x}-0x{pa_start + size - 1:x} was not found in unmapped PA intervals - may already be mapped or have overlaps")
                else:
                    logger.info(f"Successfully removed PA region 0x{pa_start:x}-0x{pa_start + size - 1:x} from unmapped intervals")
                
                # Check if we should fail when regions can't be removed
                if not va_removed or not pa_removed:
                    logger.error(f"Force address allocation failed - requested regions are not available in unmapped space")
                    raise ValueError(f"Cannot allocate at forced address 0x{force_address:x} - region is not available in unmapped space (VA removed: {va_removed}, PA removed: {pa_removed})")
                
                # Map the VA to PA with equal addresses
                page_table_manager.map_va_to_pa(self, va_start, pa_start, size, page_type)
                
                va_size = size
                logger.info(f"Successfully allocated and mapped force address memory at 0x{va_start:x}, size: {hex(size)}")
                
            elif VA_eq_PA:
                logger.info(f"Allocating unmapped memory with VA=PA constraint, size: {full_size_bytes}, alignment: {alignment_bits}")
                
                # Find a region that is available at the same address in both VA and PA unmapped spaces
                va_start, pa_start, size = self._find_va_eq_pa_unmapped_region(
                    page_table_manager, 
                    full_size_bytes, 
                    alignment_bits, 
                    page_type
                )
                
                # Allocate the region from unmapped space
                # First, update the unmapped intervals
                # memory_space_manager.state_unmapped_va_intervals[state_name].remove_region(va_start, size)
                self.unmapped_va_intervals.remove_region(va_start, size)
                page_table_manager.unmapped_pa_intervals.remove_region(pa_start, size)
                
                # Map the VA to PA with equal addresses
                page_table_manager.map_va_to_pa(self, va_start, pa_start, size, page_type)
                
                va_size = size
                logger.info(f"Successfully allocated and mapped VA=PA memory at 0x{va_start:x}, size: {hex(size)}")
                
            else:
                # Original implementation for non-VA_eq_PA case
                # Use the find_and_remove method which handles state initialization
                va_start, va_size = self.unmapped_va_intervals.find_and_remove(full_size_bytes, alignment_bits)
                
                pa_allocation = page_table_manager.allocate_pa_interval(full_size_bytes, alignment_bits=alignment_bits)
                
                pa_start, pa_size = pa_allocation
                
                # Step 2: Add the allocated regions to mapped pools
                # First, add to mapped intervals pool, specifying the page type
                page_table_manager.map_va_to_pa(self, va_start, pa_start, va_size, page_type)
                
        except (ValueError, MemoryError) as e:
            logger.error(f"Failed to allocate page memory: {e}")
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
                execution_context=self.execution_context, 
                custom_attributes=custom_attributes
            )
            
            # Add to our tracking collections
            self.page_table_entries.append(page)
            self.page_table_entries_by_type[page.page_type].append(page)
            result.append(page)
            
            logger.info(f"Created page: {page}")
            
        # Return result based on sequential_page_count
        if sequential_page_count == 1:
            return result[0]  
        else:
            return result


    def allocate_cross_core_page(self):
        logger = get_memory_logger()
        logger.info("")
        logger.info("======================== PageTableManager - allocate_cross_core_page")

        # from the cross_core_page all is hard-coded for now. TODO:: consider making it configurable in the future.
        size = Configuration.Page_sizes.SIZE_2M # setting big space, as this pages can also be used for non-cross segments 

        if size == Configuration.Page_sizes.SIZE_4K:
            alignment_bits = 12
        elif size == Configuration.Page_sizes.SIZE_2M:
            alignment_bits = 21
        elif size == Configuration.Page_sizes.SIZE_1G:
            alignment_bits = 30

        page_type = Configuration.Page_types.TYPE_DATA
        permissions = Page.PERM_READ | Page.PERM_WRITE | Page.PERM_EXECUTE
        cacheable = Page.CACHE_WB
        shareable = Page.SHARE_NONE
        custom_attributes = {}

        logger.info(f"==== size: {size}, alignment_bits: {alignment_bits}, page_type: {page_type}, permissions: {permissions}, cacheable: {cacheable}, shareable: {shareable}, custom_attributes: {custom_attributes}")

        size_bytes = size.value

        # Get current state and memory space manager
        from Arrow.Tool.memory_management.memlayout.page_table_manager import get_page_table_manager
        page_table_manager = get_page_table_manager()

        
        try:
              # Step 1: Find and allocate regions from unmapped space
            pa_allocation = page_table_manager.allocate_pa_interval(size_bytes, alignment_bits=alignment_bits)
            pa_start, pa_size = pa_allocation



            orig_state_name = self.core_id
            all_page_tables = page_table_manager.get_all_page_tables()
            
            for page_table in all_page_tables:
                logger.info(f"core_page_tables for {page_table.core_id}: {page_table.page_table_name}")

                va_start, va_size = page_table.unmapped_va_intervals.find_and_remove(size_bytes, alignment_bits)
                
                # Step 2: Add the allocated regions to mapped pools
                # First, add to mapped intervals pool, specifying the page type
                page_table_manager.map_va_to_pa(page_table, va_start, pa_start, va_size, page_type)
                
                # Create the page objects for each page in the sequence
                page = Page(
                    va=va_start, 
                    pa=pa_start, 
                    size=size_bytes, 
                    page_type=page_type, 
                    permissions=permissions, 
                    cacheable=cacheable, 
                    shareable=shareable, 
                    execution_context=page_table.execution_context, 
                    custom_attributes=custom_attributes,
                    is_cross_core=True
                )

                # Add to our tracking collections
                page_table.page_table_entries.append(page)
                page_table.page_table_entries_by_type[page.page_type].append(page)
                
                
                logger.info(f"Created Cross-Core page {page_table.core_id}:{page_table.page_table_name} - {page}")


        except (ValueError, MemoryError) as e:
            logger.error(f"Failed to allocate page memory: {e}")
            raise ValueError(f"Could not allocate memory regions of size {size} with alignment {alignment_bits}")
        
    

    def allocate_segment(self, size, page_type, alignment_bits=None, VA_eq_PA=False, page_size=4096, force_address=None):
        """
        Allocates memory from mapped but non-allocated regions
        - Can allocate cross-page regions if pages are sequential
        - Returns allocation information
        
        :param size: Size in bytes to allocate
        :param page_type: Page type to allocate
        :param alignment_bits: Alignment in bits (default: None)
        :param VA_eq_PA: If True, the virtual address must equal the physical address (default: False)
        :param page_size: Page size in bytes (default: 4096)
        :param force_address: If provided, forces allocation at this specific address (VA=PA) (default: None)
        :return: MemoryAllocation object
        """
        logger = get_memory_logger()
        
        # Input validation
        if size is None:
            raise ValueError("size parameter cannot be None")
        if page_type is None:
            raise ValueError("page_type parameter cannot be None")
        if size <= 0:
            raise ValueError(f"size must be positive, got: {size}")
        if page_size is None or page_size <= 0:
            raise ValueError(f"page_size must be positive, got: {page_size}")
            
        logger.info(f"Allocating memory of size {hex(size)} for page_table '{self.page_table_name}' with page_type {page_type}, alignment_bits={alignment_bits}, VA_eq_PA={VA_eq_PA}, force_address={hex(force_address) if force_address else None}")
        
        if force_address is not None:
            logger.info(f"==== allocate_segment - force_address: {hex(force_address)}")
            if not VA_eq_PA:
                raise ValueError("force_address is only supported when VA_eq_PA is True")
        
        # Determine if we're allocating code or data
        is_code = True if page_type == Configuration.Page_types.TYPE_CODE else False
        
        # Find suitable VA and PA addresses based on allocation type
        if force_address is not None:
            va_start = pa_start = force_address
            
            # Validate alignment if specified
            if alignment_bits is not None:
                alignment = 1 << alignment_bits
                if va_start % alignment != 0:
                    logger.error(f"Forced address 0x{va_start:x} is not aligned to {alignment_bits} bits!")
                    raise ValueError(f"Forced address 0x{va_start:x} is not aligned to {alignment_bits} bits (required alignment: {alignment})")
            
            # Find overlapping pages (we still need this for the allocation object)
            page_entries = self.get_pages()
            overlapping_pages = []
            va_end = va_start + size - 1
            
            for page in page_entries:
                if (page.va <= va_end and page.end_va >= va_start):
                    overlapping_pages.append(page)
            
            overlapping_pages.sort(key=lambda p: p.va)
            logger.info(f"Found {len(overlapping_pages)} pages for forced address allocation")
            
        elif VA_eq_PA:
            va_start, pa_start, overlapping_pages = self._find_va_eq_pa_addresses(size, page_type, alignment_bits, page_size)
        else:
            va_start, pa_start, overlapping_pages = self._find_regular_addresses(size, page_type, alignment_bits, page_size)
            
        # From here on, the logic is the same for all allocation types
        # Mark as allocated (add to allocated, remove from non-allocated)
        self.allocated_va_intervals.add_region(va_start, size, metadata={"page_type": page_type, "page_table": self.page_table_name})
        va_removed = self.non_allocated_va_intervals.remove_region(va_start, size)
        
        from Arrow.Tool.memory_management.memlayout.page_table_manager import get_page_table_manager
        page_table_manager = get_page_table_manager()
        page_table_manager.allocated_pa_intervals.add_region(pa_start, size, metadata={"page_type": page_type, "page_table": self.page_table_name})
        pa_removed = page_table_manager.non_allocated_pa_intervals.remove_region(pa_start, size)
        
        # Check if removal failed (region not available) - this catches overlaps
        if not va_removed:
            logger.error(f"VA region 0x{va_start:x}-0x{va_start + size - 1:x} is not available in non-allocated intervals")
            raise ValueError(f"Cannot allocate at address 0x{va_start:x} - VA region is not available in non-allocated space")
        
        if not pa_removed:
            logger.error(f"PA region 0x{pa_start:x}-0x{pa_start + size - 1:x} is not available in non-allocated intervals")
            raise ValueError(f"Cannot allocate at address 0x{pa_start:x} - PA region is not available in non-allocated space")
                
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
            logger.info(f"Created VA=PA allocation: VA=PA=0x{va_start:x}, size={size}")
        else:
            logger.info(f"Created allocation: VA=0x{va_start:x}, PA=0x{pa_start:x}, size={size}")
        
        self.allocations.append(allocation)
        return allocation




    def get_pages(self) -> List[Page]:
        """Get all pages in this MMU."""
        return self.page_table_entries
    
    def get_pages_by_type(self, page_type: Configuration.Page_types) -> List[Page]:
        """Get pages of a specific type."""
        return self.page_table_entries_by_type[page_type]
    
    # Query Methods
    def is_mapped(self, va_addr: int, size: int = 1) -> bool:
        """Check if a VA region is mapped."""
        return not self.unmapped_va_intervals.is_region_available(va_addr, size)
    
    def is_allocated(self, va_addr: int, size: int = 1) -> bool:
        """Check if a VA region is allocated (has pages)."""
        va_end = va_addr + size - 1
        for page in self.page_table_entries:
            if page.va <= va_end and page.end_va >= va_addr:
                return True
        return False
    
    def find_available_region(self, size: int, alignment_bits: int = None) -> Optional[Tuple[int, int]]:
        """Find an available unmapped region."""
        try:
            return self.unmapped_va_intervals.find_region(size, alignment_bits)
        except ValueError:
            return None
    
    # Attribute Management
    def set_attribute(self, key: str, value):
        """Set an MMU-specific attribute."""
        self.attributes[key] = value
    
    def get_attribute(self, key: str, default=None):
        """Get an MMU-specific attribute."""
        return self.attributes.get(key, default)
    
    # Statistics and Debugging
    def get_memory_stats(self) -> Dict:
        """Get memory usage statistics for this MMU."""
        unmapped_intervals = self.unmapped_va_intervals.get_intervals()
        mapped_intervals = self.mapped_va_intervals.get_intervals()
        allocated_intervals = self.allocated_va_intervals.get_intervals()
        
        return {
            "page_table_name": self.page_table_name,
            "core_id": self.core_id,
            "execution_context": self.execution_context.value,
            # "va_space": {
            #     "start": hex(self.va_memory_range_start_address),
            #     "size": hex(self.va_memory_range_size),
            #     "unmapped_regions": len(unmapped_intervals),
            #     "mapped_regions": len(mapped_intervals),
            #     "allocated_regions": len(allocated_intervals)
            # },
            "pages": {
                "total": len(self.page_table_entries),
                "code": len(self.page_table_entries_by_type[Configuration.Page_types.TYPE_CODE]),
                "data": len(self.page_table_entries_by_type[Configuration.Page_types.TYPE_DATA]),
                "device": len(self.page_table_entries_by_type[Configuration.Page_types.TYPE_DEVICE]),
                "system": len(self.page_table_entries_by_type[Configuration.Page_types.TYPE_SYSTEM])
            }
        }
    
   

    def _find_va_eq_pa_addresses(self, size, page_type, alignment_bits=None, page_size=4096):
        """
        Find VA and PA addresses that satisfy the VA=PA constraint
        
        :return: (va_start, pa_start, overlapping_pages)
        """
        logger = get_memory_logger()
        logger.info("Searching for matching VA and PA regions where VA=PA...")
        
        pages = self.get_pages()
        va_eq_pa_pages = []
        for page in pages:
            if page.va == page.pa:
                va_eq_pa_pages.append(page)
        logger.info(f"Found {len(va_eq_pa_pages)} pages that satisfy VA=PA")
        selected_page = random.choice(va_eq_pa_pages)
        logger.info(f"Selected page: {selected_page}")
        
        # Get the available regions for both VA and PA
        all_va_intervals = self.non_allocated_va_intervals.get_intervals(criteria={"page_type": page_type})
        
        # Find intervals that overlap with the selected VA=PA page and create intersections
        # Since we're in a VA=PA page, VA and PA intervals are identical, so we only need to check VA
        suitable_intervals = []
        
        for interval in all_va_intervals:
            # Check if interval overlaps with the page at all
            if interval.start < selected_page.end_va + 1 and (interval.start + interval.size) > selected_page.va:
                # Calculate the intersection of the interval with the page
                intersection_start = max(interval.start, selected_page.va)
                intersection_end = min(interval.start + interval.size - 1, selected_page.end_va)
                intersection_size = intersection_end - intersection_start + 1
                
                # Check if the intersection is large enough for our allocation
                if intersection_size >= size:
                    # Create a new interval representing the intersection
                    from Arrow.Tool.memory_management.memlayout.interval_lib.interval_lib import Interval
                    intersection_interval = Interval(intersection_start, intersection_size, interval.metadata)
                    suitable_intervals.append(intersection_interval)
                    logger.info(f"Found suitable intersection: 0x{intersection_start:x}-0x{intersection_end:x} (size: 0x{intersection_size:x}) from interval 0x{interval.start:x}-0x{interval.start + interval.size - 1:x}")
                else:
                    logger.info(f"Intersection too small: 0x{intersection_start:x}-0x{intersection_end:x} (size: 0x{intersection_size:x}) < required 0x{size:x}")
            # else:
            #     memory_log(f"No overlap: interval 0x{interval.start:x}-0x{interval.start + interval.size - 1:x} with page 0x{selected_page.va:x}-0x{selected_page.end_va:x}")
        
        if len(suitable_intervals) == 0:
            logger.error(f"No available {page_type} regions inside VA=PA page that fit size {size}")
            raise ValueError(f"No available {page_type} regions inside VA=PA page that fit size {size}")
        
        # Select one suitable interval (could be random or first)
        selected_interval = random.choice(suitable_intervals)
        logger.info(f"Selected interval inside VA=PA page: {hex(selected_interval.start)}-{hex(selected_interval.start + selected_interval.size - 1)}, size: 0x{selected_interval.size:x}")
        
        # Apply alignment and find position within the selected interval
        if alignment_bits is not None:
            alignment = 1 << alignment_bits
            # Find the first aligned address within the interval
            aligned_start = (selected_interval.start + alignment - 1) & ~(alignment - 1)
            
            # Check if the aligned allocation fits within the interval
            if aligned_start + size > selected_interval.start + selected_interval.size:
                logger.error(f"Aligned allocation doesn't fit in interval")
                raise ValueError(f"Cannot fit aligned allocation of size {size} with alignment {alignment_bits} bits in selected interval")
            
            # Randomize position within the aligned possibilities
            max_aligned_offset = ((selected_interval.start + selected_interval.size - size) & ~(alignment - 1)) - aligned_start
            if max_aligned_offset > 0:
                # Calculate how many aligned positions are possible
                num_positions = (max_aligned_offset // alignment) + 1
                random_position = random.randrange(num_positions)
                random_offset = random_position * alignment
                aligned_start += random_offset
                logger.info(f"Randomized aligned position: offset 0x{random_offset:x} from first aligned address")
            
            va_start = pa_start = aligned_start
        else:
            # No alignment required, randomize position within interval
            max_offset = selected_interval.size - size
            if max_offset > 0:
                random_offset = random.randrange(max_offset + 1)
                va_start = pa_start = selected_interval.start + random_offset
                logger.info(f"Randomized position: offset 0x{random_offset:x} from interval start")
            else:
                va_start = pa_start = selected_interval.start
        
        va_end = va_start + size - 1

        # print(f"va_start: {hex(va_start)}, va_end: {hex(va_end)}")
        # print(f"pa_start: {hex(pa_start)}")

        logger.info(f"Final allocation: VA=PA=0x{va_start:x}-0x{va_end:x}, size=0x{size:x}")
        
        # Since we selected our allocation from within the selected_page boundaries,
        # the only overlapping page is the one we started with
        overlapping_pages = [selected_page]
        
        return va_start, pa_start, overlapping_pages


    def _find_regular_addresses(self, size, page_type, alignment_bits=None, page_size=4096):
        """
        Find VA and PA addresses for regular allocation (not VA=PA)
        
        :return: (va_start, pa_start, overlapping_pages)
        """
        logger = get_memory_logger()

        intervals = self.non_allocated_va_intervals.get_intervals(criteria={"page_type": page_type})
        logger.info(f"Looking for {page_type.value} region of size {size}. Available {len(intervals)} regions:")
        for i, interval in enumerate(intervals):
            logger.info(f"  {page_type.value} region {i}: VA:0x{interval.start:x}-0x{interval.end:x}, size:0x{interval.size:x}")
            
        # Find available non-allocated VA region from the relevent pool only, with alignment
        va_avail = self.non_allocated_va_intervals.find_region(size, alignment_bits, criteria={"page_type": page_type})
        if not va_avail:
            raise ValueError(f"No available non-allocated {page_type.value} VA region of size {size} with alignment {alignment_bits} for {self.page_table_name}")
        
        va_start, _ = va_avail
        logger.info(f"Found suitable VA region starting at {hex(va_start)}")
        
        # Check that the region is properly aligned
        if alignment_bits is not None:
            alignment = 1 << alignment_bits
            if va_start % alignment != 0:
                logger.error(f"VA address 0x{va_start:x} is not aligned to {alignment_bits} bits!")
                raise ValueError(f"Failed to allocate properly aligned memory. VA:0x{va_start:x} is not aligned to {alignment_bits} bits!")
        
        # Find the physical address that corresponds to the VA we just found
        # Retrieve the page table entries from the current state
        page_entries = self.get_pages()
        
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
            logger.info(f"Found {len(overlapping_pages)} pages overlapping with segment VA:{hex(va_start)}-{hex(va_end)}")
            
            # Check if pages are sequential without gaps
            is_sequential = True
            covered_range_start = max(overlapping_pages[0].va, va_start)
            covered_range_end = min(overlapping_pages[0].end_va, va_end)
            
            for i in range(1, len(overlapping_pages)):
                prev_page = overlapping_pages[i-1]
                curr_page = overlapping_pages[i]
                
                # Check for a gap between pages
                if prev_page.end_va + 1 != curr_page.va:
                    logger.info(f"Gap detected between pages: {prev_page} and {curr_page}")
                    is_sequential = False
                    break
                
                # Update covered range
                if curr_page.va <= va_end:
                    covered_range_end = min(curr_page.end_va, va_end)
            
            # Verify the pages fully cover our segment
            if covered_range_start <= va_start and covered_range_end >= va_end and is_sequential:
                logger.info(f"Pages provide complete sequential coverage for the segment")
                
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
                    logger.info(f"Found corresponding PA for VA:0x{va_start:x} -> PA:0x{pa_start:x} in page {containing_page}")
                    
                    # Verify PA alignment matches VA alignment
                    if alignment_bits is not None:
                        alignment = 1 << alignment_bits
                        if pa_start % alignment != 0:
                            logger.error(f"PA address 0x{pa_start:x} is not aligned to {alignment_bits} bits!")
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
                                logger.warning(f"Physical memory is not sequential between pages: "
                                                f"PA 0x{pa_at_boundary:x} -> 0x{next_page.pa:x}")
                                # We'll continue anyway since VA is what matters for allocation
                else:
                    logger.error(f"Failed to find the specific page containing VA start 0x{va_start:x}")
                    raise ValueError(f"Internal error: couldn't identify page containing VA start")
            else:
                if not is_sequential:
                    logger.error(f"Pages are not sequential, cannot allocate segment")
                else:
                    logger.error(f"Pages don't fully cover segment VA:0x{va_start:x}-0x{va_end:x}, "
                                f"covered: 0x{covered_range_start:x}-0x{covered_range_end:x}")
                # Fall back to the error case below
                overlapping_pages = []
                
        if not overlapping_pages:
            # If we can't find the page entries (shouldn't happen with proper page management)
            # fall back to the original logic as a last resort
            logger.error(f"CRITICAL ERROR: Cannot find pages covering VA:0x{va_start:x}-0x{va_end:x}. Page table may be inconsistent!")
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
            logger.warning(f"Using fallback PA allocation: 0x{pa_start:x}. THIS IS LIKELY INCORRECT!")
            
        logger.info(f"Using PA region starting at 0x{pa_start:x}")
        
        return va_start, pa_start, overlapping_pages


    def print_summary(self, verbose: bool = False):
        """Print a comprehensive summary of this MMU's state."""
        logger = get_memory_logger()
        logger.info("")
        logger.info(f"==== PageTableManager - print_summary for {self.page_table_name}")
        stats = self.get_memory_stats()
        logger.info(f"  Core: {stats['core_id']}")
        logger.info(f"  Execution Context: {stats['execution_context']}")
        logger.info(f"  Pages ({stats['pages']['total']} total, {stats['pages']['code']} code, {stats['pages']['data']} data):")
        
        for page in self.page_table_entries:
            logger.info(f"      Page: {page}")