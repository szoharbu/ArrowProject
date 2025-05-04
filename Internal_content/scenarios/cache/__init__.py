import random
from Utils.configuration_management import Configuration
from Arrow_API import AR
from Arrow_API.resources.memory_manager import MemoryManager_API as MemoryManager
from Arrow_API.resources.register_manager import RegisterManager_API as RegisterManager


@AR.scenario_decorator(random=True, priority=Configuration.Priority.MEDIUM, tags=[Configuration.Tag.DISPATCH])
def simple_cache_scenario():
    '''
    Repeatedly load/store memory across cache lines to stress data cache behavior.
    Triggers cache fills, evictions, and potential line conflicts using stride access.
    '''

    block_size = 100
    stride = 8
    counter = block_size // stride

    base_reg = RegisterManager.get_and_reserve(reg_type="gpr")
    offset_reg = RegisterManager.get_and_reserve(reg_type="gpr")
    address_reg = RegisterManager.get_and_reserve(reg_type="gpr")
    data_reg = RegisterManager.get(reg_type="gpr")  # no need to reserve, can be overwritten
    mem_block = MemoryManager.MemoryBlock(name="cache_stress_block", byte_size=block_size, alignment=8, shared=True)

    AR.asm(f"ldr {base_reg}, ={mem_block.unique_label}")
    AR.asm(f"mov {offset_reg}, #0")

    # setting counter to be mem_block.byte_size / 8
    with AR.Loop(counter=counter):
        AR.asm(f"add {address_reg}, {base_reg}, {offset_reg}", comment="base + offset")
        AR.asm(f"ldr {data_reg}, [{address_reg}]", comment="load from memory")
        AR.generate(instruction_count=2, dest=data_reg, comment="randonly touch the data")
        AR.asm(f"str {data_reg}, [{address_reg}]", comment="store back to memory")
        AR.asm(f"add {offset_reg}, {offset_reg}, #64", comment="increment offset")

    RegisterManager.free(address_reg)
    RegisterManager.free(offset_reg)
    RegisterManager.free(base_reg)

# _start:
#     ldr x0, =data_block          // Base address
#     mov x1, #0                   // Loop counter
#     mov x2, #64                  // Stride: 64 bytes (cache line)
#     mov x3, #64                  // Number of iterations

# loop:
#     add x4, x0, x1               // x4 = base + offset
#     ldr x5, [x4]                 // Load from memory (cause cache load)
#     add x5, x5, #1               // Do some arithmetic
#     str x5, [x4]                 // Store back (write to cache)
#     add x1, x1, x2               // Increment offset by cache line size
#     subs x3, x3, #1              // Decrement loop counter
#     bne loop