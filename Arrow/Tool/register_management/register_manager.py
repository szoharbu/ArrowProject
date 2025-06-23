import random
from Arrow.Tool.register_management.register import Register
from Arrow.Utils.logger_management import get_logger
from Arrow.Utils.configuration_management import Configuration


class RegisterManager:
    def __init__(self,) -> None:
        """
            Initializes the RegisterManager with an internal pool of Registers.
        """
        #self._random_register_pool = []
        #self._full_register_pool = []
        # Categorized register storage
        self._registers_pool = []

        logger = get_logger()
        logger.info("==================== RegisterManager")


        if Configuration.Architecture.x86:
            '''
            Summary of x86-64 Registers:
                General Purpose: RAX, RBX, RCX, RDX, RSI, RDI, R8 - R15 (for data, arguments, return values).
                Special Purpose: RSP (stack pointer), RBP (base pointer), RIP (instruction pointer), FLAGS (status flags), CS, DS, ES, FS, GS, SS (segment registers).
                SIMD/Float: XMM0 - XMM15 (for 128-bit floating-point operations).
            '''
            for name in (["ax", "bx", "cx", "dx", "si", "di", "bp"]):
                reg = Register(name_mapping={64: f"r{name}", 32: f"r{name}", 16: name}, type="gpr", default_size=64, is_random=True)
                self._registers_pool.append(reg)

            for name in (["r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15"]):
                reg = Register(name_mapping={64: {name}, 32: f"{name}d", 16:f"{name}w"}, type="gpr", default_size=64, is_random=True)
                self._registers_pool.append(reg)

            for name in (["sp"]):
                reg = Register(name_mapping={64:f"r{name}",32:f"e{name}"}, type="gpr", default_size=64, is_random=False)
                self._registers_pool.append(reg)

        elif Configuration.Architecture.riscv:
            '''
            Summary of RISC-V Registers:
                General Purpose: x0 (zero), x1 (ra - return address), x2 (sp - stack pointer), x3 (gp - global pointer), x4 (tp - thread pointer), 
                    x5-x7 (t0-t2 - temporaries), x8-x15 (s0-s7 - saved), x16-x31 (t3-t7, s8-s15 - temporaries and saved).
                Special Purpose: pc (program counter), csr (control and status registers).
                Floating-Point/SIMD: f0-f31 (floating-point), v0-v31 (vector registers).
            '''
            # TODO:: in some setting, there are 16 s-registers and 8 t-registers, need to check when, for now I reduced it to 12s and 6t
            for i in range(0,6):
                reg = Register(name_mapping={64:f"t{i}"}, type="gpr", default_size=64, is_random=True)
                self._registers_pool.append(reg)
            for i in range(0,12):
                reg = Register(name_mapping={64:f"s{i}"}, type="gpr", default_size=64, is_random=True)
                self._registers_pool.append(reg)

            for name in (["pc","x0","ra","sp"]):
                reg = Register(name_mapping={64:name}, type="gpr", default_size=64, is_random=False)
                self._registers_pool.append(reg)

        elif Configuration.Architecture.arm:
            '''
            Summary of Common Registers in ARM64:
                General Purpose: (used for data storage, function arguments, etc.)
                    X0 - X30 - 64bit register (x31 is reserved for zero register)
                    W0 - W30 - 32bit register (lower 32 bit of X registers)
                    Special Purpose: sp (stack pointer), lr (link register), pc (program counter), W/XZR (zero register)
                SIMD & FP:
                    V0 - V31 - 128bit SIMD and FP registers
                    Q0 - Q31 - 128bit SIMD and FP registers, just the legacy name and more common in AArch32 
                    D0 - D31 - 64bit SIMD and FP registers (lower 64 bit of V registers)
                    S0 - S31 - 32bit SIMD and FP registers (lower 32 bit of V registers)
                    H0 - H31 - 16bit SIMD and FP registers (lower 16 bit of V registers)
                    B0 - B31 - 8bit SIMD and FP registers (lower 8 bit of V registers)
                SVE (Scalable Vector Extension):
                    Z0 - Z31 - 128bit SVE registers
                Condition Flags: NZCV (Negative, Zero, Carry, Overflow)
                SPSR (Saved Program Status Register): Holds the saved state of the CPSR during an exception.
                FAR (Fault Address Register): Holds the faulting address during an exception.
                TPIDR_EL0 (Thread Pointer ID Register): Holds the thread ID of the current thread.
            '''

            ############################### GPR registers
            for i in range(0,29):
                reg = Register(name_mapping={64:f"x{i}",32:f"w{i}"}, type="gpr", default_size=64, is_random=True)
                self._registers_pool.append(reg)

            for name in (["sp","lr","pc","xzr", "fp"]):
                reg = Register(name_mapping={64:name,}, type="gpr", default_size=64, is_random=False)
                self._registers_pool.append(reg)

            ############################### SIMD integer registers
            for i in range(0, 31):
                reg = Register(name_mapping={128:f"q{i}"}, type="simd_int", default_size=128, is_random=True)
                self._registers_pool.append(reg)

            ############################### SIMD&FP registers
            for i in range(0, 31):
                reg = Register(name_mapping={128:f"v{i}",64:f"d{i}",32:f"s{i}",16:f"h{i}",8:f"b{i}"}, type="simd_fp", default_size=128, is_random=True)
                self._registers_pool.append(reg)

            ############################### Extended vector registers
            for i in range(0, 31):
                reg = Register(name_mapping={128:f"z{i}"}, type="sve_reg", default_size=128, is_random=True)
                self._registers_pool.append(reg)

            for i in range(0, 15):
                reg = Register(name_mapping={16:f"p{i}"}, type="sve_pred", default_size=16, is_random=True)
                self._registers_pool.append(reg)

        else:
            raise ValueError(f"Unknown Architecture requested")


    def is_valid_register(self, reg_name:str=None, reg_type:str=None) -> bool:
        if reg_name is None:
            return reg_type in [reg.type for reg in self._registers_pool]
        else:
            return reg_name in [reg.name for reg in self._registers_pool]

    def get_free_registers(self, reg_type:str=None) -> list[Register]:
        """
        Returns a list of all free registers.
        """
        #return [register for register in self._random_register_pool if not register.is_reserve()]
        if reg_type is None:
            return [register for register in self._registers_pool if (not register.is_reserve() and register.is_random==True)]
        else:
            return [register for register in self._registers_pool
                    if (not register.is_reserve() and register.type==reg_type and register.is_random==True)]


    def get_used_registers(self, reg_type:str=None) -> list[Register]:
        """
        Returns a list of all reserved registers.
        """
        if reg_type is None:
            return [register for register in self._registers_pool if register.is_reserve()]
        else:
            return [register for register in self._registers_pool if (register.is_reserve() and register.type==reg_type)]

    def get(self, reg_name:str=None, reg_type:str=None) -> Register:
        """
        Selects a random free register, don't mark them as used (reserved = False),
        and returns the selected register. If no available child is found, raise Error
        """
        if reg_name:
            for reg in self._registers_pool:
                if reg.name == reg_name:
                    return reg
            raise ValueError(f'Invalid value, register {reg_name} is not part of registers list ')
        else:
            if reg_type == "sve_pred_low":
                # if reg_type is sve_pred_low, we need to check if there are any free predicate registers available at the range of p0-p7 , which is a subset of sve_pred (p0-p17)
                all_free_regs = self.get_free_registers(reg_type="sve_pred")
                low_registers = [reg for reg in all_free_regs if reg.name in ["p0", "p1", "p2", "p3", "p4", "p5", "p6", "p7"]]
                free_regs = low_registers
            else:
                free_regs = self.get_free_registers(reg_type=reg_type)

            if free_regs:
                if Configuration.Architecture.riscv:
                    # in riscv, try preferring temp registers when ask for get, and saved registers when asked for get_and_reserve
                    temp_registers = [reg for reg in free_regs if str(reg).startswith('t')]
                    selected_reg = random.choice(temp_registers) if temp_registers else random.choice(free_regs)
                else:
                    # Default selection for non-RISC-V architectures
                    selected_reg = random.choice(free_regs)
                return selected_reg
            else:
                # No available child
                raise RuntimeError(f"Register manager ran out of free registers")

    def get_and_reserve(self, reg_type:str="gpr") -> Register:
        """
        Selects a random free register, marks them as used (reserved = True),
        and returns the selected register. If no available child is found, raise Error
        """
        if not self.is_valid_register(reg_type=reg_type):
            reg_types = [reg.type for reg in self._registers_pool]
            unique_reg_types = list(set(reg_types))            # get unique types
            raise ValueError(f"Invalid register type: `{reg_type}`. Please use one of the following types: {', '.join(unique_reg_types)}")

        free_regs = self.get_free_registers(reg_type=reg_type)
        if free_regs:
            if Configuration.Architecture.riscv:
                # in riscv, try preferring temp_registers when ask for get, and saved-registers when asked for get_and_reserve
                saved_registers = [reg for reg in free_regs if str(reg).startswith('s')]
                selected_reg = random.choice(saved_registers) if saved_registers else random.choice(free_regs)
            else:
                # Default selection for non-RISC-V architectures
                selected_reg = random.choice(free_regs)

            selected_reg.set_reserve()
            return selected_reg
        else:
            # No available child
            raise RuntimeError(f"Register manager ran out of free registers")

    @staticmethod
    def reserve(register: Register):
        """
        Sets the specified register reserve attribute to True.

        Parameters:
        - register (Register): The register to make reserve.

        """
        register.set_reserve()

    @staticmethod
    def free(register: Register):
        """
        Sets the specified register reserve attribute to False.

        Parameters:
        - register (Register): The register to make free again.

        """
        register.set_free()

    def print_reg_status(self):
        for reg in self._registers_pool:
            print(f'====== reg {reg.name} , reserve = {reg.is_reserve()}')
