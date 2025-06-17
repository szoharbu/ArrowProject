
from Arrow.Tool.asm_libraries.asm_logger import AsmLogger
from Arrow.Tool.state_management import get_current_state

from Arrow.Tool.exception_management import get_exception_manager, AArch64ExceptionVector
from Arrow.Tool.asm_libraries.exception.exception_base import ExceptionBase
from Arrow.Utils.configuration_management import Configuration

class Exception_arm(ExceptionBase):

    def __enter__(self):
        """
        Called at the start of the 'with' block. Prepares for the exception logic.
        """
        current_state = get_current_state()
        exception_manager = get_exception_manager()
        register_manager = current_state.register_manager

        current_el_page_table = current_state.current_el_page_table
        exception_table = exception_manager.get_exception_table(current_state.state_name, current_el_page_table.page_table_name)


        AsmLogger.comment(f"Starting exception with {self.exception} syndrome {self.exception_syndrome} handler {self.handler} callback {self.callback}")
        AsmLogger.asm(f"nop")


        # TODO:: set bit to support exception callback due to exception type and syndrome. then set the wanted callback address.
        # HACK:: at the moment I will handle a more generic case and assume that the exception syndrome and callback are the same for all exceptions.

        reg1 = register_manager.get_and_reserve(reg_type="gpr")
        reg2 = register_manager.get_and_reserve(reg_type="gpr")




        AsmLogger.asm(f"ldr {reg1}, ={exception_table.exception_callback_target[self.exception]}")  
        AsmLogger.asm(f"ldr {reg2}, ={self.end_of_scope_label}")
        AsmLogger.asm(f"str {reg2}, [{reg1}]", comment=f"storing the address of 'self.callback' into a memory to later be used by the handler")

        register_manager.free(reg1)
        register_manager.free(reg2)


        return self  # Return self to be used in the 'with' block

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Called at the end of the 'with' block. Cleans up any resources or finalizes logic.
        """
        current_state = get_current_state()

        AsmLogger.asm(f"nop")
        AsmLogger.asm(f"{self.end_of_scope_label}:")
        AsmLogger.asm(f"nop")
        
        return False  # False means exceptions are not suppressed
