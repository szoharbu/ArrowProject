import random
from typing import Union, List, Dict, Any, Optional

def choice(
        values: Union[Dict[Any, int], List[Any]],
        name: Optional[str] = None,
) -> Any:
    """
    A function that selects a random element from either a weighted list (dict)
    or a uniform list.

    Args:
        name (str): The name of the choice.
        values (Union[Dict[Any, int], List[Any]]):
            - If a dict is provided, the keys are the values and the values are the weights.
            - If a list is provided, uniform random selection is performed.

    Returns:
        Any: The randomly selected value.
    """
    # If values is a dictionary (weighted list), use random.choices with weights
    if isinstance(values, dict):
        elements = list(values.keys())  # Extract the elements
        weights = list(values.values())  # Extract the weights
        return random.choices(elements, weights=weights, k=1)[0]

    # If values is a list (uniform list), use random.choice
    elif isinstance(values, list):
        return random.choice(values)

    # If neither a list nor a dictionary, raise a ValueError
    else:
        raise ValueError("Input must be either a list or a dictionary")

