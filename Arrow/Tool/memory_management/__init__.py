from Tool.memory_management.memory_segments import MemoryRange, MemorySegment

"""
Memory Management Module
========================

Overview
--------
This module provides a structured hierarchy for managing memory resources in various execution platforms. 
It supports both `baremetal` and `linker` execution modes and offers granular control over memory allocation 
and usage. The design ensures flexibility in handling different memory types and addresses various needs, 
from large sequential blocks to randomly allocated shared memory.

Features include:
- A robust `MemoryManager` to handle allocation, extraction, and pooling.
- Flexible handling of `MemorySegment` and `MemoryBlock` objects for custom memory configurations.
- Efficient address management in `baremetal` mode using intervals.
- Seamless generation of assembly-compatible `.data` and `.bss` sections through `DataUnit`.

Classes and Responsibilities
----------------------------
1. MemoryManager
   - Central controller for memory resources.
   - Allocates memory segments into pools: `code`, `data_shared`, `data_preserve`, and `boot`.
   - In `baremetal` mode, finds available intervals during `data_memory` extraction.
   - APIs:
     - allocate_memory_segment() - Allocate a Code or Data segment  
     - get_segments() - Retrieve list of MemorySegments by `pool_type`.
     - get_segment() - Retrieve individual `MemorySegment` by name.
     - get_data_memory() - Allocate specific `dataUnit`.
     - get_used_data_memory() - provide existing shared `dataUnit`.

2. MemorySegment
   - Represents a pool of memory (`boot`, `code`, `data_shared`, `data_preserve`).
   - Contains a list of `MemoryBlock` objects.
   - Characteristics:
     - Blocks may not be sequential.
     - In `baremetal` mode, initial memory range intervals are enforced.

3. MemoryBlock
   - Represents a chunk of memory for data operands.
   - Characteristics:
     - Suitable for sequential, overlapping, or flexible block access.
     - Size is flexible (not constrained to operand sizes like 8, 16, 32, etc.).
     - Supports `data_shared` and `data_preserve` types.
     - Initialized with `init_value` and assigned a unique label.

4. Memory
   - Represents a memory operand used in instructions.
   - Can be created within a `MemoryBlock` (inherits its properties) or independently.
   - Independent `Memory` instances generate their own `MemoryBlock` wrapper.
   - Shared `Memory` can be allocated randomly in an existing block.

5. Interval
   - Used in `baremetal` mode for address management.
   - Ensures non-overlapping preserved memory.
   - Allocates memory efficiently within a defined range.

6. DataUnit
   - Final representation of memory structures in assembly.
   - Converts segments, blocks, and memories into `.data` or `.bss` entries.
   - Holds all labels, addresses, and `init_value` data.

Glossary
--------
- `MemoryManager`: The central class managing memory segments and blocks.
- `MemorySegment`: A container for related memory blocks, categorized by type.
- `MemoryBlock`: A contiguous block of memory used for data operands.
- `Memory`: The smallest memory operand object used in instructions.
- `Interval`: A utility class for managing address ranges in `baremetal` mode.
- `DataUnit`: The low-level representation of memory structures in assembly code.
- `baremetal`: Execution mode where memory addresses and ranges are explicitly managed.
- `linker`: Execution mode where the memory layout is determined by the linker, generating ELF files.


"""







'''
the hierarchy is as follow:
- a memory manager that control all the memory resources. the manager is responsible to allocate memory segments into pools (code/data_shared/date_preserve/boot), has APIs to get block (by name) or blocks (by pool_type) or extract specific data_memory.
when running in 'baremetal' execution_platform, extracting the data_memory is responsible for finding an available interval 
- a MemorySegment can be of boot, code, data_shared, data_preserve type, and hold a list of all the memoryBlocks that reside inside it. 
the inner memoryBlocks inside the Segment are not necessarily sequential.
in 'baremetal' mode, each block has an initial memory range interval, and all smaller memories inside it should be inside that range. 
- a MemoryBlock is the smaller chunk of memory. the main usage of memory-block is when we require a large sequential block that can be used for smaller access (wither sequential, overlying and such), the MemoryBlock can be of any size and is not limited to common operand size (8,16,32,64,128,256,512).
a MemoryBlock is only for Data operand, and can be either shared or preserve. 
a MemoryBlock can get init_value as input, and will have a unique label that in most cases will be used for all smaller access via label+offset 

- a Memory is the object used for memory operand inside instruction, and it the most commonly used API to ask for memory. 
a memory can be generate from withing a memoryBlock ( and in this case will get his type, init_value, unique_label ) or without a parent memoryBlock ( and in this case a memoryBlock will be generated just to wrap it , for this usage we allow Memory to receive init_value as inputs) 
a Memory is only for Data operand, and can be either shared or preserve. 
a shared Memory without a specific parent MemoryBlock can randomly be allocated inside a pre-existing MemoryBlock.

- an interval, used for baremetal memory allocation, to allocate memory addresses and to make sure two preserved memories dont overlap one another.  
- a DataUnit is the smallest object that hold all the labels, addresses, init_values of all the above, and its what eventually get translated into the assembly level as either a .data or .bss entries 
'''