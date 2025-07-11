import random
from abc import ABC
from Arrow.Tool.memory_management.memory_logger import get_memory_logger
from Arrow.Utils.configuration_management import Configuration

from Arrow.Tool.asm_blocks import DataUnit, AsmUnit
from Arrow.Tool.asm_libraries.label import Label
from Arrow.Tool.memory_management.memlayout.interval_lib import interval_lib
from Arrow.Tool.memory_management.memory_block import MemoryBlock

# Abstract base class for MemorySegment
class MemorySegment(ABC):

    # generate incremental memory_segment_unique_id
    _memory_segment_initial_seed_id = random.randint(1234, 5678)  # start at a random label

    def __init__(self, name: str, page_table, address: int, pa_address: int, byte_size: int, memory_type:Configuration.Memory_types, exclusive_segment:bool):
        """
        Initialize a segment from a memory block.
        :param name: segment name.
        :param address: segment address.
        :param pa_address: segment physical address.
        :param byte_size: segment size in bytes.
        :param memory_type: segment type.
        :param exclusive_segment: When we want to allocate a segment that is exclusive to a specific use-case. Default is True.
        """
        MemorySegment._memory_segment_initial_seed_id += 1
        self.name = f"{name}_{MemorySegment._memory_segment_initial_seed_id}"
        self.address = address
        self.pa_address = pa_address
        self.byte_size = byte_size
        self.memory_type = memory_type
        # Will be set when allocated from memory manager
        self.allocation = None
        # List of actual Page objects this segment spans
        self.covered_pages = []
        self.page_table = page_table
        self.exclusive_segment = exclusive_segment

    def __str__(self):
        #return self.name
        return f"{self.__class__.__name__}(name={self.name}, address={hex(self.address)}, pa_address={hex(self.pa_address)}, byte_size={hex(self.byte_size)}, memory_type={self.memory_type})"

    def __repr__(self):
        page_info = f", spans {len(self.covered_pages)} pages" if self.covered_pages else ""
        return f"{self.__class__.__name__}(name={self.name}, address={hex(self.address)}, pa_address={hex(self.pa_address)}, byte_size={hex(self.byte_size)}, memory_type={self.memory_type}{page_info})"


# CodeSegment inherits from MemorySegment and adds a start_label attribute
class CodeSegment(MemorySegment):
    def __init__(self, name: str, page_table, address: int, pa_address: int, byte_size: int, memory_type:Configuration.Memory_types, exclusive_segment:bool):
        super().__init__(name, page_table, address, pa_address, byte_size, memory_type, exclusive_segment)
        self.code_label = Label(postfix=f"{name}_code_segment")

        # per CodeSegment list that holds all AsmUnits
        self.asm_units_list:list[AsmUnit] = []

        asm_unit = AsmUnit(asm_string=f"{self.code_label}:", comment=f"starting label for {name} code Segment")
        self.asm_units_list.append(asm_unit)

    def get_start_label(self):
        return self.code_label

# DataSegment inherits from MemorySegment and may add more data-specific attributes
class DataSegment(MemorySegment):
    def __init__(self, name: str, page_table, address: int, pa_address: int, byte_size: int, memory_type:Configuration.Memory_types, is_cross_core:bool, exclusive_segment:bool, init_value: str=None):
        super().__init__(name, page_table, address, pa_address, byte_size, memory_type, exclusive_segment)
        self.init_value = init_value  # Example of additional attribute

        # per DataSegment list that holds all DataUnits and all MemorySegments
        self.data_units_list:list[DataUnit] = []
        self.memory_block_list:list[MemoryBlock] = []
        self.is_cross_core = is_cross_core

        if is_cross_core and memory_type != Configuration.Memory_types.DATA_PRESERVE:
            raise ValueError(f"Cross-core segments must be of type DATA_PRESERVE, but got {memory_type}")

        if memory_type == Configuration.Memory_types.DATA_PRESERVE:
            # Initially, the entire block is free
            self.interval_tracker = interval_lib.IntervalLib(start_address=address, total_size=byte_size)



