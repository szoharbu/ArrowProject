import random
from abc import ABC
from Tool.asm_blocks import DataUnit, AsmUnit
from Utils.configuration_management import Configuration
from Tool.asm_libraries.label import Label
from Tool.memory_management import interval_lib
from Tool.memory_management.memory_block import MemoryBlock

# Abstract base class for MemorySegment
class MemorySegment(ABC):

    # generate incremental memory_segment_unique_id
    _memory_segment_initial_seed_id = random.randint(1234, 5678)  # start at a random label

    def __init__(self, name: str, address: int, byte_size: int, memory_type:Configuration.Memory_types):

        MemorySegment._memory_segment_initial_seed_id += 1
        self.name = f"{name}_{MemorySegment._memory_segment_initial_seed_id}"
        self.address = address
        self.byte_size = byte_size
        self.memory_type = memory_type

    def __str__(self):
        #return self.name
        return f"{self.__class__.__name__}(name={self.name}, address={hex(self.address)}, byte_size={hex(self.byte_size)}, type={self.memory_type})"

    def __repr__(self):
        return f"{self.__class__.__name__}(name={self.name}, address={hex(self.address)}, byte_size={hex(self.byte_size)}, type={self.memory_type})"


# CodeSegment inherits from MemorySegment and adds a start_label attribute
class CodeSegment(MemorySegment):
    def __init__(self, name: str, address: int, byte_size: int, memory_type:Configuration.Memory_types):
        super().__init__(name, address, byte_size, memory_type)
        self.code_label = Label(postfix=f"{name}_code_segment")

        # per CodeSegment list that holds all AsmUnits
        self.asm_units_list:list[AsmUnit] = []

        asm_unit = AsmUnit(asm_string=f"{self.code_label}:", comment=f"starting label for {name} code Segment")
        self.asm_units_list.append(asm_unit)

# DataSegment inherits from MemorySegment and may add more data-specific attributes
class DataSegment(MemorySegment):
    def __init__(self, name: str, address: int, byte_size: int, memory_type:Configuration.Memory_types, init_value: str=None):
        super().__init__(name, address, byte_size, memory_type)
        self.init_value = init_value  # Example of additional attribute

        # per DataSegment list that holds all DataUnits and all MemorySegments
        self.data_units_list:list[DataUnit] = []
        self.memory_block_list:list[MemoryBlock] = []

        if memory_type == Configuration.Memory_types.DATA_PRESERVE:
            # Initially, the entire block is free
            self.interval_lib = interval_lib.IntervalLib(start_address=address, total_size=byte_size)

# Each Core get allocated with a memory-range, to be used for code and data allocations. initial size is 2G per core.
# each memory-range maintains internal interval-list, and have a preserve base-reg to work with.
class MemoryRange:
    def __init__(self, core: str, address: int, byte_size: int):
        # Initially, the entire block is
        self.address = address
        self.byte_size = byte_size
        self.base_reg = None # will be set later and can be modified during the test

