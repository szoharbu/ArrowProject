import random
from Utils.configuration_management import Configuration
from Arrow_API import AR
# from Arrow_API.resources.memory_manager import MemoryManager_API as MemoryManager
from Arrow_API.resources.register_manager import RegisterManager_API as RegisterManager


@AR.scenario_decorator(random=True, priority=Configuration.Priority.MEDIUM, tags=[Configuration.Tag.DISPATCH])
def is_mx_v2g_cross_scenario():
    '''
    Explanation: MX and V2G share the WB buffer, and as V2G has higher priority, once arrived into the Issue pipe it will cancle any existing MX instruction and cause it to start over.
    stressing this flow might trigger starvation of the MX instruction. If that MX instruction become oldest and get starved for few cycles, a livelock will kicks-in and force it into the pipeline
    '''
    AR.comment("inside is_mx_v2g_cross_scenario")
    with AR.Loop(counter=10):
        for _ in range(10):
            steering_class = AR.choice(values={"mx": 20, "mx_pred": 40, "vx_v2g": 40})
            AR.generate(query=(AR.Instruction.steering_class.contains(steering_class)))


@AR.scenario_decorator(random=True, priority=Configuration.Priority.MEDIUM,
                       tags=[Configuration.Tag.DISPATCH, Configuration.Tag.BRANCH])
def is_bx_stress_scenario():
    '''
    Ticket request: https://nvbugspro.nvidia.com/bug/5035899
       Create a sequence which targets BX flushes with the following younger instructions: IDIV/FDIV; SPR R/W ; FADDA (these are all variable latency instructions)

    Description:
       Create a scenario that cross branch misprediction with bx uops, IDIV/FDIV, SPR, FADDA instructions (variable latency - non-pipelined uops).
       in order to increase the amount of bx misprediction, we create nested loops and also uses EventTrigger
    '''
    AR.comment("inside is_bx_stress_scenario")
    with AR.Loop(counter=random.randint(3, 6)):
        with AR.Loop(counter=random.randint(3, 6)):
            for _ in range(random.randint(4, 10)):
                action = AR.choice(
                    values={"bx": 10, "div": 10, "spr": 0, "fadda": 10})  # SPR is not supported at the moment
                AR.generate(query=(AR.Instruction.mnemonic.contains(action)))


@AR.scenario_decorator(random=True, priority=Configuration.Priority.MEDIUM, tags=[Configuration.Tag.DISPATCH])
def ix_ports_stressing_scenario():
    '''
    Stressing all the different IX ports with different instructions, to see if there is any imbalance in the issue ports...
    '''
    #AR.comment("inside is_mx_v2g_cross_scenario")
    reg = RegisterManager.get(reg_name="x6") # this will exclude the x6 register from being used in the instructions
    RegisterManager.reserve(reg)
    with AR.Loop(counter=10):
        for _ in range(10):
            steering_class = AR.choice(values={"mx": 20, "ix": 80})
            AR.generate(query=(AR.Instruction.steering_class.contains(steering_class)), instruction_count=4, comment=f"stressing the issue ports with {steering_class} instructions")
    RegisterManager.free(reg)
