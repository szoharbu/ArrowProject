from ....Utils.configuration_management import Configuration
from ....Arrow_API import AR


@AR.ingredient_decorator(random=True, priority=Configuration.Priority.HIGH, precondition=Configuration.Architecture.arm)
class fibonacci_caller(AR.Ingredient):
    def init(self):
        print('zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz')
        #TG.asm(".extern my_cpp_function", comment="Declare the external C++ function")

    def body(self):
        if Configuration.Architecture.x86:
            AR.asm("call my_cpp_function", comment="Call the C++ function")
        elif Configuration.Architecture.arm:
            AR.asm("bl my_cpp_function", comment="Call the C++ function")
        else: #Configuration.Architecture.riscv:
            pass
            #TODO:: get riscv toolchain and have the ability to run compiler
            #TG.asm("jal ra, my_cpp_function", comment="Call the C++ function")

    def final(self):
        pass
