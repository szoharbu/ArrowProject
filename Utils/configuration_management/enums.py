from enum import Enum

class Architecture:
    # Boolean flags to define the current architecture
    x86 = False
    riscv = False
    arm = False
    arch_str = False

class Memory_types(Enum):
    BOOT_CODE = "boot_code"
    CODE = "code"
    DATA_SHARED = "data_shared"
    DATA_PRESERVE = "data_reserved"

# Simplified Enum for standard size constants
class ByteSize(Enum):
    SIZE_1K = 1024                # Kilobyte (1K = 1024 bytes)
    SIZE_2K = 2*1024
    SIZE_4K = 4*1024
    SIZE_8K = 8*1024
    SIZE_1M = 1024 * 1024         # Megabyte (1M = 1024 * 1024 bytes)
    SIZE_2M = 2 * 1024 * 1024
    SIZE_4M = 4 * 1024 * 1024
    SIZE_1G = 1024 * 1024 * 1024  # Gigabyte (1G = 1024 * 1024 * 1024 bytes)
    SIZE_2G = 2*1024 * 1024 * 1024
    SIZE_4G = 4*1024 * 1024 * 1024

    # Method to get size in bytes
    def in_bytes(self):
        return self.value
