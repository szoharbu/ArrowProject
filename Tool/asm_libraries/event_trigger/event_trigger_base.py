from abc import ABC, abstractmethod
import random
from Tool.asm_libraries.label import Label
from Utils.configuration_management import Configuration
from Tool.state_management import get_current_state
from Tool.memory_management.memory_operand import Memory

class EventTriggerBase(ABC):
    def __init__(
            self,
            frequency: Configuration.Frequency = Configuration.Frequency.LOW,
    ):
        """
        Constructor for the EventTrigger class.

        Parameters:
        - frequancy (Frequency): Defines the pattern to use

        Initializes and validates the input parameters.
        """
        current_state = get_current_state()

        self.frequency = frequency
        self.probability = random.uniform(*self.frequency.value)
        self.label = Label(postfix='skip_label')
        self.pattern = int(self.bit_pattern())

        operand_type = random.choice(["mem","reg"])
        if Configuration.Architecture.arm:
            operand_type = "reg"

        self.memory_with_pattern = Memory(init_value=self.pattern) # initializing memory with pattern value
        if operand_type == "mem":
            self.operand = self.memory_with_pattern
        else: # reg
            self.operand = current_state.register_manager.get_and_reserve()

    def bit_pattern(self):
        # Create a bit vector with the probability of bits being set according to frequency
        # The pattern has a low percentage of 1s, the rest are zeros
        vector_length = 8  # Adjust length for larger or smaller ranges
        bit_vector = [
            1 if random.random() < self.probability else 0
            for _ in range(vector_length)
        ]
        # Convert the list of bits into an integer
        bit_value = sum(bit << (vector_length - i - 1) for i, bit in enumerate(bit_vector))

        return bit_value

    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass