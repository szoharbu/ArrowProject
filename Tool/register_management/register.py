from typing import List, Dict


class Register:
    def __init__(self, name_mapping:Dict, type:str, default_size:int, is_random:bool):
        """
        Initializes a Register with a name and a reserved attribute

        Parameters:
        - name (str): The name of the register.
        - reserved (bool): Whether the register is reserved. Defaults to False.
        """
        self.name_mapping = name_mapping
        self.type = type # gpr, vector, sve, ...
        self.is_random = is_random # some register can't get selected randomly
        self.default_size = default_size # in gpr default is 64, in simd and sve default is 128
        self._reserve = False
        self.name = f"{self.name_mapping[self.default_size]}"

    def is_reserve(self) -> bool:
        return self._reserve

    def as_size(self, size:int) -> str:
        # Convert the register to another available size.

        if size in self.name_mapping:
            return f"{self.name_mapping[size]}"
        else:
            raise ValueError(f"Size {size} is not available for {self.type} registers.")

    def set_reserve(self):
        self._reserve = True

    def set_free(self):
        self._reserve = False

    def __str__(self):
        return self.name


'''
In RISC-V, there are 32 general-purpose registers, each 32-bits wide in RV32 (32-bit mode) and 64-bits wide in RV64 (64-bit mode). 
These registers are generally referred to by their numerical index (e.g., x0, x1, ..., x31), 
but they also have specific names that suggest their primary purposes. Here’s a breakdown:
        RISC-V General-Purpose Registers
        Register	Name	Description	            Notes
        x0	        zero	Constant 0	            Always reads as zero; writes are ignored
        x1	        ra	    Return address	        Stores the return address for function calls
        x2	        sp	    Stack pointer	        Points to the current top of the stack
        x3	        gp	    Global pointer	        Points to global data
        x4	        tp	    Thread pointer	        Points to thread-local storage
        x5	        t0	    Temporary register 0	Caller-saved; used for intermediate values
        x6	        t1	    Temporary register 1	Caller-saved; used for intermediate values
        x7	        t2	    Temporary register 2	Caller-saved; used for intermediate values
        x8	        s0/fp	Saved register 0 or Frame pointer	Callee-saved; can also serve as a frame pointer
        x9	        s1	    Saved register 1	    Callee-saved
        x10	        a0	    Function argument 0 / Return value 0	First function argument and return value
        x11	        a1	    Function argument 1 / Return value 1	Second function argument and return value
        x12	        a2	    Function argument 2	    Third function argument
        x13	        a3	    Function argument 3	    Fourth function argument
        x14	        a4	    Function argument 4	    Fifth function argument
        x15	        a5	    Function argument 5	    Sixth function argument
        x16	        a6	    Function argument 6	    Seventh function argument
        x17	        a7	    Function argument 7	    Eighth function argument
        x18	        s2	    Saved register 2	    Callee-saved
        x19	        s3	    Saved register 3	    Callee-saved
        x20	        s4	    Saved register 4	    Callee-saved
        x21	        s5	    Saved register 5	    Callee-saved
        x22	        s6	    Saved register 6	    Callee-saved
        x23	        s7	    Saved register 7	    Callee-saved
        x24	        s8	    Saved register 8	    Callee-saved
        x25	        s9	    Saved register 9	    Callee-saved
        x26	        s10	    Saved register 10	    Callee-saved
        x27	        s11	    Saved register 11	    Callee-saved
        x28	        t3	    Temporary register 3	Caller-saved; used for intermediate values
        x29	        t4	    Temporary register 4	Caller-saved; used for intermediate values
        x30	        t5	    Temporary register 5	Caller-saved; used for intermediate values
        x31	        t6	    Temporary register 6	Caller-saved; used for intermediate values
Key Points about RISC-V Registers
Zero Register (x0 / zero): Always reads as zero and discards writes. This makes it useful in instructions where you want a constant 0.
Temporary Registers (t0–t6): Used as temporary storage during calculations. These are caller-saved, meaning the calling function is responsible for preserving them.
Saved Registers (s0–s11): Used to hold values that must persist across function calls. These are callee-saved, so the called function is responsible for restoring them.
Argument Registers (a0–a7): Hold function arguments. a0 and a1 also serve as return value registers.
Special-purpose Registers:
ra: Holds the return address for function calls.
sp: Stack pointer, which points to the top of the stack.
gp: Global pointer, which is typically used to point to a region containing global variables.
tp: Thread pointer, used in threading contexts for thread-local storage.

'''