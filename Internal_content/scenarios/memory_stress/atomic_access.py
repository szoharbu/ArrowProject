import random
from Arrow_API import AR
from Arrow_API.resources.memory_manager import MemoryManager_API as MemoryManager
from Arrow_API.resources.register_manager import RegisterManager_API as RegisterManager
from Utils.configuration_management import Configuration


@AR.scenario_decorator(random=True, )
def atomic_64b_store():
    AR.comment("inside atomic_64b_store")

    counter = 10
    block_size = counter * 64
    memory_block = MemoryManager.MemoryBlock(name="memory_block", byte_size=block_size, alignment=4)

    #mem = MemoryManager.Memory(memory_block=memory_block, memory_block_offset=0)
    reg = RegisterManager.get_and_reserve(reg_type="gpr")
    qreg1 = RegisterManager.get(reg_type="simd_int")
    qreg2 = RegisterManager.get(reg_type="simd_int")
    qreg3 = RegisterManager.get(reg_type="simd_int")
    qreg4 = RegisterManager.get(reg_type="simd_int")
    
    AR.asm(f"ldr {reg}, {memory_block.get_label()}")

    with AR.Loop(counter=10):

        AR.generate(instruction_count=random.randint(3, 5))
        AR.asm("DSB sy")
        AR.asm(f"stp {qreg1}, {qreg2}, [{reg}]")
        AR.asm(f"stp {qreg3}, {qreg4}, [{reg}, #32]")
        AR.asm(f"add {reg}, {reg}, #64")
        AR.asm("DSB sy")
        AR.generate(instruction_count=random.randint(3, 5))

    RegisterManager.free(reg)