import random
from Arrow_API import AR
from Utils.configuration_management import Configuration
from Arrow_API.resources.register_manager import RegisterManager_API as RegisterManager
from Arrow_API.resources.memory_manager import MemoryManager_API as MemoryManager


@AR.scenario_decorator(random=True, priority=Configuration.Priority.MEDIUM, tags=[Configuration.Tag.POWER])
def tc1_entry_scenario():
    '''
    randomize the TC1 entry sleep flavor and generate the corresponding instruction
    '''
    AR.comment("inside tc1_entry_scenario")
    sleep_flavor = AR.choice(values={"wfi": 10, "wfe": 10, "wfit": 10, "wfet": 10})
    enter_sleep_state(sleep_depth="tc1", sleep_flavor=sleep_flavor)


@AR.scenario_decorator(random=True, priority=Configuration.Priority.MEDIUM, tags=[Configuration.Tag.POWER])
def tc7_entry_scenario():
    '''
    randomize the TC7 entry sleep flavor and generate the corresponding instruction
    '''
    AR.comment("inside tc7_entry_scenario")
    sleep_flavor = AR.choice(values={"wfi": 10, "wfe": 10, "wfit": 10, "wfet": 10})
    enter_sleep_state(sleep_depth="tc7", sleep_flavor=sleep_flavor)


# @AR.scenario_decorator(random=False, priority=Configuration.Priority.MEDIUM, tags=[Configuration.Tag.POWER])
# def cross_thread_PM_stress_scenario():
#     '''
#     randomize the cross thread PM instruction and generate the corresponding instruction
#     '''
#     num_steps = random.randint(3, 5)
#     for i in range(num_steps):
#         for core in Configuration.get_cores():
#             with AR.Core(core):
#                 # setting a barrier to ensure that all cores are at the same step
#                 AR.barrier(barrier_name=f"cross_thread_PM_stress_scenario_step_{i}")

#                 action = AR.choice(values={"tc1": 10, "tc7": 10, "sev":5, "random_instr": 20})
#                 AR.comment(f"step: {i} - core: {core} - action: {action}")
#                 if action == "tc1":
#                     tc1_entry_scenario()
#                 elif action == "tc7":
#                     tc7_entry_scenario()
#                 elif action == "sev":
#                     AR.asm(f"sev", comment="Send event to all cores")
#                 else:
#                     AR.generate(instruction_count=random.randint(5, 10))


def enter_sleep_state(sleep_depth=None, sleep_flavor=None):
    if sleep_depth is None:
        sleep_depth = AR.choice(values={"tc1": 40, "tc7": 60})

    if sleep_flavor is None:
        sleep_flavor = AR.choice(values={"wfi": 10, "wfe": 10, "wfit": 10, "wfet": 10})

    sleep_depth = "tc1"
    sleep_flavor = "wfit"

    if sleep_depth == "tc7":
        AR.asm(f"XXX", comment="Set relevant bit to indicate entry into TC7")

    if sleep_flavor == "wfi":
        raise ValueError("wfi flavor is currently not supported as it require Interrupts")
    elif sleep_flavor == "wfe":
        AR.asm(f"wfe", comment="Wait for event (halts until an event occurs)")
    elif sleep_flavor == "wfit":
        wfxt_timer_delay = random.randint(100, 1000)
        reg = RegisterManager.get_and_reserve(reg_type="gpr")
        reg_2 = RegisterManager.get_and_reserve(reg_type="gpr")

        AR.asm(f"mrs {reg}, cntpct_el0", comment="Read Time step counter")
        AR.asm(f"mov {reg_2}, #{wfxt_timer_delay}", comment="Move the delay value to the register")
        AR.asm(f"add {reg}, {reg}, {reg_2}", comment=f"adding {wfxt_timer_delay} to TSC value")
        AR.asm(f"wfit {reg}", comment="go to sleep zzzz")

        RegisterManager.free(reg)
        RegisterManager.free(reg_2)

    elif sleep_flavor == "wfet":
        AR.asm(f"wfet", comment="Wait for event and interrupt (halts until an event or interrupt occurs)")


def SPE_setup():
    '''
    Setup the SPE for the current core
    '''

    AR.comment("----- inside SPE_setup")

    memory_buffer = MemoryManager.MemorySegment(name="SPE_buffer", byte_size=0x1000,
                                                memory_type=Configuration.Memory_types.DATA_PRESERVE)
    print(f"memory_buffer: {memory_buffer}")
    print(f"memory_buffer.address: {hex(memory_buffer.address)}")

    reg = RegisterManager.get_and_reserve(reg_type="gpr")
    AR.asm(f"adrp {reg}, {memory_buffer.name}_bss", comment=f"Load the page address containing {memory_buffer.name}")
    AR.asm(f"add {reg}, {reg}, #:lo12:{memory_buffer.name}_bss",
           comment=f"Add the offset within the page to get the exact address of {memory_buffer.name}")

    # AR.asm(f"MSR PMBPTR_EL1, {reg}", comment="Write the memory buffer.start address to the PMB pointer")

    # AR.asm(f"ldr {reg}, #0")
    # AR.asm(f"MSR PMBSR_EL1, {reg}", comment="Write the value of x0 to the PMBSR_EL1")

    # # mov  x1, #0x2021
    # # movk  x1, #0x6d87, lsl #16
    # # movk  x1, #0xcc, lsl #32
    # AR.asm(f"MSR PMBLIMITR_EL1, {reg}")

    RegisterManager.free(reg)

    # def msr_write(sysreg, value):
    #     AR.asm(f"mov {reg}, {value}", comment="Write the PMB pointer")
    #     AR.asm(f"MSR {sysreg}, {reg}", comment="Write the PMB pointer")

    # def msr_read(sysreg, reg):
    #     AR.asm(f"MRS {reg}, {sysreg}", comment="Read the PMB pointer")


@AR.scenario_decorator(random=True, )
def WFIT_CROSS_SPE_scenario():
    AR.comment("inside WFIT_CROSS_SPE_scenario")

    with AR.SwitchState(state="core_0"):
        enter_sleep_state()

    with AR.SwitchState(state="core_1"):
        SPE_setup()
