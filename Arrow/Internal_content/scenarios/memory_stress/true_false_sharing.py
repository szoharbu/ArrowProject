import random
from Arrow.Arrow_API import AR
from Arrow.Arrow_API.resources.memory_manager import MemoryManager_API as MemoryManager
from Arrow.Arrow_API.resources.register_manager import RegisterManager_API as RegisterManager
from Arrow.Utils.configuration_management import Configuration

'''
package for True/False sharing scenarios.

'''

@AR.scenario_decorator(random=True, priority=Configuration.Priority.MEDIUM, tags=[Configuration.Tag.MEMORY])
def basic_false_sharing_scenario():
    '''
    This scenario is a simple example of false sharing.
    it create a cross-core memory_block, and allocate it into multiple smaller memory objects while ensuring no overlap.
    then it will randomly split the objects between the two cores, and generate instructions that will access the memory objects.
    '''

    block_size = 0x50
    cross_core_memory_block = MemoryManager.MemoryBlock(name="false_sharing_cross_core_memory_block", byte_size=block_size, cross_core=True)

    pre_core_mem_dict = {"core_0": [], "core_1": []}

    offset = 0
    block_base_address = cross_core_memory_block.get_address()
    
    while offset < block_size:
        mem_byte_size = AR.choice(values={4:30, 8:70})
        
        # Calculate the final address (block base + current offset)
        current_address = block_base_address + offset
        if current_address % mem_byte_size != 0:
            alignment_adjustment = mem_byte_size - (current_address % mem_byte_size)
            offset += alignment_adjustment
        
        if offset + mem_byte_size > block_size:
            break
            
        core = AR.choice(values=["core_0", "core_1"])
        mem = MemoryManager.Memory(name=f"false_sharing_{core}_{hex(offset)}", byte_size=mem_byte_size, memory_block=cross_core_memory_block, memory_block_offset=offset)
        pre_core_mem_dict[core].append(mem)
        
        offset_stride = AR.choice(values={0:50, 2:40, 4:30})
        offset += mem_byte_size + offset_stride
        
    for core in pre_core_mem_dict:
        if len(pre_core_mem_dict[core]) == 0:
            continue
        with AR.SwitchState(state_name=core):
            with AR.Loop(counter=10):
                for _ in range(5):
                    random_mem = AR.choice(values=pre_core_mem_dict[core])
                    AR.generate(src=random_mem)
