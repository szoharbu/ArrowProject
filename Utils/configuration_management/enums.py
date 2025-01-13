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