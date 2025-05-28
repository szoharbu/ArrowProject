from enum import Enum

class Architecture:
    # Boolean flags to define the current architecture
    x86 = False
    riscv = False
    arm = False
    arch_str = False

class Memory_types(Enum):
    BSP_BOOT_CODE = "bsp_boot_code"
    BOOT_CODE = "boot_code"
    CODE = "code"
    DATA_SHARED = "data_shared"
    DATA_PRESERVE = "data_reserved"
    STACK = "stack"

class Execution_context(Enum):
    EL3 = "EL3" # Secure Monitor (Root/EL3)
    EL2_NS = "EL2_NS" # EL2, Non-secure Hypervisor
    EL2_S = "EL2_S" # EL2, Secure Hypervisor (less common)
    EL1_NS = "EL1_NS" # EL1, Non-secure
    EL1_S = "EL1_S" # EL1, Secure
    EL1_Realm = "EL1_Realm" # EL1, Realm (Armv9+)
    EL0_NS = "EL0_NS" # User-space, Non-secure
    EL0_S = "EL0_S" # User-space, Secure (TrustZone aware)
    EL0_Realm = "EL0_Realm" # User-space in Realm world

class Page_types(Enum):
    TYPE_CODE = "code"
    TYPE_DATA = "data"
    TYPE_DEVICE = "device"
    TYPE_SYSTEM = "system"

class Page_sizes(Enum):
    SIZE_4K = 4*1024
    SIZE_2M = 2 * 1024 * 1024
    SIZE_1G = 1024 * 1024 * 1024

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

class Tag(Enum):
    SLOW = "slow"
    FAST = "fast"
    RECIPE = "recipe"
    FEATURE_A = "feature_a"
    FEATURE_B = "feature_b"
    FEATURE_C = "feature_c"
    MEMORY = "memory"
    STACK = "stack"
    REST = "rest"  # Special tag representing all available tags
    DISPATCH = "dispatch"
    CACHE = "cache"
    BRANCH = "branch"
    POWER = "power"

class Priority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    RARE = "rare"

# Global priority weight mapping
PRIORITY_WEIGHTS = {
    Priority.HIGH: 20,    # High priority gets the highest weight
    Priority.MEDIUM: 10,  # Medium priority gets medium weight
    Priority.LOW: 5,      # Low priority gets a low weight
    Priority.RARE: 1,     # Rare priority gets the lowest weight
}

# Define the frequency enum with corresponding probability ranges
class Frequency(Enum):
    RARE = (0.001, 0.001)
    LOW = (0.05, 0.01)
    MED = (0.2, 0.05)
    HIGH = (0.4, 0.2)