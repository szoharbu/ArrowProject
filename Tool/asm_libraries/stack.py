
from typing import List
from Utils.configuration_management import Configuration
from Tool.register_management.register import Register
from Tool.asm_libraries.asm_logger import AsmLogger
from Tool.frontend.sources_API import Sources

class Stack:

    @staticmethod
    def push(register_list: List[Register], comment:str=None) -> None:
        """
        Generate push assembly code for the given registers.
        """
        if comment:
            AsmLogger.print_comment_line(comment)
        if Configuration.Architecture.x86:
            for reg in register_list:
                AsmLogger.print_asm_line(f"push {reg}")
        elif Configuration.Architecture.arm:
            # ARM64: Use post-indexing to adjust SP automatically while storing registers
            sp_reg = Sources.RegisterManager.get("sp")
            num_regs = len(register_list)
            for i in range(0, num_regs, 2):
                reg_pair = register_list[i:i + 2]
                if len(reg_pair) == 2:
                    # Use post-indexing with stp to store registers and adjust SP automatically
                    AsmLogger.print_asm_line(f"stp {reg_pair[0]}, {reg_pair[1]}, [{sp_reg}], #-16")
                else:
                    # For a single register, use str and post-indexing
                    AsmLogger.print_asm_line(f"str {reg_pair[0]}, [{sp_reg}], #-8")
        elif Configuration.Architecture.riscv:
            # RISC-V: Adjust SP once, then write using sd with offsets
            sp_reg = Sources.RegisterManager.get("sp")
            num_regs = len(register_list)
            stack_adjust = num_regs * 8  # 8 bytes per register
            AsmLogger.print_asm_line(f"addi {sp_reg}, {sp_reg}, -{stack_adjust}", comment="Adjust stack pointer")
            for i, reg in enumerate(register_list):
                AsmLogger.print_asm_line(f"sd {reg}, {i * 8}({sp_reg})", comment=f"Store register {reg} with offset")
        else:
            raise ValueError(f"Unsupported architecture")

    @staticmethod
    def pop(register_list: List[Register], comment:str=None) -> None:
        """
        Generate pop assembly code for the given registers.
        """
        if comment:
            AsmLogger.print_comment_line(comment)
        if Configuration.Architecture.x86:
            # x86: Direct pop for each register in reverse order
            for reg in register_list:
                AsmLogger.print_asm_line(f"pop {reg}")
        elif Configuration.Architecture.arm:
            # ARM64: Efficiently read registers using ldp/ldr with post-indexing
            sp_reg = Sources.RegisterManager.get("sp")
            num_regs = len(register_list)
            # Use post-indexing with #16 for two registers, #8 for one register
            for i in range(0, num_regs, 2):
                reg_pair = register_list[i:i + 2]
                if len(reg_pair) == 2:
                    # Load two registers and adjust SP with #16 post-indexing
                    AsmLogger.print_asm_line(f"ldp {reg_pair[0]}, {reg_pair[1]}, [{sp_reg}], #-16")
                else:
                    # For a single register, load and adjust SP with #8 post-indexing
                    AsmLogger.print_asm_line(f"ldr {reg_pair[0]}, [{sp_reg}], #-8")
        elif Configuration.Architecture.riscv:
            # RISC-V: Read registers using ld with offsets, then adjust SP
            sp_reg = Sources.RegisterManager.get("sp")
            num_regs = len(register_list)
            for i, reg in enumerate(reversed(register_list)):
                AsmLogger.print_asm_line(f"ld {reg}, {i * 8}({sp_reg})", comment="Load register with offset")
            stack_adjust = num_regs * 8  # 8 bytes per register
            AsmLogger.print_asm_line(f"addi {sp_reg}, {sp_reg}, {stack_adjust}", comment="Restore stack pointer")
        else:
            raise ValueError(f"Unsupported architecture")

    @staticmethod
    def read(offset: int, register: Register, comment:str=None) -> None:
        """
          Reads a value from the stack at the given offset into the specified register.

          :param offset: Offset (in bytes) from the stack pointer.
          :param register: Register to load the value into.
          """
        if comment:
            AsmLogger.print_comment_line(comment)
        if Configuration.Architecture.x86:
            rsp_reg = Sources.RegisterManager.get("rsp")  # 64-bit stack pointer
            AsmLogger.print_asm_line(f"mov {register}, [{rsp_reg} + {offset}]",
                                          comment=f"Read from stack at offset {offset}")
        elif Configuration.Architecture.arm:
            sp_reg = Sources.RegisterManager.get("sp")
            AsmLogger.print_asm_line(f"ldr {register}, [{sp_reg}, #{offset}]",
                                          comment=f"Read from stack at offset {offset}")
        elif Configuration.Architecture.riscv:
            sp_reg = Sources.RegisterManager.get("sp")
            AsmLogger.print_asm_line(f"ld {register}, {offset}({sp_reg})",
                                          comment=f"Read from stack at offset {offset}")
        else:
            raise ValueError(f"Unsupported architecture")

    @staticmethod
    def write(offset, register, comment:str=None):
        """
        Writes a value from the specified register to the stack at the given offset.

        :param offset: Offset (in bytes) from the stack pointer.
        :param register: Register containing the value to store.
        """
        if comment:
            AsmLogger.print_comment_line(comment)
        if Configuration.Architecture.x86:
            rsp_reg = Sources.RegisterManager.get("rsp")  # 64-bit stack pointer
            AsmLogger.print_asm_line(f"mov [{rsp_reg} + {offset}], {register}",
                                          comment=f"Write to stack at offset {offset}")
        elif Configuration.Architecture.arm:
            sp_reg = Sources.RegisterManager.get("sp")
            AsmLogger.print_asm_line(f"str {register}, [{sp_reg}, #{offset}]",
                                          comment=f"Write to stack at offset {offset}")
        elif Configuration.Architecture.riscv:
            sp_reg = Sources.RegisterManager.get("sp")
            AsmLogger.print_asm_line(f"sd {register}, {offset}({sp_reg})",
                                          comment=f"Write to stack at offset {offset}")
        else:
            raise ValueError(f"Unsupported architecture")