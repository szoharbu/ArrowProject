from Tool.memory_management.memory_segments import MemoryRange, MemorySegment

"""
Memory Management Module
========================

Overview
--------
This module provides a comprehensive, hierarchical memory management system for various execution platforms.
It supports both `baremetal` and `linked_elf` execution modes with granular control over memory allocation
across virtual and physical address spaces. The architecture enables precise management of memory resources
from page-level allocations to high-level memory segments, blocks, and individual data units.

Features include:
- A multi-layered memory management architecture with clear separation of concerns
- Virtual-to-physical address translation through page tables
- Segmentation of memory into different types (code, data_shared, data_preserve, boot)
- Page-level memory management with explicit tracking of memory pages
- Efficient interval-based allocation for both physical and virtual address spaces
- Support for memory alignment and specialized memory requirements

Architecture and Component Hierarchy
-----------------------------------
The memory management subsystem follows a hierarchical design:

1. Memory Space Manager (Top Level)
   └── Page Table Manager
       └── Memory Manager
           └── Memory Segments
               └── Memory Blocks
                   └── Data Units

Each layer addresses specific concerns of memory management, from physical page allocation
to logical organization of memory regions.

Classes and Responsibilities
----------------------------
1. MemorySpaceManager
   - Top-level controller for the entire memory address space
   - Manages both physical and virtual address spaces across all states
   - Tracks available/used PA and VA intervals for code and data separately
   - Handles memory space allocation requests and coordinates with page table manager
   - APIs:
     - allocate_memory() - Allocates VA space and automatically handles PA mapping
     - allocate_pa_space() - Explicitly allocates physical address space
     - allocate_va_space() - Explicitly allocates virtual address space

2. PageTableManager
   - Manages page tables for virtual-to-physical address translation
   - Creates and maintains page tables for multiple states
   - Handles page allocation, mapping, and permission management
   - Supports different page types (code, data, system, device)
   - APIs:
     - allocate_pages() - Allocates pages of a specific type
     - map_va_to_pa() - Creates mappings between virtual and physical addresses

3. SegmentManager
   - Manages a pool of memory segments with different types
   - Delegates to memory_space_manager for actual memory allocation
   - Provides high-level APIs for memory segment and data unit allocation
   - APIs:
     - allocate_memory_segment() - Allocates a segment of memory (code or data)
     - allocate_data_memory() - Allocates data memory from appropriate segments
     - get_segments() - Retrieves segments by type
     - get_used_memory_block() - Gets existing memory blocks

4. MemorySegment
   - Represents a logical segment of memory (code, data_shared, data_preserve, boot)
   - Contains memory blocks and data units
   - Has allocation information linking it to physical pages
   - Characteristics:
     - Each segment has a specific type and memory range
     - Stores references to the pages that compose it
     - Maintains lists of contained memory blocks and data units

5. MemoryBlock
   - Represents a chunk of memory for data operations
   - Resides within a memory segment
   - Characteristics:
     - Can be of various sizes for flexible memory usage
     - Supports shared or preserved data types
     - Has a unique identifier and may have initialization values

6. DataUnit
   - The final representation of memory for assembly/code generation
   - Contains all necessary information for memory access
   - Characteristics:
     - Has name, address, size, and initialization values
     - Knows its parent memory segment
     - May have alignment requirements

Memory Interval Management
--------------------------
The system uses interval-based allocation to track available memory:

- VA intervals: Track available virtual address space
  - Separate intervals for code and data
  - Managed per state for multi-state support

- PA intervals: Track available physical address space
  - Separate intervals for different memory regions
  - Used to back virtual addresses with physical memory

- Allocation Process:
  1. Request VA space from appropriate interval
  2. Request PA space to back the VA allocation
  3. Map VA to PA through page tables
  4. Return allocation details including page information

Page Management
--------------
Each memory allocation spans one or more pages:

- Pages are the fundamental unit of memory management
- Each page has:
  - A virtual address (VA)
  - A physical address (PA)
  - A type (code, data, system, device)
  - Access permissions
  - Size (architecture-dependent)

- Memory allocations track which pages they cover
- Memory segments store references to their covered pages
- This enables precise tracking of memory usage at the page level

Memory Mapping Workflow
----------------------
1. Application requests a memory segment through SegmentManager
2. SegmentManager delegates to MemorySpaceManager for allocation
3. MemorySpaceManager:
   - Allocates VA space from appropriate interval
   - Allocates PA space to back it
   - Works with PageTableManager to create VA→PA mappings
4. SegmentManager creates a MemorySegment using the allocation
5. Application can create MemoryBlocks and DataUnits within the segment

Correlation Between Components
-----------------------------
- Page → Segment: Each segment knows which pages it spans via segment.allocation.covered_pages
- Segment → Block: Segments contain memory blocks in segment.memory_block_list
- Segment → DataUnit: Segments track data units in segment.data_units_list
- Block → DataUnit: DataUnits reference their parent block via memory_block_id
- DataUnit → Segment: DataUnits reference their parent segment via memory_segment_id

This correlation allows tracing any memory object back to its underlying pages and physical memory.

Glossary
--------
- `MemorySpaceManager`: Top-level manager for all memory spaces (VA/PA) across states
- `PageTableManager`: Manages page tables and VA→PA mappings
- `SegmentManager`: Manages memory segments and provides allocation APIs
- `MemorySegment`: A logical segment of memory with specific type and purpose
- `MemoryBlock`: A contiguous block of memory within a segment
- `DataUnit`: The smallest memory unit with all necessary information for access
- `VA`: Virtual Address - the address seen by the program
- `PA`: Physical Address - the actual hardware memory address
- `Page`: The smallest unit of memory for translation and protection
- `Interval`: A utility for tracking available ranges of addresses
- `baremetal`: Execution mode with explicit memory address management
- `linked_elf`: Execution mode where memory layout is determined at link time


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