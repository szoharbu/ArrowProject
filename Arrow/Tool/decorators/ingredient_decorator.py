from typing import Callable, List, Optional, Dict, Union
from Arrow.Utils.configuration_management import Configuration
from Arrow.Tool.ingredient_management import get_ingredient_manager

# Decorator for registering ingredients with optional params
def ingredient_decorator(
        random: bool = True,
        priority: Configuration.Priority = Configuration.Priority.MEDIUM,
        tags: Union[List[Configuration.Tag], Dict[Configuration.Tag,int]] = None,
        precondition: Optional[Callable|bool] = None,
):
    def decorator(cls):
        # Register the ingredient in the manager
        ingredient_manager = get_ingredient_manager()
        ingredient_manager.add_ingredient(cls)
        # Add random and priority as class attributes
        cls.random = random
        cls.priority = priority
        cls.precondition = precondition

        if tags is None:
            cls.tags = [Configuration.Tag.REST]
        elif isinstance(tags, list):
            cls.tags = tags
            cls.tags.append(Configuration.Tag.REST)
        else:
            raise TypeError(f"Expected tags input to be of type list or None, received {type(tags)}")

        # # Handle both dict and list for tags
        # if isinstance(tags, list):
        #     # If tags is a list, convert it to a dict with equal weights
        #     equal_weight = 100 / len(tags) if tags else 0  # Avoid division by zero
        #     cls.tags = {tag: equal_weight for tag in tags}
        # elif isinstance(tags, dict):
        #     cls.tags = tags
        # else:
        #     cls.tags = {}

        # Add a custom __str__ method to the class if not already present
        if not hasattr(cls, '__str__'):
            def __str__(self):
                return f"{self.__class__.__name__}(random={self.random}, priority={self.priority})"
            cls.__str__ = __str__
        return cls

    return decorator
