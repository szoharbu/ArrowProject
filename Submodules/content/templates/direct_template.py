import random
from Tool.frontend.AR_API import AR
from Tool.frontend.sources_API import Sources

def content():
    print('--------------------------------------------------------------------')
    AR.comment(comment="Direct test start here")
    for _ in range(20):
        reg = Sources.RegisterManager.get_and_reserve()
        number = AR.choice(values={7:30, random.randint(2,40):70})
        AR.asm(f"mov {reg}, {number}", comment=f"moving {number} into {reg}")
        Sources.RegisterManager.free(reg)

        mem = Sources.Memory()
        print(mem)

    print('--------------------------------------------------------------------')

