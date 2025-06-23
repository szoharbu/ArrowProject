from typing import Optional, Dict, Callable, Union, List
from Arrow.Utils.singleton_management import SingletonManager
from Arrow.Utils.configuration_management import Configuration
from Arrow.Utils.logger_management import get_logger
from Arrow.Utils.APIs.choice import choice

class ScenarioWrapper:
    """
    Class representing a scenario with metadata.
    """
    def __init__(
            self,
            _func: Callable,
            random: bool = False,
            priority:  Configuration.Priority = Configuration.Priority.MEDIUM,
            tags: list[Configuration.Tag] = None,
            precondition: Optional[Callable] = None,
    ):
        if not callable(_func):
            raise TypeError(f"Variable function has to be callable. Got {type(_func)}.")

        self.func = _func
        self._name = _func.__name__  # Use a different internal name to avoid conflict
        self.random = random
        self.priority = priority
        self.tags = tags
        self.precondition = precondition  # Function that returns True/False based on scenario-specific logic

        if tags is None:
            self.tags = [Configuration.Tag.REST]
        elif isinstance(tags, list):
            self.tags.append(Configuration.Tag.REST)
        else:
            raise TypeError(f"Expected tags input to be of type list or None, received {type(tags)}")

    def name(self) -> str:
        """Return the function's name."""
        return self._name

    def __str__(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return f"Scenario(func={self._name}, random={self.random}, priority={self.priority})"

    def check_precondition(self) -> bool:
        # Evaluate the precondition if it exists; if no precondition, return True by default
        if self.precondition:
            return self.precondition()
        return True  # No precondition means it's always valid


class ScenarioManager:
    """
    Manager to handle the storage, selection, and filtering of scenarios.
    """
    def __init__(self):
        logger = get_logger()
        logger.info("======================== ScenarioManager")
        self._scenarios_pool = []

    def list_scenarios(self):
        """Return a list of all scenarios for debugging or reporting purposes."""
        return self._scenarios_pool

    def add_scenario(self, scenario: ScenarioWrapper):
        """
        Add a new scenario to the pool.

        Args:
            scenario (ScenarioWrapper): The scenario instance to add.

        Raises:
            ValueError: If a scenario with the same name already exists in the pool.
        """
        #print(f"Adding scenario {scenario.name()}")
        # Check if a scenario with the same name already exists
        if any(existing_scenario.name() == scenario.name() for existing_scenario in self._scenarios_pool):
            raise ValueError(f"A scenario with the name '{scenario.name()}' already exists in the pool.")

        # Add the scenario to the pool
        logger = get_logger()
        logger.debug(f"Add new scenario {scenario.name()}")
        self._scenarios_pool.append(scenario)

    # Functions to query scenarios
    def get_scenario_by_name(self, name: str) -> Optional[ScenarioWrapper]:
        """
        Retrieve a scenario by its function name.

        Args:
            name (str): The name of the scenario function.

        Returns:
            ScenarioWrapper: The ScenarioWrapper object or None if not found.
        """
        for scenario_inst in self._scenarios_pool:
            if scenario_inst.name() == name:
                return scenario_inst

        raise ValueError(f"Scenario '{name}' not found.")


    def get_random_scenario(self, tags: Optional[Union[Dict[Configuration.Tag, int],List[Configuration.Tag]]] = None, _precondition_retries: int = 10) -> ScenarioWrapper:
        """
            Returns a single random scenario that matches the tag distribution, is random=True, satisfies the precondition, and
            takes into account priority levels (higher priority scenarios have higher selection weight).
            If no tags are provided, treat it as 100% REST tag.

            Args:
                tags (Optional[Dict[Tool.Tag, int]]): A dictionary of tags and their weights.
                _precondition_retries (int): The number of times to try finding a valid scenario before raising an error.

            Returns:
                ScenarioWrapper: A valid scenario that fits the requirements.

            Raises:
                ValueError: If no valid scenario is found after 'retries' attempts.
        """

        # Filter scenarios that have random=True
        random_scenarios = [s for s in self._scenarios_pool if s.random]

        if not random_scenarios:
            raise ValueError("No random scenarios available.")


        if tags is None:
            # If no tags provided, default to 100% REST
            tags = {Configuration.Tag.REST: 100}
        elif isinstance(tags, list):
            # If tags is a list, convert to dict with uniform weights
            uniform_weight = 100 / len(tags) if tags else 0  # Avoid division by zero
            tags = {tag: uniform_weight for tag in tags}
        elif isinstance(tags, dict):
            # list is of the correct instance, do nothing
            pass
        else:
            # list is at an invalid type
            raise TypeError(f"Expected 'tags' to be a dictionary or List, but got {type(tags).__name__}")

        '''
        Calculate Combined Weights: 
        For each object, calculate a weight based on both its priority and the requested tag distribution. 
        This combined weight can be the product of the object's priority and the distribution weight for each tag it has.
        Construct a Weighted List: 
        Create a list where each object appears with its combined weight. 
        This list will include all objects with weights that reflect both the priority and the tag distribution.
        Weighted Sampling: 
        Use a single weighted random selection based on these combined weights to choose the required number of objects.
        '''

        # Step 1: Calculate combined weights for each object
        weighted_objects_dict = {}
        total_weight = 0
        for scenario in random_scenarios:
            # calculate based on tags sum
            tag_weights = sum(tags.get(tag, 0) for tag in scenario.tags)
            combined_weight = Configuration.PRIORITY_WEIGHTS[scenario.priority] * tag_weights

            # Only add to the list if combined_weight > 0
            if combined_weight > 0:
                total_weight += combined_weight
                weighted_objects_dict[scenario] = combined_weight

        # Step 2: handle "direct" scenarios, calculate their weight and add to dict

        for scenario in random_scenarios:
            if str(scenario) in tags.keys():
                # calculate relative weight
                direct_scenario_portion = tags[str(scenario)] / sum(tags.values())
                all_other_portion = 1 - direct_scenario_portion
                overall_weight = total_weight / all_other_portion
                weighted_objects_dict[scenario] = overall_weight * direct_scenario_portion

        # Step 3: use `Tool.choices` to randomize from weighted_objects_dict

        # Create a mapping of scenarios by tag, and ensure scenarios without tags are part of REST
        if not weighted_objects_dict:
            raise RuntimeError("No valid tags found with associated scenarios.")

        for _ in range(_precondition_retries):
            candidate = choice(values=weighted_objects_dict)

            # Check precondition, if it exists and is callable
            if hasattr(candidate, 'precondition') and callable(candidate.precondition):
                if candidate.precondition():  # Call precondition if it exists
                    return candidate # Return the Selected ScenarioWrapper
            else:
                # If there is no precondition, treat it as valid
                return candidate

        # if we reached here, all retries have ended without a return value
        raise RuntimeError("Failed to find a suitable scenario after multiple retries.")


# Factory function to retrieve the ScenarioManager instance
def get_scenario_manager():
    # Access or initialize the singleton variable
    scenario_manager_instance = SingletonManager.get("scenario_manager_instance", default=None)
    if scenario_manager_instance is None:
        scenario_manager_instance = ScenarioManager()
        SingletonManager.set("scenario_manager_instance", scenario_manager_instance)
    return scenario_manager_instance
