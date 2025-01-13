import random
from Utils.configuration_management import Configuration
from Tool.frontend.AR_API import AR
from Tool.frontend.sources_API import Sources

@AR.scenario_decorator(random=True, priority=Configuration.Priority.MEDIUM, tags=[Configuration.Tag.FEATURE_A, Configuration.Tag.SLOW])
def direct_scenario():
    print('-------------------------------------------------------------------- direct content start')
    AR.comment(comment="Direct test start here")
    for _ in range(20):
        reg = Sources.RegisterManager.get_and_reserve()
        number = AR.choice(values={7:30, random.randint(2,40):70})
        AR.asm(f"mov {reg}, {number}", comment=f"moving {number} into {reg}")
        Sources.RegisterManager.free(reg)

        AR.generate()
        AR.generate(src=reg)

@AR.scenario_decorator(random=True, priority=Configuration.Priority.MEDIUM, tags=[Configuration.Tag.FEATURE_A, Configuration.Tag.SLOW])
def direct_memory_stress_scenario():
    print('-------------------------------------------------------------------- direct_memory_stress_scenario')
    AR.comment(comment="Direct test start here")
    for _ in range(20):
        mem = Sources.Memory()
        action = AR.choice(values=["src","dest"])
        if action == "src":
            AR.generate(src=mem)
        else:
            AR.generate(dest=mem)

