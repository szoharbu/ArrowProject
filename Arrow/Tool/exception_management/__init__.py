from enum import Enum
from typing import Dict
from Arrow.Tool.state_management import get_state_manager
from Arrow.Tool.state_management.switch_state import switch_code
from Arrow.Utils.singleton_management import SingletonManager
from Arrow.Tool.asm_libraries.asm_logger import AsmLogger
from Arrow.Utils.configuration_management import Configuration
from Arrow.Utils.logger_management import get_logger
from Arrow.Tool.memory_management.memlayout.segment import MemorySegment, CodeSegment
from Arrow.Tool.memory_management.memlayout.page_table_manager import get_page_table_manager
from Arrow.Tool.asm_libraries.label import Label
from Arrow.Tool.memory_management.memory_operand import Memory


'''
configure exception manager , per each of the page_table contexts 
'''

class AArch64ExceptionVector(Enum):
    # Current EL using SP0
    CURRENT_SP0_SYNCHRONOUS     = 0x000  # Synchronous
    CURRENT_SP0_IRQ             = 0x080  # IRQ/vIRQ
    CURRENT_SP0_FIQ             = 0x100  # FIQ/vFIQ
    CURRENT_SP0_SERROR          = 0x180  # SError/vSError

    # Current EL using SPx (not SP0)
    CURRENT_SPX_SYNCHRONOUS     = 0x200  # Synchronous
    CURRENT_SPX_IRQ             = 0x280  # IRQ/vIRQ
    CURRENT_SPX_FIQ             = 0x300  # FIQ/vFIQ
    CURRENT_SPX_SERROR          = 0x380  # SError/vSError

    # Lower EL using AArch64
    LOWER_A64_SYNCHRONOUS       = 0x400  # Synchronous
    LOWER_A64_IRQ               = 0x480  # IRQ/vIRQ
    LOWER_A64_FIQ               = 0x500  # FIQ/vFIQ
    LOWER_A64_SERROR            = 0x580  # SError/vSError

    # Lower EL using AArch32
    LOWER_A32_SYNCHRONOUS       = 0x600  # Synchronous
    LOWER_A32_IRQ               = 0x680  # IRQ/vIRQ
    LOWER_A32_FIQ               = 0x700  # FIQ/vFIQ
    LOWER_A32_SERROR            = 0x780  # SError/vSError




class ExceptionTable:
    def __init__(self, state_name:str, page_table_name:str):
        self.state_name = state_name
        self.page_table_name = page_table_name
        self.exception_entries:Dict[AArch64ExceptionVector, Label] = {}
        self.exception_callback_target:Dict[AArch64ExceptionVector, Label] = {}
        self.exception_table_segment: CodeSegment = None
        self.vbar_label = None

        page_table_manager = get_page_table_manager()
        self.page_table = page_table_manager.get_page_table(self.page_table_name)
        logger = get_logger()

        # Create the halting label once and use it consistently
        self.halting_label = Label(postfix="halting_label")
        self.callback_label = Label(postfix="callback_label")


    def get_exception(self, exception:AArch64ExceptionVector):
        return self.exception_entries.get(exception)
    
    def add_exception_callback(self, exception:AArch64ExceptionVector, target_label:str):
        #check if the exception already exists
        if self.get_exception(exception) is not None:
            raise Exception(f"Exception already exists for {exception}")
        
        if target_label == "callback_label":
            self.exception_entries[exception] = self.callback_label

        # if already populated, use assembly mode to add the exception
        #     use assembly mode to add the exception

    def get_vbar_label(self):
        if self.vbar_label is None:
            raise Exception(f"VBAR label is not set for {self.page_table_name}, please make sure to populate the page table first")
        return self.vbar_label
    
    def populate_exception_table(self):
        state_manager = get_state_manager()
        orig_state = state_manager.get_active_state()
        tmp_state = state_manager.set_active_state(self.state_name)
        tmp_state_original_page_table = tmp_state.current_el_page_table
        tmp_state.current_el_page_table = self.page_table

        segment_manager = self.page_table.segment_manager
        self.exception_table_segment = segment_manager.allocate_memory_segment(name=f"exception_table_{self.page_table_name}",
                                                                        byte_size=0x800,
                                                                        memory_type=Configuration.Memory_types.CODE, 
                                                                        alignment_bits=11) # ensure 2KB alignment for VBAR_EL3

        self.vbar_label = self.exception_table_segment.get_start_label()


        # set default target to each of the exceptions that don't have a target
        for exception in AArch64ExceptionVector:
            if exception not in self.exception_entries:
                self.exception_entries[exception] = self.halting_label
            if exception not in self.exception_callback_target:
                self.exception_callback_target[exception] = None

        orig_code_block = orig_state.current_code_block
        tmp_state.current_code_block = self.exception_table_segment

        AsmLogger.comment(f"================ exception table for {self.state_name} {self.page_table_name} =====================")
        for exception in AArch64ExceptionVector:
            target_label = self.exception_entries[exception]
            AsmLogger.asm(f".org {hex(exception.value)}")
            AsmLogger.comment(f" exception {exception} - target label {target_label} ")
            AsmLogger.asm(f"b {target_label}")


        AsmLogger.asm(f"{self.halting_label}:")
        AsmLogger.comment(f"default halting hander")
        AsmLogger.asm(f"nop")

        print(f"Exception handling:: WA WA WA - need to randomize and protect the register, at the moment hard-coding x0 - remove after")
        # print(f"WA WA WA - need to randomize and protect the register, at the moment hard-coding x0 - remove after")
        # print(f"WA WA WA - need to randomize and protect the register, at the moment hard-coding x0 - remove after")

        print(f"Exception handling:: WA WA WA - at the moment hard-coding support for UD case. need to generelize - remove after")
        # print(f"WA WA WA - at the moment hard-coding support for UD case. need to generelize - remove after")
        # print(f"WA WA WA - at the moment hard-coding support for UD case. need to generelize - remove after")


        halting_callback_memory = Memory(name=f"{self.page_table_name}__exception_callback_LOWER_A64_SYNC", byte_size=8, init_value=0x0)
        self.exception_callback_target[AArch64ExceptionVector.CURRENT_SPX_SYNCHRONOUS] = halting_callback_memory.get_label()        

        halting_handler_test_fail_label = Label(postfix="halting_handler_test_fail_label")

        AsmLogger.asm(f"mrs x0, esr_el1", comment="Read cause of exception")
        AsmLogger.asm(f"ubfx x1, x0, #26, #6", comment="Extract EC (bits[31:26])")
        AsmLogger.asm(f"cmp x1, #0x00", comment="EC = 0b000000 = undefined instruction")
        AsmLogger.asm(f"b.ne {halting_handler_test_fail_label}", comment="handle undefined instruction")

        AsmLogger.asm(f"ldr x0, ={self.exception_callback_target[AArch64ExceptionVector.CURRENT_SPX_SYNCHRONOUS]}")
        AsmLogger.asm(f"ldr x1, [x0]")
        AsmLogger.asm(f"br x1")

        AsmLogger.asm(f"{halting_handler_test_fail_label}:")
        from Arrow.Tool.asm_libraries import end_test
        end_test.end_test_asm_convention(test_pass=False)


        AsmLogger.asm(f"{self.callback_label}:")
        AsmLogger.comment(f"default callback handler ")
        AsmLogger.asm(f"nop")

        print(f"Exception handling:: WA WA WA - need to randomize and protect the register, at the moment hard-coding x0 - remove after")
        # print(f"WA WA WA - need to randomize and protect the register, at the moment hard-coding x0 - remove after")
        # print(f"WA WA WA - need to randomize and protect the register, at the moment hard-coding x0 - remove after")

        print(f"Exception handling:: WA WA WA - assume callback is hardcoded for LOWER_A64_SYNCHRONOUS - not accurate - remove after")
        # print(f"WA WA WA - assume callback is hardcoded for LOWER_A64_SYNCHRONOUS - not accurate - remove after")
        # print(f"WA WA WA - assume callback is hardcoded for LOWER_A64_SYNCHRONOUS - not accurate - remove after")


        skipping_callback_memory = Memory(name=f"{self.page_table_name}__exception_callback_LOWER_A64_SYNC", byte_size=8, init_value=0x0)
        self.exception_callback_target[AArch64ExceptionVector.LOWER_A64_SYNCHRONOUS] = skipping_callback_memory.get_label()        

        AsmLogger.asm(f"ldr x0, ={self.exception_callback_target[AArch64ExceptionVector.LOWER_A64_SYNCHRONOUS]}")
        AsmLogger.asm(f"ldr x1, [x0]")
        AsmLogger.asm(f"br x1")
       

        AsmLogger.comment(f"================ end of exception table for {self.state_name} {self.page_table_name} ===============")

        tmp_state.current_el_page_table = tmp_state_original_page_table
        tmp_state.current_code_block = orig_code_block
        state_manager.set_active_state(orig_state.state_name)

class ExceptionManager:
    def __init__(self):

        self.exception_table_dict = []

    def add_exception_table(self, state_name:str, page_table_name:str):

        #check if the exception table already exists
        if self.get_exception_table(state_name, page_table_name) is not None:
            raise Exception(f"Exception table already exists for state {state_name} and page table {page_table_name}")
        
        #add the exception table to the dictionary
        exception_table = ExceptionTable(state_name, page_table_name)
        self.exception_table_dict.append(exception_table)
        return exception_table

    def get_exception_table(self, state_name:str, page_table_name:str):
        for exception_table in self.exception_table_dict:
            if exception_table.state_name == state_name and exception_table.page_table_name == page_table_name:
                return exception_table
        return None
    
    def get_all_exception_tables(self, state_name:str):
        if state_name is None:
            return self.exception_table_dict
        else:
            return [exception_table for exception_table in self.exception_table_dict if exception_table.state_name == state_name]
    

# Factory function to retrieve the ExceptionManager instance
def get_exception_manager():
    # Access or initialize the singleton variable
    exception_manager_instance = SingletonManager.get("exception_manager_instance", default=None)
    if exception_manager_instance is None:
        exception_manager_instance = ExceptionManager()
        SingletonManager.set("exception_manager_instance", exception_manager_instance)
    return exception_manager_instance
