import random
from Arrow_API import AR
from Utils.configuration_management import Configuration
from Arrow_API.resources.memory_manager import MemoryManager_API as MemoryManager
from Arrow_API.resources.register_manager import RegisterManager_API as RegisterManager


# TODO:: PGT
    # refactor memory manager to support paging, and add a new memory manager that will be used for paging.
    # integrate the PGT with the new memory manager
    # solve PGT ISS issue with section
    # add a logic that auto-generate section-start
    # replace ARM_ASSEMBLY with GENERIC - should be more simlar to GNU AS

# Done:: debug code branching issue with WFIT (thread0 is waking after sleep state to threa1 code)
# Done:: Add ability to use "with core" that will allow same scenario to address multiple cores
# Done:: Need to add ability for Memblock to me aligned, using .align(4) or .align(8), and set some default
# TODO:: add logic to check that every get_and_reserve is freed at the end of the scenario scope.
# TODO:: create an lst like file, that shows both lips from the objdump and the asm+comment+file+line from the asm file
# TODO:: Barrier
    # Done:: Work on barrier , add barrier manager to take care of uniuq names and mem addresses
    # Done:: currently the barrier vector is hardcoded for 2 cores. need to make it dynamic
    # Done:: Need to think how to handle the barrier vector synamic init? probably gives it a special naming convention, like barrier_vector_memory, and at asm creation look for it and modify the value accordingly.
    # TODO:: End post_init, and end_test barrier, make sure the TBOX setting has barrier so only the last thread should write test pass. Or else it will create overlapping!
# TODO:: Memory
    # TODO:: continue working on Memory at generate.py
    # TODO:: Enable memory instrutions, currently disabled
    # TODO:: Memory block setting in asm file
# TODO:: Asm_template parser
# TODO:: Stack, handle it properly with code allocation and stack pointer, possibly a stack manager
# Done:: each core should have a unique number, that be used for the barrier and BSP logic. at the moment I'm using core.name
# TODO:: LOR manager and basic usage.


Configuration.Knobs.Config.core_count.set_value(2)
Configuration.Knobs.Template.scenario_count.set_value(10)
#Configuration.Knobs.Template.scenario_query.set_value({"simple_cache_scenario":100, "WFIT_CROSS_SPE_scenario": 0, Configuration.Tag.REST: 1})
#Configuration.Knobs.Template.scenario_query.set_value({"random_instructions": 100, "bypass_bursts": 1, Configuration.Tag.REST: 1})
Configuration.Knobs.Template.scenario_query.set_value({"ldstcc_release_rar_check": 100, Configuration.Tag.REST: 1})


@AR.scenario_decorator(random=True, )
def random_instructions():
    AR.comment("inside random_instructions")

    AR.asm("nop")
    import time
    start_time = time.time()
    for _ in range(10):
        AR.generate()
    print(f"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx time= {time.time() - start_time}")
    start_time = time.time()
    for _ in range(40):
        AR.generate(query=(AR.Instruction.mnemonic.contains("ldsetal")))
    print(f"xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx time= {time.time() - start_time}")


    with AR.Loop(counter=10):
        for _ in range(10):
            AR.asm("nop")
#        AR.generate(instruction_count=10)
    
    return 
    for _ in range(10):

        AR.asm("nop")
        AR.generate()
        reg = RegisterManager.get(reg_type="gpr")
        AR.generate(src=reg)
        AR.generate(dest=reg, comment=f"use reg as {reg} as dest")
        RegisterManager.free(reg)

    return

    for _ in range(10):
        mem = MemoryManager.Memory(init_value=random.randint(0, 0xffff))
        AR.generate(query=(AR.Instruction.mnemonic=="ldr"), src=mem, comment="load mem")
        AR.generate(query=(AR.Instruction.mnemonic.contains("str")), dest=mem, comment="store mem")

    AR.generate(instruction_count=5)
    AR.generate(query=(AR.Instruction.steering_class.contains("mx")))
    AR.generate(query=(AR.Instruction.mnemonic.contains("ADC")))

    return 

    reg = RegisterManager.get(reg_type="gpr")
    reg2 = RegisterManager.get(reg_type="gpr")
    AR.asm(f"add {reg}, {reg}, {reg2}", comment=f"adding {reg} = {reg} + {reg2}")

    AR.generate(query=(AR.Instruction.mnemonic.contains("ADC")), src=reg, comment=f"ADC with register {reg} as src")
    # AR.generate(query=(AR.Instruction.mnemonic.contains("ADC")), dest=reg, comment=f"ADC with register {reg} as dest")

    for _ in range(10):
        reg = RegisterManager.get()
        AR.generate(src=reg)


    # AR.Barrier("barrier_1")
    # AR.asm("nop")
    # return

    # for i in range(10):
    #     value = 0x12340+i

    #     # mem = MemoryManager.Memory(init_value=value, byte_size=8)
    #     # AR.generate(src=mem, comment=f"load {hex(value)} to mem")
    #     # AR.generate(dest=mem, comment=f"store {hex(value)} to mem")
        
    #     reg = RegisterManager.get_and_reserve()
    #     ld_mem = MemoryManager.Memory(init_value=value, byte_size=8)
    #     AR.generate(src=ld_mem, dest=reg, query=(AR.Instruction.mnemonic.contains("ldr")))
    #     AR.generate(src=reg, query=(AR.Instruction.mnemonic.contains("str")))
    #     RegisterManager.free(reg)

    # AR.asm("nop")
    # AR.asm("nop")
    # AR.asm("nop")
    
    # return

    # mem = MemoryManager.Memory(init_value=0x1234)
    # AR.generate(src=mem)

    # with AR.Loop(counter=5):
    #     AR.generate(instruction_count=5)
    #     # with AR.EventTrigger(frequency=Configuration.Frequency.RARE):
    #     #     AR.asm("wfi", comment="simple nop instruction")

    # # code_segment = MemoryManager.CodeSegment(name="my_segment", byte_size=100, type="code")
    # # with AR.BranchToSegment(segment_name=code_segment):
    # #     AR.generate(instruction_count=10)

    # # AR.asm(f"nop")



def switch_EL(current_el_level:int, target_el_level:int):

    '''
    Higher → Lower: Always use ERET (exception return).
    Lower → Higher: Trigger an exception (e.g., interrupt, SVC, HVC).
    Direct Jumps (e.g., EL3 → EL0): Technically allowed via ERET, but not recommended (skip initialization steps in intermediate ELs).
    '''

    while current_el_level != target_el_level:
        reg = RegisterManager.get_and_reserve(reg_type="gpr")
        reg2 = RegisterManager.get_and_reserve(reg_type="gpr")

        target_el_label = f"el{target_el_level}_target_address"
        AR.comment(f"Transition from EL{current_el_level} to EL{target_el_level}")

        AR.comment(f"Set the target address in ELR_EL3")
        AR.asm(f"adr {reg}, {target_el_label}")
        AR.asm(f"msr ELR_EL3, {reg}", comment="set ELR_EL3 target address")

        AR.comment(f"Configure the processor state for EL{target_el_level}")
        AR.asm(f"mrs {reg}, SPSR_el3", comment="get SPSR_el3")
        AR.asm(f"bic {reg}, {reg}, #0xf", comment="clear mode bits")
        if target_el_level == 2: SPSR_value = 0x9   # EL2h (AArch64), DAIF=0000 (interrupts enabled)
        elif target_el_level == 1: SPSR_value = 0x5 # EL1h (AArch64), DAIF=0000 (interrupts enabled)
        else: SPSR_value = 0x0                      # EL0h (AArch64), DAIF=0000 (interrupts enabled)
        AR.asm(f"mov {reg2}, #{SPSR_value}") 
        AR.asm(f"orr {reg}, {reg}, {reg2}", comment="set EL2 mode")
        AR.asm(f"msr SPSR_el3, {reg}", comment="set SPSR_el3")

        AR.comment(f"Set the stack pointer in EL{target_el_level}")
        AR.asm(f"adr {reg}, _stack_start")
        AR.asm(f"msr SP_EL{target_el_level}, {reg}", comment="set SP_EL{target_el_level} stack pointer")

        AR.comment(f"Switch to a non-secure state")
        AR.asm(f"mrs x0, scr_el3", comment="Read SCR_EL3")
        AR.asm(f"orr x0, x0, #(1 << 0)", comment="Set NS bit (bit 0)")
        AR.asm(f"msr scr_el3, x0", comment="Update SCR_EL3")
        

        AR.asm("eret")
        AR.asm(f"{target_el_label}:")



        return
        if current_el_level == 3:
            AR.comment("Transition from EL3 to EL2")

            AR.comment(f"Configure the processor state for EL2")
            AR.asm(f"mrs {reg}, SPSR_el3", comment="get SPSR_el3")
            AR.asm(f"bic {reg}, {reg}, #0xf", comment="clear mode bits")
            AR.asm(f"mov {reg2}, #0x9") # EL2h (AArch64), DAIF=0000 (interrupts enabled)
            AR.asm(f"orr {reg}, {reg}, {reg2}", comment="set EL2 mode")
            AR.asm(f"msr SPSR_el3, {reg}", comment="set SPSR_el3")

            AR.comment(f"Set the target address in EL2")
            AR.asm(f"adr {reg}, el2_return_address")
            AR.asm(f"msr ELR_EL3, {reg}", comment="set ELR_EL3 return address")

            AR.comment(f"Set the stack pointer in EL2")
            AR.asm(f"adr {reg}, _stack_start")
            AR.asm(f"msr SP_EL2, {reg}", comment="set SP_EL2 stack pointer")

            AR.comment(f"Switch to a non-secure state")
            AR.asm(f"mrs x0, scr_el3", comment="Read SCR_EL3")
            AR.asm(f"orr x0, x0, #(1 << 0)", comment="Set NS bit (bit 0)")
            AR.asm(f"msr scr_el3, x0", comment="Update SCR_EL3")
            

            AR.asm(f"eret")
            AR.asm("el2_return_address:")
            AR.asm("nop")
            current_el_level = 2
        elif current_el_level == 2:
            if target_el_level == 1:
                AR.comment("Transition from EL2 to EL1")
                AR.asm(f"ADR {reg}, el1_return_address")
                AR.asm(f"MSR ELR_EL2, {reg}")
                AR.asm(f"MSR SPSel, #1")
                AR.asm(f"ERET")
                AR.asm("el1_return_address:")
                current_el_level = 1
            else: 
                AR.comment("Transition from EL2 to EL3")
                current_el_level = 3
        elif current_el_level == 1:
            if target_el_level == 0:
                AR.comment("Transition from EL1 to EL0")
                AR.asm(f"ADR {reg}, el0_return_address")
                AR.asm(f"MSR ELR_EL1, {reg}")
                AR.asm(f"MSR SPSel, #0")
                AR.asm(f"ERET")
                AR.asm("el0_return_address:")
                current_el_level = 0
            else: 
                AR.comment("Transition from EL1 to EL2")
                current_el_level = 2
        else:
            AR.comment("Transition from EL0 to EL1")
            current_el_level = 1



# // At EL3
# // Transition from EL3 to EL2
# MSR ELR_EL3, el2_return_address  // Set return address for EL2
# MSR SPSel, #1                    // Select SP_EL2
# ERET                             // Return to EL2

# // At EL2
# el2_return_address:
# MSR ELR_EL2, el1_return_address  // Set return address for EL1
# MSR SPSel, #1                    // Select SP_EL1
# ERET                             // Return to EL1

# // At EL1
# el1_return_address:
# MSR ELR_EL1, el0_return_address  // Set return address for EL0
# MSR SPSel, #0                    // Select SP_EL0
# ERET                             // Return to EL0

# // At EL0
# el0_return_address:
# MOV X0, X0                       // No-op instruction to indicate we are at EL0



@AR.scenario_decorator(random=True)
def mx_cross_v2g_scenario():
    AR.comment("inside direct_memory_scenario")

    with AR.Loop(counter=random.randint(10, 20)):
        mem = MemoryManager.Memory(memory_type="uc", init_value=0x456)

        AR.comment("inside Loop scope, generating 5 instructions")
        for _ in range(20):
            action = AR.choice(values={"mx": 80, "v2g": 80})
            if action == "mx":
                AR.generate(instruction_count=10, query=(AR.Instruction.steering_class.contain("mx_pred")))
            else:
                AR.generate(query=(AR.Instruction.steering_class.contain("vx_v2x")))


def koko():
    print("koko")


    mem_block = MemoryManager.MemoryBlock(name="block1", byte_size=20)
    mem1 = MemoryManager.Memory(name='mem1_partial1', memory_block=mem_block, memory_block_offset=2, byte_size=4)
    mem2 = MemoryManager.Memory(name='mem1_partial2', memory_block=mem_block, memory_block_offset=14, byte_size=4)

    AR.asm(f"mov {mem1}, 0x1234")
    AR.generate(src=mem2, comment="load mem2")





@AR.scenario_decorator(random=True, priority=Configuration.Priority.MEDIUM,
                       tags=[Configuration.Tag.FEATURE_A, Configuration.Tag.SLOW])
def direct_memory_scenario():
    AR.comment("inside direct_memory_scenario")
    mem1 = MemoryManager.Memory()
    mem2 = MemoryManager.Memory(name='mem2_shared', shared=True)
    mem_block = MemoryManager.MemoryBlock(name="blockzz100", byte_size=20, shared=True)
    mem_block2 = MemoryManager.MemoryBlock(name="blockzz150", byte_size=25, shared=True)
    mem_block3 = MemoryManager.MemoryBlock(name="blockzz200", byte_size=100, shared=True)
    mem5 = MemoryManager.Memory(name='mem5_partial', memory_block=mem_block, memory_block_offset=2, byte_size=4,
                                shared=True)
    mem6 = MemoryManager.Memory(name='mem6_partial', memory_block=mem_block, memory_block_offset=14, byte_size=4,
                                shared=True)
    instr = AR.generate(src=mem5, comment="zzzzzzzzzzzzzzzzz")
    # instr2 = AR.asm(f'mov {mem2}, rax')
    instr = AR.generate(src=mem6)
    for _ in range(100):
        instr = AR.generate()


@AR.scenario_decorator(random=True, priority=Configuration.Priority.MEDIUM,
                       tags=[Configuration.Tag.FEATURE_A, Configuration.Tag.SLOW])
def direct_scenario():
    AR.comment("inside direct_scenario")

    AR.generate(instruction_count=30)

    # array = AR.MemoryArray("my_array", [10, 20, 30, 40, 50])

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
        # Replacing choice with Adaptive_choice, instead of always being 50:50 the adaptive will give wider randomization
        # action = AR.choice(values={"load":50, "store":50})
        values_with_ranges = {"load": (30, 70), "store": (70, 30)}
        action = AR.adaptive_choice(values_with_ranges)
        size = AR.choice(values=[1, 2, 4, 8])
        offset = random.randint(0, mem.byte_size - size)
        # partial_mem = mem.get_partial(byte_size=size, offset=offset)
        if action == "load":
            AR.generate(src=mem, comment=f" Load instruction ")
        else:  # store
            AR.generate(dest=mem, comment=f" Store instruction ")

    loop_count = AR.rangeWithPeak(10, 20, peak=12)

    with AR.Loop(counter=loop_count, counter_direction='increment'):
        AR.comment("inside Loop scope, generating 5 instructions")
        AR.generate(instruction_count=50)

    AR.comment("outside of Loop scope, generating 'load mem, reg' instruction")
    mem1 = MemoryManager.Memory(name="direct_mem", init_value=0x12345678)
    reg = RegisterManager.get_and_reserve()
    if Configuration.Architecture.x86:
        AR.generate(src=mem1, dest=reg)
    else:
        AR.generate(src=mem1, dest=reg, query=(
                    AR.Instruction.group == "load" & AR.Instruction.cyc > 3 & AR.Instruction.streed == "mx_pred"))
    RegisterManager.free(reg)

    # if Configuration.Architecture.x86:
    #     mem2 = mem1.get_partial(byte_size=2, offset=1)
    #     AR.asm(f"mov {mem2}, 0x1234")


@AR.scenario_decorator(random=False, priority=Configuration.Priority.LOW,
                       tags=[Configuration.Tag.FEATURE_A, Configuration.Tag.SLOW])
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

