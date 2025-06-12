from abc import ABC, abstractmethod
import random
from Tool.asm_libraries.label import Label
from Utils.configuration_management import Configuration
from Tool.state_management import get_current_state
from Tool.memory_management.memory_operand import Memory
from Tool.asm_libraries.asm_logger import AsmLogger

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

        self.memory_with_pattern = Memory(init_value=self.pattern, byte_size=8) # initializing memory with pattern value
        if operand_type == "mem":
            self.operand = self.memory_with_pattern
        else: # reg
            self.operand = current_state.register_manager.get_and_reserve()

        AsmLogger.comment(f"EventTrigger:: Setting event trigger flow with {self.frequency} frequency ")
        AsmLogger.comment(f"EventTrigger:: Using mem at {hex(self.memory_with_pattern.get_address())} with the following 64bit pattern: {self.pattern:064b}")

    def bit_pattern(self):
        # Create a bit vector with the probability of bits being set according to frequency
        # The pattern has a low percentage of 1s, the rest are zeros
        vector_length = 64  # Changed from 8 to 64 for a 64-bit vector
        
        prob_min, prob_max = self.frequency.value
        if prob_min > prob_max:
            raise ValueError(f"Invalid frequency range: {prob_min} > {prob_max}")
        
        # Generate probability within the corrected range
        corrected_probability = random.uniform(prob_min, prob_max)
        
        bit_vector = [
            1 if random.random() < corrected_probability else 0
            for _ in range(vector_length)
        ]
        
        # Ensure at least one bit is set to 1
        if sum(bit_vector) == 0:
            # Set a random bit to 1
            random_index = random.randint(0, vector_length - 1)
            bit_vector[random_index] = 1
        
        # Convert the list of bits into an integer
        bit_value = sum(bit << (vector_length - i - 1) for i, bit in enumerate(bit_vector))
        
        # Ensure the value fits within 64 bits (8 bytes) by masking to 64-bit maximum
        bit_value = bit_value & ((1 << 64) - 1)

        return bit_value

    @abstractmethod
    def __enter__(self):
        pass

    @abstractmethod
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass