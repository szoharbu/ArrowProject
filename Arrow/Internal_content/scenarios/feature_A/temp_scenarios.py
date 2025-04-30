from Arrow_API import AR
from Arrow_API.resources.memory_manager import MemoryManager_API as MemoryManager
from Arrow_API.resources.register_manager import RegisterManager_API as RegisterManager

from Utils.configuration_management import Configuration

@AR.scenario_decorator(random=True, priority=Configuration.Priority.MEDIUM, tags=[Configuration.Tag.FEATURE_A, Configuration.Tag.SLOW])
def loop_scenario():
    reg1 = RegisterManager.get_and_reserve()
    loop_counter = AR.choice(values = {10:90,20:10})
    with AR.Loop(counter=loop_counter, counter_direction='increment'):
        AR.asm(f"nop")
        reg2 = RegisterManager.get_and_reserve()
        AR.generate(instruction_count=5)
        RegisterManager.free(reg2)
    RegisterManager.free(reg1)



@AR.scenario_decorator(random=True, priority=Configuration.Priority.MEDIUM)
def generate_random_instructions():
    some_label = AR.Label(postfix="some_label")
    AR.asm(f"{some_label}:")
    for _ in range(5):
        AR.generate()


def random_precondition():
    value = AR.choice(values={True:70,False:30})
    return value

@AR.scenario_decorator(random=True, priority=Configuration.Priority.MEDIUM, tags=[Configuration.Tag.FEATURE_A, Configuration.Tag.FAST], precondition=lambda:random_precondition())
def mid_prio_basic():
    some_label = AR.Label(postfix="some_label")
    AR.asm(f"{some_label}:")
    for _ in range(5):
        AR.generate()

@AR.scenario_decorator(random=True, priority=Configuration.Priority.HIGH, precondition=lambda:random_precondition())
def random_precondition_scenario():
    AR.comment("random_precondition_scenario")
    for _ in range(5):
        AR.generate()

@AR.scenario_decorator(random=False, priority=Configuration.Priority.MEDIUM, tags=[Configuration.Tag.FEATURE_A])
def not_a_random_scenario():
    Sources.logger.warning("Scenario: not_a_random_scenario")
    raise ValueError("This scenario should not be selected randomly.")
