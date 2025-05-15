
from Arrow.Utils.configuration_management import Configuration
from Arrow.Tool.register_management.register import Register
from Arrow.Tool.asm_libraries.asm_logger import AsmLogger


def store_value_into_register(register:Register, value:int) -> None:
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
        if value < 0 or value > 0xFFFFFFFFFFFFFFFF:
            raise ValueError("The value must be a 64-bit integer (0 to 0xFFFFFFFFFFFFFFFF)")
        # ARM AArch64 MOV instruction can handle immediate values up to 16 bits directly.
        # The MOV instruction with an immediate can only take 12-bit wide constants with rotations.

        # Step 1: Split the value into 32-bit chunks
        high_32 = (value >> 32) & 0xFFFFFFFF  # High 32 bits
        low_32 = value & 0xFFFFFFFF  # Low 32 bits

        # Step 2: Check if the high and low parts can be loaded directly using MOVZ/MOVK
        if high_32 != 0:
            AsmLogger.asm(f"movz {register}, 0x{high_32:X}, LSL #32", comment="Load the high 32 bits")
            AsmLogger.asm(f"movk {register}, 0x{low_32:X}, LSL #0", comment="Load the low 32 bits")
        else:
            # If only low part exists, load using MOVZ
            AsmLogger.asm(f"movz {register}, 0x{low_32:X}, LSL #0", comment="Load the low 32 bits directly")
    else:
        raise ValueError(f"Unsupported architecture")