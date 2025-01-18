import random

from Arrow_API import AR
from Arrow_API.resources.memory_manager import MemoryManager_API as MemoryManager
from Arrow_API.resources.register_manager import RegisterManager_API as RegisterManager

from Utils.configuration_management import Configuration


Configuration.Knobs.Config.core_count.set_value(1)
Configuration.Knobs.Template.scenario_count.set_value(3)
Configuration.Knobs.Template.scenario_query.set_value({"direct_scenario":40, "direct_memory_scenario":59,Configuration.Tag.REST:1})


@AR.scenario_decorator(random=True, priority=Configuration.Priority.MEDIUM, tags=[Configuration.Tag.FEATURE_A, Configuration.Tag.SLOW])
def direct_memory_scenario():
    AR.comment("inside direct_memory_scenario")
    mem1 = MemoryManager.Memory()
    mem2 = MemoryManager.Memory(name='mem2_shared', shared=True)
    mem_block = MemoryManager.MemoryBlock(name="blockzz100",byte_size=20, shared=True)
    mem_block2 = MemoryManager.MemoryBlock(name="blockzz150",byte_size=25, shared=True)
    mem_block3 = MemoryManager.MemoryBlock(name="blockzz200",byte_size=100, shared=True)
    mem5 = MemoryManager.Memory(name='mem5_partial', memory_block=mem_block, memory_block_offset=2, byte_size=4, shared=True)
    mem6 = MemoryManager.Memory(name='mem6_partial', memory_block=mem_block2, memory_block_offset=14, byte_size=4, shared=True)
    instr = AR.generate(src=mem5)
    #instr2 = AR.asm(f'mov {mem2}, rax')
    instr = AR.generate(src=mem6)
    for _ in range(100):
        instr = AR.generate()


@AR.scenario_decorator(random=True, priority=Configuration.Priority.MEDIUM, tags=[Configuration.Tag.FEATURE_A, Configuration.Tag.SLOW])
def direct_scenario():
    AR.comment("inside direct_scenario")

    AR.generate(instruction_count=30)

    #array = AR.MemoryArray("my_array", [10, 20, 30, 40, 50])

    # AR.comment("doing EventTrigger flow")
    # with AR.EventTrigger(frequency=Configuration.Frequency.LOW):
    #     AR.asm("nop", comment="simple nop instruction")

    AR.comment("store-load memory")
    mem = MemoryManager.Memory(init_value=0x456)
    reg = RegisterManager.get()
    AR.generate(dest=mem, comment=f" store instruction ")
    AR.generate(src=mem, comment=f" Load instruction ")
    AR.generate(dest=reg, comment=f" reg dest ")
    AR.generate(src=reg, comment=f" reg src ")
    AR.generate(src=reg, dest=mem, comment=f" src reg dest mem ")
    AR.generate(src=mem, dest=reg, comment=f" src mem dest reg ")


    AR.comment("same memory stress with load store of different size")
    mem = MemoryManager.Memory(init_value=0x123)
    for _ in range(5):
        action = AR.choice(values=["load","store"])
        size = AR.choice(values=[1,2,4,8])
        offset = random.randint(0, mem.byte_size - size)
        #partial_mem = mem.get_partial(byte_size=size, offset=offset)
        if action == "load":
            AR.generate(src=mem, comment=f" Load instruction ")
        else: # store
            AR.generate(dest=mem, comment=f" Store instruction ")

    loop_count = AR.rangeWithPeak(10,20,peak=12)

    with AR.Loop(counter=loop_count, counter_direction='increment'):
        AR.comment("inside Loop scope, generating 5 instructions")
        AR.generate(instruction_count=50)

    AR.comment("outside of Loop scope, generating 'load mem, reg' instruction")
    mem1 = MemoryManager.Memory(name="direct_mem", init_value=0x12345678)
    reg = RegisterManager.get_and_reserve()
    if Configuration.Architecture.x86:
        AR.generate(src=mem1, dest=reg)
    else:
        AR.generate(src=mem1, dest=reg, query=(AR.Instruction.group == "load" ))
    RegisterManager.free(reg)

    # if Configuration.Architecture.x86:
    #     mem2 = mem1.get_partial(byte_size=2, offset=1)
    #     AR.asm(f"mov {mem2}, 0x1234")


@AR.scenario_decorator(random=False, priority=Configuration.Priority.LOW, tags=[Configuration.Tag.FEATURE_A, Configuration.Tag.SLOW])
def direct_array_scenario():
    AR.comment("inside direct_array_scenario")

    from Tool.asm_libraries.memory_array.memory_array import MemoryArray

    mem_array = MemoryArray("my_array", [10, 20, 30, 40, 50])
    loop_count = 20
    with AR.Loop(counter=loop_count, counter_direction='increment'):
        used_reg = RegisterManager.get_and_reserve()

        AR.comment(f"zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz load to {used_reg}")
        MemoryArray.load_element(used_reg)
        AR.comment(f"zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz store to {used_reg}")
        MemoryArray.store_element(used_reg)
        AR.comment("zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz increment element")
        MemoryArray.next_element(1)
        AR.comment("zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz")

        RegisterManager.free(used_reg)

