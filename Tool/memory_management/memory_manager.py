import random
from typing import List, Dict

from Utils.configuration_management import Configuration, get_config_manager
from Utils.logger_management import get_logger
from Tool.asm_blocks import DataUnit

from Tool.memory_management.memory_segments import MemorySegment, CodeSegment, DataSegment, MemoryRange
from Tool.memory_management.memory_block import MemoryBlock
from Tool.memory_management import interval_lib

class MemoryManager:
    def __init__(self, memory_range:MemoryRange):
        """
        Memory manager class to manage a pool of memory segments.
        """
        logger = get_logger()
        logger.info("======================== MemoryManager")

        self.memory_range = memory_range

        # Initialize the memory library with the provided memory_range
        self.interval_lib = interval_lib.IntervalLib(start_address=self.memory_range.address, total_size=self.memory_range.byte_size)
        self.memory_segments: List[MemorySegment] = []
        self.pool_type_mapping: Dict[Configuration.Memory_types, List[MemorySegment]] = {}  # To map pool types to blocks


    def allocate_memory_segment(self, name: str, byte_size:int, memory_type:Configuration.Memory_types)->MemorySegment:
        """
        Allocate a segment of memory for either code or data
        :param name:ste: name of the segment
        :param byte_size: Size of the segment.
        :param memory_type:Memory_types: type of the segment.

        :return: Allocated memory segment.
        """

        for segment in self.memory_segments:
            if segment.name == name:
                raise ValueError(f"Memory segment with name '{name}' already exists.")

        segment_start, segment_size = self.interval_lib.allocate(byte_size)

        if (memory_type == Configuration.Memory_types.CODE) \
            or (memory_type == Configuration.Memory_types.BOOT_CODE) \
            or (memory_type == Configuration.Memory_types.BSP_BOOT_CODE):
            memory_segment = CodeSegment(name=name, address=segment_start, byte_size=segment_size, memory_type=memory_type)
        else:
            memory_segment = DataSegment(name=name, address=segment_start, byte_size=segment_size, memory_type=memory_type)

        self.memory_segments.append(memory_segment)

        # Map the segment to the pool type
        if memory_type not in self.pool_type_mapping:
            self.pool_type_mapping[memory_type] = []
        self.pool_type_mapping[memory_type].append(memory_segment)

        return memory_segment


    # def add_block_to_pools(self, block: MemoryBlock, pool_type: Memory_types):
    #     """
    #     Add a new memory block to the manager.
    #
    #     Args:
    #         block (CodeBlock): The given memory block.
    #         pool_type (str): The pool type (e.g., 'code', 'data_share' or 'data_preserve').
    #     """
    #     if not isinstance(block, CodeBlock):
    #         raise ValueError("invalid block type.")
    #
    #     if not isinstance(pool_type, Memory_types):
    #         raise ValueError(f"expected pool type from Memory_pools, invalid type {type(pool_type)}.")
    #
    #     self.memory_blocks.append(block)
    #
    #     # Map the block to the pool type
    #     if pool_type not in self.pool_type_mapping:
    #         self.pool_type_mapping[pool_type] = []
    #     self.pool_type_mapping[pool_type].append(block)


    def get_segments(self, pool_type:[Configuration.Memory_types | list[Configuration.Memory_types]]) -> List[MemorySegment]:
        """
        Retrieve memory segments based on specific attributes.

        Args:
            pool_type [Memory_types|list[Memory_types]]: Filter segments by pool type, can receive one or list of many.

        Returns:
            List[MemorySegment]: A list of memory segments that match the criteria.
        """
        logger = get_logger()
        # If `pool_type` is not a list, wrap it in a single-element list
        if not isinstance(pool_type, list):
            pool_types = [pool_type]
        else:
            pool_types = pool_type

        filtered_segmentss = []
        for pool_type in pool_types:
            if not isinstance(pool_type, Configuration.Memory_types):
                logger.warning("ID of pool_type's type:", id(type(pool_type)))
                logger.warning("ID of Configuration.Memory_types:", id(Configuration.Memory_types))
                raise ValueError(f"Invalid pool type {pool_type}.")
            # Filter blocks based on pool_type
            if pool_type in self.pool_type_mapping:
                filtered_segmentss = filtered_segmentss + [segment for segment in self.memory_segments if segment in self.pool_type_mapping[pool_type]]

        if not filtered_segmentss:
                raise ValueError("No segments available to match the query request.")

        return filtered_segmentss

    def get_segment(self, segment_name:str) -> MemorySegment:
        """
        Retrieve a memory segment based on given segment name.

        Returns:
            MemorySegment: A memory segments that match the criteria.
        """

        for segment in self.memory_segments:
            if segment.name == segment_name:
                return segment
        raise ValueError(f"No segment available to match the name requested {segment_name}.")


    def get_segment_dataUnit_list(self, segments_name:str) -> list[DataUnit]:
        """
        Retrieve DataUnit list of memory segment based on given segment name.

        Returns:
            list[DataUnit]: A list of the memory segment DataUnits
        """
        segment = self.get_segment(segments_name)
        if segment.memory_type is not Configuration.Memory_types.DATA_SHARED and segment.memory_type is not Configuration.Memory_types.DATA_PRESERVE:
            raise ValueError(f"Invalid segment type {segment.memory_type}. Segment need to be of type DATA_SHARED or DATA_PRESERVE.")
        return segment.data_units_list

    def allocate_data_memory(self, name:str, memory_block_id:str, pool_type:Configuration.Memory_types, byte_size:int=8, init_value_byte_representation:list[int]=None, alignment:int=None) -> DataUnit:
        """
        Retrieve data memory operand from the given pools .

        Args:
            pool_type (Memory_types): either 'share' or 'preserve'.
            byte_size (int): size of the memory operand.
        Returns:
            memory: A memory operand from a random data block.
        """
        config_manager = get_config_manager()
        execution_platform = config_manager.get_value('Execution_platform')

        if pool_type not in [Configuration.Memory_types.DATA_SHARED, Configuration.Memory_types.DATA_PRESERVE]:
            raise ValueError(f"Invalid memory type {pool_type}, type should only be DATA_SHARED or DATA_PRESERVE")

        if pool_type is Configuration.Memory_types.DATA_SHARED and init_value_byte_representation is not None:
            raise ValueError(f"Can't initialize value in a shared memory")

        data_segments = self.get_segments(pool_type)
        selected_segment = random.choice(data_segments)

        if execution_platform == 'baremetal':
            if pool_type is Configuration.Memory_types.DATA_SHARED:
                '''
                When DATA_SHARED is asked, the heuristic is as following:
                - randomly select a block
                - randomly select an offset inside that block
                '''
                start_block = selected_segment.address
                end_block = selected_segment.address + selected_segment.byte_size
                offset_inside_block = random.randint(start_block, end_block - byte_size)
                address = offset_inside_block
            else: # pool_type is Configuration.Memory_types.DATA_PRESERVE:
                '''
                When DATA_PRESERVE is asked, the heuristic is as following:
                - Extract interval from the inner interval_lib
                '''
                mem_start, mem_size = selected_segment.interval_lib.allocate(byte_size)
                address = mem_start
        else:  # 'linked_elf'
            address = None

        data_unit = DataUnit(name=name, memory_block_id=memory_block_id, address=address, byte_size=byte_size,memory_segment_id=selected_segment.name, init_value_byte_representation=init_value_byte_representation, alignment=alignment)
        selected_segment.data_units_list.append(data_unit)

        return data_unit


    def get_used_memory_block(self, byte_size:int=8) -> [MemoryBlock|None]:
        """
        Retrieve data memory operand from the existing pools.

        Args:
            byte_size (int): size of the memory operand.
        Returns:
            DataUnit: A memory operand from a random data block.
        """

        # extract all shared memory-blocks with byte_size bigger than 'byte-size'
        valid_memory_blocks = []

        data_shared_segments = self.get_segments(Configuration.Memory_types.DATA_SHARED)
        for segment in data_shared_segments:
            for mem_block in segment.memory_block_list:
                if mem_block.byte_size >= byte_size:
                    valid_memory_blocks.append(mem_block)

        if not valid_memory_blocks:
            return None

        selected_memory_block = random.choice(valid_memory_blocks)

        return selected_memory_block
