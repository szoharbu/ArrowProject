import random
from Utils.configuration_management import Configuration
from Arrow_API import AR

@AR.scenario_decorator(random=True, priority=Configuration.Priority.MEDIUM, tags=[Configuration.Tag.DISPATCH])
def is_mx_v2g_cross_scenario():
    AR.comment("inside is_mx_v2g_cross_scenario")
    with AR.Loop(counter=10):
        for _ in range(10):
            action = AR.choice(values={"mx": 80, "v2g": 80})
            AR.generate(query=AR.Instruction.steering_class.contains(action))


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
                if action == "bx":
                    AR.generate(query=(AR.Instruction.mnemonic.contains("bx")))
                elif action == "div":
                    AR.generate(query=(AR.Instruction.mnemonic.contains("div")))
                elif action == "fadda":
                    AR.generate(query=(AR.Instruction.mnemonic.contains("fadda")))

