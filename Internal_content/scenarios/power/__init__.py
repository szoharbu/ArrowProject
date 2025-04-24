import random
from Arrow_API import AR
from Utils.configuration_management import Configuration
from Arrow_API.resources.register_manager import RegisterManager_API as RegisterManager


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

    if sleep_depth == "tc7":
        AR.asm(f"XXX", comment="Set relevent bit to indicate entry into TC7")

    if sleep_flavor == "wfi":
        AR.asm(f"wfi", comment="Wait for interrupt (halts until an interrupt occurs)")
    elif sleep_flavor == "wfe":
        AR.asm(f"wfe", comment="Wait for event (halts until an event occurs)")
    elif sleep_flavor == "wfit":
        delay = random.randint(10, 100)
        reg = RegisterManager.get(reg_type="gpr")
        AR.asm(f"mov {reg}, {delay}", comment=f"Delay for {delay} cycles")
        AR.asm(f"wfit {reg}", comment="Wait for interrupt and event (halts until an interrupt or event occurs)")
    elif sleep_flavor == "wfet":
        AR.asm(f"wfet", comment="Wait for event and interrupt (halts until an event or interrupt occurs)")
