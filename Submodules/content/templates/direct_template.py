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

        mem = Sources.Memory()
        AR.generate()
        AR.generate(src=mem)

    print('-------------------------------------------------------------------- direct content end')

