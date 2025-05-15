import random
from Arrow.Utils.configuration_management import Configuration
from Arrow.Arrow_API import AR
from Arrow.Arrow_API.resources.register_manager import RegisterManager_API as RegisterManager
from Arrow.Arrow_API.resources.memory_manager import MemoryManager_API as MemoryManager

from Arrow.Internal_content.ingredients.fibonacci.fibonacci_caller import fibonacci_caller

_fibonacci_recursive_code_block = None
@AR.ingredient_decorator(random=True, priority=Configuration.Priority.HIGH, precondition=Configuration.Architecture.arm )
class fibonacciRecursive_ing(AR.Ingredient):
    '''
    Function: fib
    Description: Computes the nth Fibonacci number recursively using the stack for parameter passing and result storage.
                 Base case returns n if n <= 1. For n > 1, recursively computes fib(n-1) + fib(n-2).
    Inputs: n (passed via stack)
    Outputs: fib(n) (in register a0)
    Stack Usage: Saves input, return address, and intermediate results.
    '''

    def __init__(self):
        self.fibonacci_block = None
        self.n_register = None
        self.result_register = None

    def init(self):
        self.fibonacci_result_mem = MemoryManager.Memory()
        self.n_register = RegisterManager.get_and_reserve()
        self.result_register = RegisterManager.get_and_reserve()

        global _fibonacci_recursive_code_block
        if _fibonacci_recursive_code_block is not None:
            # previously allocated. reuse the same code block
            self.fibonacci_block = _fibonacci_recursive_code_block
        else: # _fibonacci_recursive_code_block is None

            self.fibonacci_block = MemoryManager.MemorySegment(f"fibonacci_block", byte_size=0x500, memory_type=Configuration.Memory_types.CODE)
            AR.comment(f'allocating fibonacci-blocks at {hex(self.fibonacci_block.address)}')
            _fibonacci_recursive_code_block = self.fibonacci_block

            fib_base_case_label = AR.Label(postfix="fib_base_case")

            with AR.BranchToSegment(code_block=self.fibonacci_block):

                if Configuration.Architecture.riscv:
                    sp_reg = RegisterManager.get("sp")
                    ra_reg = RegisterManager.get("ra")
                elif Configuration.Architecture.arm:
                    sp_reg = RegisterManager.get("sp")
                    fp_reg = RegisterManager.get("fp")
                    lr_reg = RegisterManager.get("lr")

                else:
                    raise ValueError('Unsupported Architecture for this code ')

                tmp_reg = RegisterManager.get_and_reserve()
                AR.comment("Save return address to stack, and check if N reached base-case")
                if Configuration.Architecture.riscv:
                    AR.Stack.push([ra_reg, self.n_register])
                    #AR.asm(f"addi {sp_reg}, {sp_reg}, -8", comment="Allocate stack space")
                    #AR.asm(f"sw {ra_reg}, 4({sp_reg})", comment="store return address")
                    #AR.asm(f"sw {self.n_register}, 0({sp_reg})", comment="Save input n")
                    AR.comment("check base case")
                    AR.Stack.read(0, self.n_register)
                    #AR.asm(f"lw {self.n_register}, 0({sp_reg})")
                    AR.asm(f"li {tmp_reg}, 1")
                    AR.asm(f"ble {self.n_register}, {tmp_reg}, {fib_base_case_label}", comment="If n <= 1, go to base case")
                else:  # Configuration.Architecture.arm:
                    AR.Stack.push([fp_reg, lr_reg])
                    #AR.asm(f"stp {fp_reg}, {lr_reg}, [{sp_reg}, #-16]!", comment="save frame pointer and link register")
                    AR.asm(f"mov {fp_reg}, {sp_reg}", comment="update frame pointer")
                    AR.asm(f"cmp {self.n_register}, #1", "Compare n with 1")
                    AR.asm(f"ble {fib_base_case_label}", "If n <= 1, go to base case")

                AR.comment("Recursive case: fib(n-1)")
                if Configuration.Architecture.riscv:
                    AR.Stack.push([self.n_register])
                    #AR.asm(f"addi {self.n_register}, {self.n_register}, -1 ", comment="n -1")
                    #AR.asm(f"sw {self.n_register}, 0({sp_reg})", comment="Push n-1 onto the stack")
                    AR.asm(f"jal {ra_reg}, {self.fibonacci_block.code_label}", comment=f"Call fib(n-1)")
                    AR.Stack.read(0, tmp_reg, comment=f"Retrieve n-1 result into {tmp_reg}")
                    #AR.asm(f"lw {tmp_reg}, 0({sp_reg})", comment=f"Retrieve n-1 result into {tmp_reg}")
                else:  # Configuration.Architecture.arm:
                    AR.asm(f"sub {self.result_register}, {self.n_register}, #1 ", comment="n -1")
                    AR.Stack.push([self.n_register, self.result_register])
                    #AR.asm(f"stp {self.n_register}, {self.result_register}, [{sp_reg}, #-16]!", comment="Save current n and n-1 on the stack")
                    AR.asm(f"mov {self.n_register}, {self.result_register}", comment=f"Set {self.n_register} to n-1 for the recursive call")
                    AR.asm(f"bl {self.fibonacci_block.code_label}", comment=f"Call fib(n-1)")
                    AR.Stack.pop([self.result_register,tmp_reg])
                    #AR.asm(f"ldp {self.result_register}, {tmp_reg}, [{sp_reg}], #16", comment="Restore n and n-1 from the stack")
                    AR.asm(f"mov {tmp_reg}, {self.n_register}", comment=f"Retrieve n-1 result into {tmp_reg}")

                AR.comment("Recursive case: fib(n-2)")
                if Configuration.Architecture.riscv:
                    AR.Stack.read(0, self.n_register, comment="Restore n")
                    #AR.asm(f"lw {self.n_register}, 0({sp_reg})", comment="Restore n")
                    AR.Stack.push([self.n_register])
                    #AR.asm(f"addi {self.n_register}, {self.n_register}, -2 ", comment="n -2")
                    #AR.asm(f"sw {self.n_register}, 0({sp_reg})", comment="Push n-2 onto the stack")
                    AR.asm(f"jal {ra_reg}, {self.fibonacci_block.code_label}", comment=f"Call fib(n-2)")
                else:  # Configuration.Architecture.arm:
                    AR.asm(f"sub {self.n_register}, {self.result_register}, #2 ", comment="n -2")
                    AR.asm(f"stp {self.result_register}, {tmp_reg}, [{sp_reg}, #-16]!", comment="Save current n and fib(n-1) on the stack")
                    AR.asm(f"bl {self.fibonacci_block.code_label}", comment=f"Call fib(n-2)")
                    AR.Stack.pop([self.result_register, tmp_reg])
                    #AR.asm(f"ldp {self.result_register}, {tmp_reg}, [{sp_reg}], #16", comment="Restore n and fib(n-1) from the stack")

                AR.comment("Combine results: a0 = fib(n-1) + fib(n-2)")
                if Configuration.Architecture.riscv:
                    AR.asm(f"add {self.result_register}, {tmp_reg}, {self.result_register}")
                else:  # Configuration.Architecture.arm:
                    AR.asm(f"add {self.n_register}, {tmp_reg}, {self.n_register}")

                AR.comment("fibonacci_base_case")
                if Configuration.Architecture.riscv:
                    AR.asm(f"{fib_base_case_label}:")
                    AR.Stack.read(0, self.n_register, comment="Restore input n")
                    #AR.asm(f"lw {self.n_register}, 0({sp_reg})", comment="Restore input n")
                    AR.asm(f"mv {self.result_register}, {self.n_register}", comment="Base case result = n")
                    AR.Stack.pop([self.n_register, ra_reg])
                    #AR.asm(f"lw {self.n_register}, 0({sp_reg})", comment="Restore n from stack")
                    #AR.asm(f"lw {ra_reg}, 4({sp_reg})", comment="Restore return address from stack")
                    #AR.asm(f"addi {sp_reg}, {sp_reg}, 8", comment="Deallocate stack space")
                    AR.asm(f"jr {ra_reg}", comment="Return to caller")
                else:  # Configuration.Architecture.arm:
                    AR.Stack.pop([fp_reg,lr_reg])
                    #AR.asm(f'ldp {fp_reg}, {lr_reg}, [{sp_reg}], #16', comment="Restore frame pointer and link register")
                    AR.asm("ret", comment="Return to caller")
                    AR.asm(f"{fib_base_case_label}:")
                    AR.Stack.pop([fp_reg,lr_reg])
                    #AR.asm(f'ldp {fp_reg}, {lr_reg}, [{sp_reg}], #16', comment="Restore frame pointer and link register")
                    AR.asm("ret", comment="Return to caller")

                RegisterManager.free(tmp_reg)

            RegisterManager.free(self.n_register)
            RegisterManager.free(self.result_register)
        yield

    def body(self):

        yield
        # TODO:: need an API to check if a register is free, and if not need to store it in stack before usage
        self.n_register = RegisterManager.get(self.n_register.name)
        RegisterManager.reserve(self.n_register)


        recursive_count = random.randint(2, 5)

        if Configuration.Architecture.riscv:
            sp_reg = RegisterManager.get("sp")
            ra_reg = RegisterManager.get("ra")
            self.result_register = RegisterManager.get(self.result_register.name)
            RegisterManager.reserve(self.result_register)

            AR.asm(f'li {self.n_register}, {recursive_count}', comment=f"set the value of {recursive_count} into {self.n_register}") #TODO:: Implement a function to store values into operands! will make code arch-agnostic
            AR.asm(f'addi, {sp_reg}, {sp_reg}, -4', comment=f"Decrement stack pointer (allocate space)")                 #TODO:: Implement a function to push/pop values to stack! will make code arch-agnostic
            AR.asm(f'sw {self.n_register}, 0({sp_reg})', comment=f"Store the value of {self.n_register} at the top of the stack")
            AR.asm(f'jal {ra_reg}, {self.fibonacci_block.code_label}', comment=f"Call fib(n)")                     #TODO:: Implement a function to branch to different locations! will make code arch-agnostic
            RegisterManager.free(self.n_register)
            tmp_reg = RegisterManager.get_and_reserve()
            AR.asm(f'la {tmp_reg}, {self.fibonacci_result_mem.unique_label}', comment="Load address of fib_result")
            AR.asm(f'sw {self.result_register}, 0({tmp_reg})', comment="Store result in fib_result")
            RegisterManager.free(tmp_reg)
            RegisterManager.free(self.result_register)
        elif Configuration.Architecture.arm:
            AR.asm(f'mov {self.n_register}, #{recursive_count}', comment=f"set the value of {recursive_count} into {self.n_register}")
            AR.asm(f'bl {self.fibonacci_block.code_label}', comment=f"Call fib(n)")
            AR.comment(f"Result will be in {self.n_register} after the function returns")
            tmp_reg = RegisterManager.get_and_reserve()
            AR.asm(f'ldr {tmp_reg}, ={self.fibonacci_result_mem.unique_label}', comment=f"Load the address of 'result memory' into {tmp_reg}")
            AR.asm(f'str {self.result_register}, [{tmp_reg}]', comment="Store the value of {self.result_register} into memory at 'result memory'")
            RegisterManager.free(self.n_register)
            RegisterManager.free(tmp_reg)
            '''
            x0 == n_register
            w0 = result register
            '''
        else:
            raise ValueError('Unsupported Architecture for this code ')


    def final(self):
        pass


'''
    .data
fib_input:  .word 10          # Input: Fibonacci number to compute
fib_result: .word 0           # Output: Store the result

    .text
    .global _start

# Entry Point
_start:
    la t0, fib_input          # Load address of input n
    lw t1, 0(t0)              # Load value of n into t1
    addi sp, sp, -4           # Push n onto the stack
    sw t1, 0(sp)              # Store n on the stack
    jal ra, fib               # Call fib(n)
    la t0, fib_result         # Load address of fib_result
    sw a0, 0(t0)              # Store result in fib_result

    # Exit program
    li a7, 10                 # Syscall for exit
    ecall

# Fibonacci Function: fib(n)
# Input: n is on top of the stack
# Output: a0 contains fib(n)
fib:
    addi sp, sp, -8           # Allocate stack space for locals
    sw ra, 4(sp)              # Save return address
    sw t1, 0(sp)              # Save input n

    lw t1, 0(sp)              # Load n
    li t2, 1
    ble t1, t2, fib_base_case # If n <= 1, return n

    # Recursive case: fib(n-1)
    addi t1, t1, -1           # n-1
    sw t1, 0(sp)              # Push n-1 onto the stack
    jal ra, fib               # Call fib(n-1)
    lw t2, 0(sp)              # Retrieve n-1 result into t2

    # Recursive case: fib(n-2)
    lw t1, 0(sp)              # Restore n
    addi t1, t1, -2           # n-2
    sw t1, 0(sp)              # Push n-2 onto the stack
    jal ra, fib               # Call fib(n-2)

    # Combine results: a0 = fib(n-1) + fib(n-2)
    add a0, t2, a0

fib_base_case:
    lw t1, 0(sp)              # Restore input n
    mv a0, t1                 # Base case result = n

    lw t1, 0(sp)              # Restore n from stack
    lw ra, 4(sp)              # Restore return address
    addi sp, sp, 8            # Deallocate stack space
    jr ra                     # Return to caller

'''