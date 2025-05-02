
from Utils.configuration_management import Configuration
from Tool.register_management.register import Register
from Tool.asm_libraries.asm_logger import AsmLogger


def store_value_into_register(register:Register, value:int) -> None:

    AsmLogger.comment(f"writing value {hex(value)} into {register}")

    if Configuration.Architecture.x86:
        # Ensure the value is a 64-bit integer (to fit into a 64-bit register)
        if value < 0 or value > 0xFFFFFFFFFFFFFFFF:
            raise ValueError("The value must be a 64-bit integer (0 to 0xFFFFFFFFFFFFFFFF)")
        AsmLogger.asm(f"mov {register}, {value:X}", comment=f"Load {value} into {register}")
    elif Configuration.Architecture.riscv:
        # Ensure the value is a 32-bit integer (to fit into 32-bit register)
        if value < 0 or value > 0xFFFFFFFF:
            raise ValueError("The value must be a 32-bit integer (0 to 0xFFFFFFFF)")

        # Step 1: Split into upper 20 bits and lower 12 bits
        upper_20_bits = (value >> 12) & 0xFFFFF  # Extract upper 20 bits
        lower_12_bits = value & 0xFFF  # Extract lower 12 bits

        # Step 2: Generate the LUI instruction for the upper 20 bits
        AsmLogger.asm(f"lui {register}, 0x{upper_20_bits:X}", comment=f"Load upper 20 bits into {register}")

        # Step 3: Handle the lower 12 bits with ADDI
        if lower_12_bits != 0:
            # If lower 12 bits are within the signed 12-bit range, use ADDI directly
            if lower_12_bits >= -2048 and lower_12_bits <= 2047:
                AsmLogger.asm(f"addi {register}, {register}, 0x{lower_12_bits:X}", comment=f"Add lower 12 bits into {register}")
            else:
                while lower_12_bits != 0:
                    # If the lower 12 bits are positive and fit within the range, subtract them
                    if lower_12_bits > 0:
                        add_value = min(2047, lower_12_bits)
                    else:
                        # If it's negative, use the negative range
                        add_value = max(-2048, lower_12_bits)

                    AsmLogger.asm(f"addi {register}, {register}, 0x{add_value:X}", comment="Add the largest chunk that fits within signed 12-bit range")
                    lower_12_bits -= add_value  # Subtract the added part
        else:
            AsmLogger.comment("No need for ADDI, the value is already handled by LUI.")
    elif Configuration.Architecture.arm:
        # Ensure the value is a 64-bit integer (to fit into a 64-bit register)
        if not (0 <= value <= 0xFFFFFFFFFFFFFFFF):
                raise ValueError("Value must be a 64-bit unsigned integer")

        # ARM AArch64 MOV instruction can handle immediate values up to 16 bits directly.
        # The MOV instruction with an immediate can only take 12-bit wide constants with rotations.

        parts = []
        for i in range(4):
            part = (value >> (i * 16)) & 0xFFFF
            if part != 0:
                parts.append((part, i * 16))

        if not parts:  # Value is 0
            AsmLogger.asm(f"movz {register}, #0", comment="Load zero")
            return

        AsmLogger.asm(f"movz {register}, 0x{parts[0][0]:X}, LSL #{parts[0][1]}", comment=f"Load first non-zero part")

        for part, shift in parts[1:]:
            AsmLogger.asm(f"movk {register}, 0x{part:X}, LSL #{shift}", comment=f"Load subsequent part")

    else:
        raise ValueError(f"Unsupported architecture")