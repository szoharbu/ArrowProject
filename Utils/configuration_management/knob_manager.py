from typing import Callable, Any, Dict, List
from Utils.logger_management import get_logger
from Utils.singleton_management import SingletonManager

class Knob:
    def __init__(self, name: str, value_func: [Callable[[], Any],List[Callable[[], Any]]], read_only: bool, dynamic: bool, global_knob: bool, description:str=None):
        """
        Initialize a knob.

        :param name: Name of the knob.
        :param value_func: Function to evaluate the knob's value (optional).
        :param read_only: Whether the knob can be modified.
        :param dynamic: Whether the knob's value should be evaluated every time it is accessed.
        :param global_knob: Whether the knob's value is shared across all states.
        """
        self.name = name
        self.value_func = value_func  # Function to evaluate the knob's value.
        self.read_only = read_only
        self.dynamic = dynamic
        self.global_knob = global_knob
        self.value_cache = None  # Cache for static values
        self.sealed = False  # Knob sealing mechanism
        self.description = description # Knob description

        # Automatically register the knob in the KnobManager
        knob_manager = get_knob_manager()
        knob_manager.add_knob(self)

    def get_value(self) -> Any:
        """Evaluate and return the knob's value."""
        if self.dynamic:
            # For dynamic knobs, evaluate the function every time
            if callable(self.value_func):
                return self.value_func()
            else:
                return self.value_func
        else:
            # For static knobs, cache the value on the first access
            if self.value_cache is None:
                if callable(self.value_func):
                    self.value_cache = self.value_func()
                else:
                    self.value_cache = self.value_func
            return self.value_cache

    def set_value(self, new_value: Any):
        """Set a new value for the knob if it is not read-only."""
        if self.sealed and self.read_only:
            raise ValueError(f"Knob '{self.name}' is read-only and cannot be modified.")
        self.value_func = new_value
        if not self.dynamic:
            self.value_cache = new_value

    def seal(self):
        """Seal the knob to prevent further modifications."""
        self.sealed = True

    # Implicit conversion methods
    def __bool__(self):
        return bool(self.get_value()) # Return the evaluated value as bool

    def __str__(self):
        return str(self.get_value())  # Return the evaluated value as string

    def __int__(self):
        return int(self.get_value())  # Return the evaluated value as integer

    def __float__(self):
        return float(self.get_value()) # Return the evaluated value as float

    def __repr__(self):
        return f"<Knob(name={self.name}, value={self.get_value()}, read_only={self.read_only}, dynamic={self.dynamic})>"


class KnobManager:

    def __init__(self):
        logger = get_logger()
        logger.info("======================== KnobManager")
        self.knobs: Dict[str, Knob] = {}

    def add_knob(self, knob: Knob):
        """Add a knob to the manager."""
        self.knobs[knob.name] = knob

    def get_knob(self, knob_name: str) -> Knob:
        """Retrieve a knob by name."""
        if knob_name in self.knobs:
            return self.knobs[knob_name]
        raise AttributeError(f"No knob found with the name: {knob_name}")

    def override_knob(self, name, new_value):
        """Override the value of a knob."""
        knob = self.get_knob(name)
        if knob:
            knob.set_value(new_value)
            self.knobs[name] = knob
        else:
            raise ValueError(f"Knob '{name}' not found.")

    def seal_all(self):
        """seal all knobs."""
        logger = get_logger()
        for knob in self.knobs.values():
            logger.debug(f"KNOBS INFO: {knob.name} = {knob.get_value()}")
            knob.seal()

    # def evaluate_knobs(self):
    #     """Evaluate all knobs and update their values if dynamic."""
    #     for knob in self.knobs.values():
    #         if knob.dynamic:
    #             knob.get_value()  # This updates the value for dynamic knobs

    def evaluate_knob(self, name):
        """Evaluate and return the value of a knob."""
        knob = self.get_knob(name)
        if knob:
            return knob.get_value()
        else:
            raise ValueError(f"Knob '{name}' not found.")

# Factory function to retrieve the KnobManager instance
def get_knob_manager():
    # Access or initialize the singleton variable
    knob_manager_instance = SingletonManager.get("knob_manager_instance", default=None)
    if knob_manager_instance is None:
        knob_manager_instance = KnobManager()
        SingletonManager.set("knob_manager_instance", knob_manager_instance)
    return knob_manager_instance
