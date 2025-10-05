"""
NonPagingSegmentManager - A minimal segment manager for when paging is disabled.
Provides the same interface as SegmentManager but without page table dependencies.
"""

from typing import List, Dict
from Arrow.Tool.memory_management.memlayout.segment import MemorySegment, CodeSegment, DataSegment
from Arrow.Tool.memory_management.memory_logger import get_memory_logger
from Arrow.Utils.configuration_management import Configuration


class NonPagingIntervalTracker:
    """
    Simple interval tracker for non-paging segments.
    Manages available memory regions within a segment.
    """
    
    def __init__(self, base_address: int, size: int):
        self.base_address = base_address
        self.size = size
        self.next_offset = 0  # Simple sequential allocation

    def find_region(self, byte_size: int, alignment: int = None) -> tuple:
        """
        Find an available memory region of the specified size.
        Returns (address, size) tuple or None if not available.
        """
        # Apply alignment if specified
        if alignment and alignment > 1:
            aligned_offset = (self.next_offset + alignment - 1) & ~(alignment - 1)
        else:
            aligned_offset = self.next_offset
        
        # Check if we have enough space
        if aligned_offset + byte_size > self.size:
            return None
        
        address = self.base_address + aligned_offset
        return (address, byte_size)
    
    def remove_region(self, address: int, byte_size: int):
        """
        Mark a memory region as allocated.
        For simple sequential allocation, just advance the next_offset.
        """
        expected_address = self.base_address + self.next_offset
        if address >= expected_address:
            # Update next_offset to after this allocation
            self.next_offset = (address - self.base_address) + byte_size


class NonPagingSegmentManager:
    """
    Minimal segment manager for bare-metal/non-paging scenarios.
    Provides the same interface as SegmentManager but manages segments directly in memory.
    """
    
    def __init__(self, name: str = "non_paging"):
        """
        Initialize the non-paging segment manager.
        """
        logger = get_memory_logger()
        logger.info(f"============ initializing NonPagingSegmentManager for {name}")
        
        self.name = name
        self.memory_segments: List[MemorySegment] = []
        self.pool_type_mapping: Dict[Configuration.Memory_types, List[MemorySegment]] = {}
        
        # Simple address allocation - start from a base address and increment
        self.next_address = 0x10000000  # Start at 256MB

    def get_name(self):
        return self.name

    def allocate_memory_segment(self, name: str, byte_size: int, memory_type: Configuration.Memory_types, 
                              alignment_bits: int = None, VA_eq_PA: bool = False, force_address: int = None, 
                              exclusive_segment: bool = True) -> MemorySegment:
        """
        Allocate a memory segment - simplified version for non-paging.
        """
        logger = get_memory_logger()
        logger.info(f"==================== NonPaging allocate_memory_segment: {name}, size: {byte_size}, type: {memory_type}")
        
        # Check for duplicate names
        for segment in self.memory_segments:
            if segment.name == name:
                raise ValueError(f"Memory segment with name '{name}' already exists.")
        
        # Determine address
        if force_address:
            address = force_address
            pa_address = force_address  # In non-paging, VA == PA
        else:
            # Simple allocation - just increment from base
            if alignment_bits:
                # Align to the specified boundary
                align_size = 1 << alignment_bits
                self.next_address = (self.next_address + align_size - 1) & ~(align_size - 1)
            address = self.next_address
            pa_address = address  # In non-paging, VA == PA
            self.next_address += byte_size
        
        # Create appropriate segment type
        if memory_type in [Configuration.Memory_types.CODE, Configuration.Memory_types.BOOT_CODE, Configuration.Memory_types.BSP_BOOT_CODE]:
            # Create a minimal CodeSegment without page_table dependency
            segment = NonPagingCodeSegment(name, address, pa_address, byte_size, memory_type, exclusive_segment)
        else:
            # Create a minimal DataSegment
            segment = NonPagingDataSegment(name, address, pa_address, byte_size, memory_type, exclusive_segment)
        
        # Add to tracking
        self.memory_segments.append(segment)
        if memory_type not in self.pool_type_mapping:
            self.pool_type_mapping[memory_type] = []
        self.pool_type_mapping[memory_type].append(segment)
        
        logger.info(f"==================== Allocated non-paging segment {name} at {hex(address)}")
        return segment
    
    def get_segments(self, pool_type, non_exclusive_only: bool = False) -> List[MemorySegment]:
        """
        Get segments by type - same interface as SegmentManager.
        """
        # Handle both single type and list of types
        if not isinstance(pool_type, list):
            pool_types = [pool_type]
        else:
            pool_types = pool_type
            
        result = []
        for ptype in pool_types:
            if ptype in self.pool_type_mapping:
                segments = self.pool_type_mapping[ptype]
                if non_exclusive_only:
                    segments = [s for s in segments if not s.exclusive_segment]
                result.extend(segments)
        
        return result
    
    def get_segment(self, segment_name: str) -> MemorySegment:
        """
        Get a specific segment by name.
        """
        for segment in self.memory_segments:
            if segment.name == segment_name:
                return segment
        raise ValueError(f"Segment '{segment_name}' not found")
    
    def get_stack_data_start_address(self) -> int:
        """
        Get stack data start address - simplified for non-paging.
        """
        # Find stack segments
        stack_segments = self.get_segments(Configuration.Memory_types.STACK)
        if stack_segments:
            return stack_segments[0].address
        else:
            # Return a default stack address if no stack segment allocated
            return 0x80000000
    
    def print_memory_summary(self, verbose=False):
        """
        Print memory summary.
        """
        logger = get_memory_logger()
        logger.info(f"NonPagingSegmentManager '{self.name}' - {len(self.memory_segments)} segments allocated")
        if verbose:
            for segment in self.memory_segments:
                logger.info(f"  {segment}")


class NonPagingCodeSegment(CodeSegment):
    """
    Minimal CodeSegment for non-paging scenarios.
    """
    def __init__(self, name: str, address: int, pa_address: int, byte_size: int, 
                 memory_type: Configuration.Memory_types, exclusive_segment: bool):
        self.name = name
        self.address = address
        self.pa_address = pa_address
        self.byte_size = byte_size
        self.memory_type = memory_type
        self.exclusive_segment = exclusive_segment
        
        # Essential for AsmLogger compatibility
        self.asm_units_list = []
        
        # Required for cross-core compatibility - non-paging segments are not cross-core
        self.is_cross_core = False
        
        # Create a simple label
        from Arrow.Tool.asm_libraries.label import Label
        from Arrow.Tool.asm_blocks import AsmUnit
        self.code_label = Label(postfix=f"{name}_code_segment")
        
        # Add initial label
        asm_unit = AsmUnit(asm_string=f"{self.code_label}:", comment=f"starting label for {name} code Segment")
        self.asm_units_list.append(asm_unit)
    
    def get_start_label(self):
        return self.code_label
    
    def __str__(self):
        return f"NonPagingCodeSegment(name={self.name}, address={hex(self.address)}, byte_size={hex(self.byte_size)}, memory_type={self.memory_type})"
    
    def __repr__(self):
        return self.__str__()


class NonPagingDataSegment(DataSegment):
    """
    Minimal DataSegment for non-paging scenarios.
    """
    def __init__(self, name: str, address: int, pa_address: int, byte_size: int, 
                 memory_type: Configuration.Memory_types, exclusive_segment: bool):
        self.name = name
        self.address = address
        self.pa_address = pa_address
        self.byte_size = byte_size
        self.memory_type = memory_type
        self.exclusive_segment = exclusive_segment
        
        # Essential for data compatibility
        self.data_units_list = []
        self.memory_block_list = []
        
        # Required for cross-core compatibility - non-paging segments are not cross-core
        self.is_cross_core = False
        
        # Required for memory allocation - create a simple interval tracker
        self.interval_tracker = NonPagingIntervalTracker(address, byte_size)
    
    def __str__(self):
        return f"NonPagingDataSegment(name={self.name}, address={hex(self.address)}, byte_size={hex(self.byte_size)}, memory_type={self.memory_type})"
    
    def __repr__(self):
        return self.__str__()