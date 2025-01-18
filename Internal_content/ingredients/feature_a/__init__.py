
import random
from Utils.configuration_management import Configuration
from Arrow_API import AR
from Arrow_API.resources.register_manager import RegisterManager_API as RegisterManager
from Arrow_API.resources.memory_manager import MemoryManager_API as MemoryManager


@AR.ingredient_decorator(random=True, priority=Configuration.Priority.HIGH)
class ing_A(AR.Ingredient):
    def init(self):
        burst_count = random.randint(1, 5)
        AR.generate(instruction_count=burst_count)
        yield
        AR.generate(instruction_count=burst_count)

    def body(self):
        reg = RegisterManager.get_and_reserve()

        AR.generate(src=reg)
        yield
        AR.generate(dest=reg)
        yield
        AR.generate(src=reg)

        RegisterManager.free(reg)

    def final(self):
        AR.generate()

@AR.ingredient_decorator(random=True, priority=Configuration.Priority.MEDIUM, precondition=Configuration.Architecture.x86)
class ing_B(AR.Ingredient):
    def init(self):
        pass

    def body(self):
        mem = MemoryManager.Memory(init_value=random.randint(1,1000))
        reg = RegisterManager.get_and_reserve()
        AR.asm(f"mov {mem}, 0x1234")
        yield
        AR.asm(f"mov {reg}, {mem}")
        yield
        AR.asm(f"mov {mem}, {reg}")
        RegisterManager.free(reg)

    def final(self):
        pass

def random_precondition():
    value = AR.choice(values={True:50,False:50})
    return value

@AR.ingredient_decorator(random=True, priority=Configuration.Priority.MEDIUM, tags=[Configuration.Tag.FAST, Configuration.Tag.FEATURE_A], precondition=lambda: random_precondition())
class ing_B_with_precond(AR.Ingredient):
    def init(self):
        pass

    def body(self):
        mem1 = MemoryManager.Memory()
        mem2 = MemoryManager.Memory(shared=True)
        reg = RegisterManager.get_and_reserve()
        reg2 = RegisterManager.get_and_reserve()
        if Configuration.Architecture.x86:
            AR.asm(f"mov {mem1}, 0x1234")
            yield
            AR.asm(f"mov {reg}, {mem2}")
            yield
            AR.asm(f"mov {mem1}, {reg}")
        elif Configuration.Architecture.arm:
            # in arm, we can't use memory operands for MOV instructions
            AR.asm(f"mov {reg2}, 0x1234")
            yield
            AR.asm(f"mov {reg}, {reg2}")
            yield
            AR.asm(f"mov {reg2}, {reg}")
        else: # riscv
            # in riscv there is no MOV instruction
            AR.asm(f"add {reg}, {reg}, {reg2}")
            yield
            AR.asm(f"addi {reg}, {reg2}, 0x123")
            yield
            AR.asm(f"sub {reg}, {reg}, {reg2}")


        RegisterManager.free(reg)
        RegisterManager.free(reg2)

    def final(self):
        pass

@AR.ingredient_decorator(random=True, priority=Configuration.Priority.LOW, precondition=Configuration.Architecture.x86)
class ing_C(AR.Ingredient):
    def init(self):
        reg = RegisterManager.get()
        AR.asm(f"mov {reg}, 0x12345678")
        AR.asm(f"push {reg}")
        yield

    def body(self):
        pass

    def final(self):
        reg = RegisterManager.get()
        AR.asm(f"pop {reg}")
        AR.asm(f"cmp {reg}, 0x12345678")
        yield

@AR.ingredient_decorator(random=True, priority=Configuration.Priority.HIGH, precondition=Configuration.Architecture.riscv)
class riscv_load_stress(AR.Ingredient):
    def __init__(self):
        self.mem = None
        self.label = AR.Label(postfix="riscv_label")

    def init(self):
        self.mem = MemoryManager.Memory(shared=True)
        for i in range(2):
            AR.generate(src=self.mem, query=(AR.Instruction.group=="load"))
            yield

    def body(self):
        count = random.randint(1,5)
        AR.comment(self.label)
        for i in range(count):
            AR.generate(src=self.mem, query=(AR.Instruction.group=="load"))
            yield

    def final(self):
        pass


@AR.ingredient_decorator(random=True, priority=Configuration.Priority.HIGH)
class ing_with_boot_code(AR.Ingredient):

    def boot(self):
        if Configuration.Architecture.x86:
            AR.generate(instruction_count=5, query=(AR.Instruction.group=="bitwise"))
        if Configuration.Architecture.riscv:
            AR.generate(instruction_count=5, query=(AR.Instruction.group=="logical"))
        if Configuration.Architecture.arm:
            AR.generate(instruction_count=5, query=(AR.Instruction.group == "bitwise"))

    def init(self):
        pass

    def body(self):
        if Configuration.Architecture.x86:
            AR.generate(instruction_count=5, query=(AR.Instruction.group=="arithmetic"))
        else:
            AR.generate(query=(AR.Instruction.group=="load"))
            yield
            AR.generate(query=(AR.Instruction.group == "load"))

    def final(self):
        pass

@AR.ingredient_decorator(random=True, priority=Configuration.Priority.MEDIUM, precondition=(not Configuration.Architecture.riscv))
class ing_with_event_trigger(AR.Ingredient):

    def init(self):
        pass

    def body(self):
        #TODO:: EventTrigger is currently not implemented in RISCV, remove precondition once fixed
        with AR.EventTrigger(frequency=Configuration.Frequency.LOW):
            AR.generate(instruction_count=5)

    def final(self):
        pass