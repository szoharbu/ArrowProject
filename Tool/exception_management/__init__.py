from enum import Enum
from typing import Dict
from Tool.state_management import get_state_manager
from Tool.state_management.switch_state import switch_code
from Utils.singleton_management import SingletonManager
from Tool.asm_libraries.asm_logger import AsmLogger
from Utils.configuration_management import Configuration
from Utils.logger_management import get_logger
from Tool.memory_management.memlayout.segment import MemorySegment, CodeSegment
from Tool.memory_management.memlayout.page_table_manager import get_page_table_manager
from Tool.asm_libraries.label import Label
'''
configure exception manager , per each of the page_table contexts 
'''

class Exception_type(Enum):
    SVC = "SVC"
    BRANCH = "BRANCH"
    DATA_ABORT = "DATA_ABORT"
    INSTRUCTION_ABORT = "INSTRUCTION_ABORT"
    UNDEFINED = "UNDEFINED"
    SYNC = "SYNC"
    IRQ = "IRQ"
    FIQ = "FIQ"

# def get_exception_offset(exception:Exception_type):
#     if exception == Exception_type.SVC:
#         return 0
#     elif exception == Exception_type.BRANCH:
#         return 1
#     elif exception == Exception_type.DATA_ABORT:
#         return 2
#     elif exception == Exception_type.INSTRUCTION_ABORT:
#         return 3

class ExceptionTable:
    def __init__(self, state_name:str, page_table_name:str):
        self.state_name = state_name
        self.page_table_name = page_table_name
        self.exception_entries:Dict[Exception_type, Label] = {}
        self.exception_table_segment: CodeSegment = None
        self.vbar_label = None

        page_table_manager = get_page_table_manager()
        self.page_table = page_table_manager.get_page_table(self.page_table_name)
        logger = get_logger()

    def get_exception(self, exception:Exception_type):
        return self.exception_entries.get(exception)
    
    def add_exception(self, exception:Exception_type, target_label:str):
        #check if the exception already exists
        if self.get_exception(exception) is not None:
            raise Exception(f"Exception already exists for {exception}")
        self.exception_entries[exception] = target_label

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

        segment_manager = self.page_table.segment_manager
        self.exception_table_segment = segment_manager.allocate_memory_segment(name=f"exception_table_{self.page_table_name}",
                                                                        byte_size=0x800,
                                                                        memory_type=Configuration.Memory_types.CODE, 
                                                                        alignment_bits=11) # ensure 2KB alignment for VBAR_EL3

        self.vbar_label = self.exception_table_segment.get_start_label()

        # Create the halting label once and use it consistently
        halting_label = Label(postfix="halting_label")
        
        # set default target to each of the exceptions that don't have a target
        for exception in Exception_type:
            if exception not in self.exception_entries:
                self.exception_entries[exception] = halting_label

        orig_code_block = orig_state.current_code_block
        tmp_state.current_code_block = self.exception_table_segment

        AsmLogger.comment(f"================ exception table for {self.state_name} {self.page_table_name} =====================")
        offset = 0x80
        for exception in Exception_type:
            target_label = self.exception_entries[exception]
            AsmLogger.comment(f" exception {exception} - target label {target_label} ")
            AsmLogger.asm(f"b {target_label}")
            AsmLogger.asm(f".org {hex(offset)}")
            offset += 0x80
        AsmLogger.comment(f"default target to halting_label")
        AsmLogger.asm(f"{halting_label}:")
        AsmLogger.asm(f"nop")

        AsmLogger.comment(f"================ end of exception table for {self.state_name} {self.page_table_name} ===============")

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
    
    def get_all_exception_tables(self):
        return self.exception_table_dict
    

# Factory function to retrieve the ExceptionManager instance
def get_exception_manager():
    # Access or initialize the singleton variable
    exception_manager_instance = SingletonManager.get("exception_manager_instance", default=None)
    if exception_manager_instance is None:
        exception_manager_instance = ExceptionManager()
        SingletonManager.set("exception_manager_instance", exception_manager_instance)
    return exception_manager_instance
