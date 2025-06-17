from abc import ABC, abstractmethod
from typing import Optional
from Arrow.Utils.APIs.choice import choice
from Arrow.Tool.state_management import get_current_state
from Arrow.Tool.asm_libraries.label import Label
from Arrow.Tool.exception_management import get_exception_manager, AArch64ExceptionVector


class ExceptionBase(ABC):
    def __init__(
            self,
            exception: AArch64ExceptionVector,
            exception_syndrome: Optional[str] = None,
            handler: Optional[str] = None,
            callback: Optional[str] = None,
    ):
        """
        Constructor for the AssemblyException class.

        Parameters:
        - exception (AArch64ExceptionVector): The exception to handle.

        Initializes and validates the input parameters.
        """
        current_state = get_current_state()

        # Validation for the inputs
        if not isinstance(exception, AArch64ExceptionVector):
            raise ValueError("Exception must be of type AArch64ExceptionVector.")

        self.exception = exception
        self.exception_syndrome = exception_syndrome
        self.handler = handler
        self.callback = callback
        self.end_of_scope_label = Label(postfix="end_of_exception_scope_label")

    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
