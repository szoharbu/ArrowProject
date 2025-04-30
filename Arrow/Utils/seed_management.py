import random
import numpy as np
from Utils.configuration_management import get_config_manager

def set_seed(seed):
    """
    Sets the random seed for reproducibility.
    """
    config_manager = get_config_manager()
    if seed:
        # received seed from command line
        config_manager.set_value('Seed', value=seed)
    else:
        # Generate a random seed if none is provided
        seed = random.randint(0, 2 ** 32 - 1)  # Random seed in range [0, 2^32-1]
        config_manager.set_value('Seed', value=seed)

    # Set the seed for the built-in random module
    random.seed(seed)

    # Set the seed for numpy random number generator
    np.random.seed(seed)

    return seed

    # If using PyTorch, set the seed (uncomment if needed)
    # import torch
    # torch.manual_seed(seed)
    # torch.cuda.manual_seed(seed)
    # torch.backends.cudnn.deterministic = True
    # torch.backends.cudnn.benchmark = False


# # Example function that uses randomness
# def random_number_example(seed=None):
#     set_seed()
#
#     # Generate random integers as an example
#     random_number = random.randint(1, 100)
#     numpy_random_number = np.random.randint(1, 100)
#
#     return random_number, numpy_random_number
#
# #
# # Usage
# print(random_number_example())  # Randomized behavior with a random seed
# print(random_number_example(42))  # Reproducible behavior with seed 42
