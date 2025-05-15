import random
import inspect
from typing import Union, Dict, Any, Tuple
from Arrow.Utils.singleton_management import SingletonManager


class AdaptiveChoiceManager:
    def __init__(self):
        self.contexts = {}

    def adaptive_choice(self, values: Dict[Any, Union[int, Tuple[int, int]]]) -> Any:
        """
        A function that selects a random element based on weights or weight ranges,
        generating distributions dynamically and associating them with the file and line number.

        Args:
            values (Dict[Any, Union[int, Tuple[int, int]]]):
                - Keys are the elements to choose from.
                - Values are either fixed weights (int) or weight ranges (tuple of two ints).

        Returns:
            Any: The randomly selected value.
        """
        # Get the file and line number of the caller
        frame = inspect.currentframe()
        caller_frame = frame.f_back if frame else None
        caller_info = (caller_frame.f_code.co_filename, caller_frame.f_lineno) if caller_frame else None

        # Check if the distribution for this file-line identifier is already stored
        if caller_info not in self.contexts:
            elements = list(values.keys())
            weights = []

            # Generate weights based on the provided values
            for key, weight in values.items():
                if isinstance(weight, tuple) and len(weight) == 2:  # Weight range
                    # Ensure the range is valid
                    lower, upper = sorted(weight)  # Sort the range to ensure lower <= upper
                    weights.append(random.randint(lower, upper))
                    #weights.append(random.randint(weight[0], weight[1]))
                elif isinstance(weight, int):  # Fixed weight
                    weights.append(weight)
                else:
                    raise ValueError("Weights must be either integers or (min, max) tuples.")

            # Normalize weights to ensure they sum to 1
            total = sum(weights)
            if total == 0:
                raise ValueError("Sum of weights cannot be zero.")
            normalized_weights = [w / total for w in weights]

            # Store the distribution for this context
            self.contexts[caller_info] = (elements, normalized_weights)

        # Retrieve the stored distribution and make a choice
        elements, weights = self.contexts[caller_info]
        return random.choices(elements, weights=weights, k=1)[0]


# Factory function to retrieve the AdaptiveChoiceManager instance
def get_adaptive_choice_manager():
    # Access or initialize the singleton variable
    adaptive_choice_manager_instance = SingletonManager.get("adaptive_choice_manager_instance", default=None)
    if adaptive_choice_manager_instance is None:
        adaptive_choice_manager_instance = AdaptiveChoiceManager()

        SingletonManager.set("adaptive_choice_manager_instance", adaptive_choice_manager_instance)
    return adaptive_choice_manager_instance


def adaptive_choice(values: Dict[Any, Union[int, Tuple[int, int]]]) -> Any:
    """
    Public API for adaptive_choice. Delegates to AdaptiveChoiceManager.
    """
    adaptive_choice_manager = get_adaptive_choice_manager()
    return adaptive_choice_manager.adaptive_choice(values)
