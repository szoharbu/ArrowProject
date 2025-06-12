import random
from Arrow_API import AR
from Utils.configuration_management import Configuration
from Arrow_API.resources.memory_manager import MemoryManager_API as MemoryManager
from Arrow_API.resources.register_manager import RegisterManager_API as RegisterManager


# Setting the number of cores (PEs) and scenarios
Configuration.Knobs.Config.core_count.set_value(2)
Configuration.Knobs.Template.scenario_count.set_value(2)

# Setting the scenarios to be used
Configuration.Knobs.Template.scenario_query.set_value({"random_instructions": 100, Configuration.Tag.REST: 1})


@AR.scenario_decorator(random=True)
def random_instructions():
    AR.comment("inside random_instructions")

    # Case 1: generate an assembly loop of 50 iteration, inside the loop generate 3 times the following: one ADC instruciton and 2 instructions from steering class mx
    with AR.Loop(counter=50):
        for _ in range(3):
            AR.generate(query=(AR.Instruction.mnemonic.contains("ADC")))
            AR.generate(query=(AR.Instruction.steering_class.contains("mx")), instruction_count=2)

    # Case 2: generate an assembly ADD instruction, followed by a random instruction that uses the register as its destination 
    reg = RegisterManager.get_and_reserve(reg_type="gpr")
    reg2 = RegisterManager.get(reg_type="gpr")
    AR.asm(f"add {reg}, {reg}, {reg2}", comment=f"adding {reg} = {reg} + {reg2}")
    AR.generate(dest=reg, comment="store reg")

    # free the previously reserved register
    RegisterManager.free(reg)


    # Case 3: generate a memory operand and access it. 
    mem = MemoryManager.Memory(init_value=0x456)
    # print(f"using Mem {mem}") # uncomment if you want to see address and properties of selected memory
    AR.generate(src=mem, comment="load mem")
    AR.generate(dest=mem, comment="store mem")

    # Case 4: a loop with an inner EventTrigger to alternate memory operand for later access 
    mem1 = MemoryManager.Memory(init_value=0x1234)
    mem2 = MemoryManager.Memory(init_value=0x5678)
    reg = RegisterManager.get_and_reserve(reg_type = "gpr")
    
    with AR.Loop(counter=100):
        AR.asm(f"ldr {reg}, ={mem1.get_address()}")

        with AR.EventTrigger(frequency=Configuration.Frequency.LOW):
            AR.asm(f"ldr {reg}, ={mem2.get_address()}")

        tmp_reg = RegisterManager.get(reg_type = "gpr")
        AR.asm(f"ldr {tmp_reg}, [{reg}]")

    RegisterManager.free(reg)