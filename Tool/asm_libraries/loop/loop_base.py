from abc import ABC, abstractmethod
from typing import Optional
from Tool.frontend.choice import choice
from Tool.asm_libraries.label import Label
from Tool.frontend.sources_API import Sources

class LoopBase(ABC):
    def __init__(
            self,
            counter: int,
            counter_type:Optional[str] = None,
            counter_direction:Optional[str] = None,
            label:Optional[str] = None,
    ):
        """
        Constructor for the AssemblyLoop class.

        Parameters:
        - counter (int): The number of iterations for the loop. Must be a non-negative integer.
        - counter_type (str, optional): Defines where the counter is stored, either 'memory' or 'register' operand.
        - counter_direction (str, optional): Defines the type of loop behavior, either 'increment' or 'decrement'.
        - label (str, optional): Defines the loop label.

        Initializes and validates the input parameters.
        """

        # Validation for the inputs
        if not isinstance(counter, int) or counter < 0:
            raise ValueError("Counter must be a non-negative integer.")

        if counter_type is None:
            #counter_type = random.choice(['memory', 'register'])
            counter_type = 'register' # Memory is not yet supported in this beta version
        elif counter_type not in ['memory', 'register']:
            raise ValueError("Counter type must be 'memory' or 'register'.")

        if counter_direction is None:
            counter_direction = choice(values={'increment': 70, 'decrement': 30})
        elif counter_direction not in ['increment', 'decrement']:
            raise ValueError("Counter direction must be 'increment' or 'decrement'.")

        if label is None:
            label = Label(postfix="loop_label")
        else:
            if not isinstance(label, Label):
                raise ValueError("Label must be of type Label. please use Tool.Label() to create a label.")

        self.counter = counter
        self.counter_type = counter_type
        self.counter_direction = counter_direction
        self.label = label

        if self.counter_type == 'register':
            self.counter_operand = Sources.RegisterManager.get_and_reserve()
        else:  # counter_type == 'memory':
            raise ValueError("Counter type Memory is not yet supported in this beta version.")

    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
