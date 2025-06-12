import random
from Utils.configuration_management import Configuration
from Arrow_API import AR
from Arrow_API.resources.memory_manager import MemoryManager_API as MemoryManager
from Arrow_API.resources.register_manager import RegisterManager_API as RegisterManager


@AR.scenario_decorator(random=True, priority=Configuration.Priority.MEDIUM, tags=[Configuration.Tag.HRO])
def Basic_hro_scenario():
    '''
    Explanation: Allocating two memory operands, one with 32bit data and one with 64bit data. inside a loop keep loading the 32bit data, and in rare probability switch to the 64bit data.
    The goal is get the HRO prediction to learn and expect a 32bit data, and occually in the same load LIP switch to the 64bit data.
    '''
    AR.comment("inside Basic_hro_scenario")
    memory_32b_data = MemoryManager.Memory(init_value=0x12345678)
    memory_64b_data = MemoryManager.Memory(init_value=0x5555555555555555)


    with AR.Loop(counter=100):
        reg = RegisterManager.get_and_reserve(reg_type = "gpr")
        reg1 = RegisterManager.get(reg_type = "gpr")

        AR.asm(f"ldr {reg}, ={memory_32b_data.get_address()}")

        with AR.EventTrigger(frequency=Configuration.Frequency.LOW):
            AR.asm(f"nop")
            AR.asm(f"ldr {reg}, ={memory_64b_data.get_address()}")

        AR.asm(f"ldr {reg1}, [{reg}]")

    RegisterManager.free(reg)