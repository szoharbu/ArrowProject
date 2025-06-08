from Utils.configuration_management import Configuration, get_config_manager
from Utils.logger_management import get_logger

class Page:
    """Represents a single page mapping in the page table"""
    
    
    # Permission flags
    PERM_READ = 0x1
    PERM_WRITE = 0x2
    PERM_EXECUTE = 0x4
    
    # Cacheability options
    CACHE_NONE = "non-cacheable"
    CACHE_WT = "write-through"
    CACHE_WB = "write-back"
    
    # Shareability domains
    SHARE_NONE = "non-shareable"
    SHARE_INNER = "inner-shareable"
    SHARE_OUTER = "outer-shareable"
    
    def __init__(self, va, pa, size, page_type=Configuration.Page_types, permissions=PERM_READ, 
                 cacheable=CACHE_WB, shareable=SHARE_NONE, execution_context=Configuration.Execution_context.EL3, 
                 custom_attributes=None, is_cross_core=False):
        """
        Initialize a page mapping with detailed memory attributes.
        
        Args:
            va (int): Virtual address of the page
            pa (int): Physical address of the page
            size (int): Size of the page in bytes
            page_type (str): Type of memory (code, data, device, system)
            permissions (int): Combination of PERM_READ, PERM_WRITE, PERM_EXECUTE
            cacheable (str): Cacheability setting
            shareable (str): Shareability domain
            execution_context (Configuration.Execution_context): Execution context (EL3, EL1_NS, EL1_S, EL2_NS, EL2_S, EL0_NS, EL0_S, EL0_Realm)
            custom_attributes (dict): Any additional custom attributes
            is_cross_core (bool): Whether the page is cross-core
        """
        self.va = va
        self.pa = pa
        self.size = size
        self.page_type = page_type
        self.permissions = permissions
        self.cacheable = cacheable
        self.shareable = shareable
        self.execution_context = execution_context
        self.custom_attributes = custom_attributes or {}
        self.is_cross_core = is_cross_core

    @property
    def is_readable(self):
        """Check if page is readable"""
        return bool(self.permissions & self.PERM_READ)
        
    @property
    def is_writable(self):
        """Check if page is writable"""
        return bool(self.permissions & self.PERM_WRITE)
        
    @property
    def is_executable(self):
        """Check if page is executable"""
        return bool(self.permissions & self.PERM_EXECUTE)
            
    @property
    def end_va(self):
        """Virtual address of the last byte in this page"""
        return self.va + self.size - 1
        
    @property
    def end_pa(self):
        """Physical address of the last byte in this page"""
        return self.pa + self.size - 1
    
    def contains_va(self, address):
        """Check if this page contains the given virtual address"""
        return self.va <= address <= self.end_va
    
    def contains_pa(self, address):
        """Check if this page contains the given physical address"""
        return self.pa <= address <= self.end_pa
    
    def va_to_pa(self, va_address):
        """Convert a virtual address to its corresponding physical address"""
        if not self.contains_va(va_address):
            raise ValueError(f"Virtual address 0x{va_address:x} not in this page")
        offset = va_address - self.va
        return self.pa + offset
    
    def pa_to_va(self, pa_address):
        """Convert a physical address to its corresponding virtual address"""
        if not self.contains_pa(pa_address):
            raise ValueError(f"Physical address 0x{pa_address:x} not in this page")
        offset = pa_address - self.pa
        return self.va + offset
    
    def get_attributes_dict(self):
        """Get all attributes as a dictionary"""
        return {
            "type": self.page_type,
            "permissions": {
                "read": self.is_readable,
                "write": self.is_writable,
                "execute": self.is_executable
            },
            "cacheable": self.cacheable,
            "shareable": self.shareable,
            "execution_context": self.execution_context,
            **self.custom_attributes
        }
        
    def get_mmu_attributes(self):
        """
        Convert page attributes to MMU-specific format.
        This would be implemented based on the specific architecture (ARM, etc.)
        """
        # Example for ARM MMUs - actual implementation would be more complex
        attr = 0
        
        # Set permission bits
        if self.is_readable:
            attr |= 0x1
        if self.is_writable:
            attr |= 0x2
        if self.is_executable:
            attr &= ~0x4  # In ARM, XN bit=0 means executable
        else:
            attr |= 0x4   # XN bit=1 means non-executable
            
        # Set memory type bits (this is simplified)
        if self.cacheable == self.CACHE_WB:
            attr |= 0x8
        elif self.cacheable == self.CACHE_WT:
            attr |= 0x10
            
        # Set shareability bits
        if self.shareable == self.SHARE_INNER:
            attr |= 0x20
        elif self.shareable == self.SHARE_OUTER:
            attr |= 0x40
            
        return attr
    
    def __repr__(self):
        """String representation of the page"""
        perms = []
        if self.is_readable:
            perms.append("R")
        if self.is_writable:
            perms.append("W")
        if self.is_executable:
            perms.append("X")
            
        return (f"Page(VA:0x{self.va:x}-0x{self.end_va:x}, "
                f"PA:0x{self.pa:x}-0x{self.end_pa:x}, "
                f"0x{self.size:x} bytes, {self.page_type}, "
                f"{''.join(perms)}, {self.cacheable}, is_cross_core: {self.is_cross_core})")

