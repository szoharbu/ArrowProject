
from typing import Optional, Callable, List
from Utils.configuration_management import Configuration
from Tool.scenario_management import ScenarioWrapper, get_scenario_manager


def scenario_decorator(
        random: bool = True,
        priority: Configuration.Priority = Configuration.Priority.MEDIUM,
        tags: List[Configuration.Tag] = None,
        precondition: Optional[Callable] = None,
) -> Callable[[Callable], Callable]:
    """
    Decorator to register a function as a scenario with additional metadata.

    Args:
        random (bool): Whether the scenario is selectable randomly.
        priority (Tool.Priority): The priority level of the scenario (high, medium, low).
        tags: the provided list of tags to describe the scenario
        precondition: any relevant precondition to the scenario
    """
    def decorator(func: Callable) -> Callable:
        scenario_manager = get_scenario_manager()
        # Create a ScenarioWrapper object with the given metadata and function
        scenario_instance = ScenarioWrapper(func, random, priority, tags, precondition)
        # Add the scenario to the global _scenarios_pool
        scenario_manager.add_scenario(scenario_instance)
        return func  # Return the original function, not the ScenarioWrapper

    return decorator
