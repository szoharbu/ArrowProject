import random
from Tool.frontend.AR_API import AR

AR.comment(comment="Direct test start here")
number = AR.choice(values={7:30, random.randint(2,40):70})
AR.asm(f"mov eax, {number}", comment=f"moving {number} into eax")

