import random
from Tool.frontend.AR_API import AR
from Tool.frontend.sources_API import Sources

AR.comment(comment="Direct test start here")
#reg = Sources.RegisterManager.get_free_registers()
number = AR.choice(values={7:30, random.randint(2,40):70})
#AR.asm(f"mov {reg}, {number}", comment=f"moving {number} into eax")

