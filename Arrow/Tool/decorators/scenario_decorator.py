
from typing import Optional, Callable, List, Union
from Arrow.Utils.configuration_management import Configuration
from Arrow.Tool.scenario_management import ScenarioTemplate, get_scenario_manager
from Arrow.Utils.configuration_management.enums import PrivilegeLevel


def scenario_decorator(
        random: bool = True,
        priority: Configuration.Priority = Configuration.Priority.MEDIUM,
        tags: List[Configuration.Tag] = None,
        precondition: Optional[Callable] = None,
        privilege_levels = PrivilegeLevel.ALL,
) -> Callable[[Callable], Callable]:
    """
    Decorator to register a function as a scenario with additional metadata.

    Args:
        random (bool): Whether the scenario is selectable randomly.
        priority (Tool.Priority): The priority level of the scenario (high, medium, low).
        tags: the provided list of tags to describe the scenario
        precondition: any relevant precondition to the scenario
        privilege_levels: The privilege levels where this scenario can execute.
                         Can be:
                         - PrivilegeLevel.ALL (default) which automatically expands to 
                           all privilege levels for the current architecture (e.g., all RISC-V levels 
                           if RISC-V architecture is active)
                         - A single privilege level enum (e.g., PrivilegeLevel.RISCV.MACHINE)
                         - A list of privilege level enums
    """
    def decorator(func: Callable) -> Callable:
        scenario_manager = get_scenario_manager()
        # Create a ScenarioTemplate object with the given metadata and function
        scenario_template = ScenarioTemplate(func, random, priority, tags, precondition, privilege_levels)
        # Add the template to the global scenario pool
        scenario_manager.add_scenario(scenario_template)
        return func  # Return the original function, not the ScenarioTemplate

    return decorator
