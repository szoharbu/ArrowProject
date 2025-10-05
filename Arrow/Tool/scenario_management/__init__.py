from typing import Optional, Dict, Callable, Union, List
from collections import defaultdict
from Arrow.Utils.singleton_management import SingletonManager
from Arrow.Utils.configuration_management import Configuration
from Arrow.Utils.logger_management import get_logger
from Arrow.Utils.APIs.choice import choice
from Arrow.Tool.asm_libraries import label, end_test
from Arrow.Utils.configuration_management.enums import PrivilegeLevel


class ScenarioTemplate:
    """
    Template class that stores scenario metadata and function without creating runtime instances.
    Used to create fresh ScenarioWrapper instances on demand.
    """
    def __init__(
            self,
            _func: Callable,
            random: bool = False,
            priority = Configuration.Priority.MEDIUM,
            tags: List = None,
            precondition: Optional[Callable] = None,
            privilege_levels: Union[List[PrivilegeLevel], PrivilegeLevel] = PrivilegeLevel.ALL,
    ):
        if not callable(_func):
            raise TypeError(f"Variable function has to be callable. Got {type(_func)}.")

        self._func = _func
        self._name = getattr(_func, '__name__', 'unknown')
        self.random = random
        self.priority = priority
        self.precondition = precondition
        
        # Handle privilege levels
        if privilege_levels == PrivilegeLevel.ALL:
            # Expand ALL to include all privilege levels for the current architecture
            if Configuration.Architecture.riscv:
                # Add all RISC-V privilege levels
                self.privilege_levels = [
                    PrivilegeLevel.RISCV.USER,
                    PrivilegeLevel.RISCV.SUPERVISOR, 
                    PrivilegeLevel.RISCV.HYPERVISOR,
                    PrivilegeLevel.RISCV.MACHINE
                ]
            elif Configuration.Architecture.arm:
                # Future: Add all ARM privilege levels when implemented
                raise NotImplementedError("ARM privilege levels not yet implemented.")
            elif Configuration.Architecture.x86:
                # Future: Add all x86 privilege levels when implemented
                raise NotImplementedError("x86 privilege levels not yet implemented.")
        elif isinstance(privilege_levels, list):
            self.privilege_levels = privilege_levels
        elif hasattr(privilege_levels, 'value'):  # Check if it's an enum member with a value
            self.privilege_levels = [privilege_levels]
        else:
            raise TypeError(f"Expected privilege_levels to be PrivilegeLevel.ALL, an enum member, or a list, got {type(privilege_levels)}")

        if tags is None:
            self.tags = [Configuration.Tag.REST]
        elif isinstance(tags, list):
            self.tags = tags + [Configuration.Tag.REST]
        else:
            raise TypeError(f"Expected tags input to be of type list or None, received {type(tags)}")

    def name(self) -> str:
        """Return the function's name."""
        return self._name

    def create_instance(self, privilege_level) -> 'ScenarioWrapper':
        """Create a fresh ScenarioWrapper instance from this template."""
        return ScenarioWrapper(self, privilege_level)

    def __str__(self) -> str:
        return self._name

    def __repr__(self) -> str:
        priv_levels_str = [str(p.value) if hasattr(p, 'value') else str(p) for p in self.privilege_levels]
        return f"ScenarioTemplate(func={self._name}, random={self.random}, priority={self.priority}, privilege_levels={priv_levels_str})"


class ScenarioWrapper:
    """
    Runtime instance of a scenario with fresh labels and execution context.
    Created from a ScenarioTemplate to ensure unique labels each time.
    """
    def __init__(self, template: ScenarioTemplate, privilege_level: PrivilegeLevel):
        self.template = template
        self._name = template._name
        self.random = template.random
        self.priority = template.priority
        self.tags = template.tags
        self.precondition = template.precondition
        self.privilege_level = privilege_level

        # Create a unique label for this scenario instance
        self.label = label.Label(f"{self._name.removesuffix('_scenario')}_scenario")

        self.func = template._func

    def name(self) -> str:
        """Return the function's name."""
        return self._name
    
    def get_label(self) -> str:
        """Return the label associated with this scenario."""
        return self.label

    def __str__(self) -> str:
        return self._name

    def __repr__(self) -> str:
        return f"Scenario(func={self._name}, random={self.random}, priority={self.priority}, privilege_level={self.privilege_level})"

    def check_precondition(self) -> bool:
        # Evaluate the precondition if it exists; if no precondition, return True by default
        if self.precondition:
            return self.precondition()
        return True  # No precondition means it's always valid


class ScenarioManager:
    """
    Manager to handle the storage, selection, and filtering of scenario templates.
    Creates fresh ScenarioWrapper instances on demand.
    """
    def __init__(self):
        logger = get_logger()
        logger.info("======================== ScenarioManager")
        self._scenario_templates = []
        # Global registry to track scenario instances by privilege level
        self._privilege_level_registry = defaultdict(list)
        # Dictionary to track which scenario instances have been returned by get_scenario_for_xret() for each privilege level
        self._xret_returned_scenarios = defaultdict(set)

    def list_scenarios(self):
        """Return a list of all scenario templates for debugging or reporting purposes."""
        return self._scenario_templates

    def add_scenario(self, template: ScenarioTemplate):
        """
        Add a new scenario template to the pool.

        Args:
            template (ScenarioTemplate): The scenario template to add.

        Raises:
            ValueError: If a scenario template with the same name already exists in the pool.
        """
        # Check if a scenario template with the same name already exists
        if any(existing_template.name() == template.name() for existing_template in self._scenario_templates):
            raise ValueError(f"A scenario with the name '{template.name()}' already exists in the pool.")

        # Add the template to the pool
        logger = get_logger()
        logger.debug(f"Add new scenario template {template.name()}")
        self._scenario_templates.append(template)

    def register_scenario_for_privilege_level(self, privilege_level: int, scenario_instance: ScenarioWrapper):
        """
        Register a scenario instance in the global registry for a specific privilege level.
        This allows higher-level scenarios to find lower-level scenarios for mret/sret operations.

        Args:
            privilege_level (int): The privilege level (e.g., 0=User, 1=Supervisor, 3=Machine for RISC-V)
            scenario_instance (ScenarioWrapper): The scenario instance to register.
        """
        self._privilege_level_registry[privilege_level].append(scenario_instance)

    def get_scenario_for_xret(self, current_privilege_level: PrivilegeLevel) -> ScenarioWrapper:
        """
        Get a random scenario for xret instruction (mret/sret) from equal or lower privilege levels.
        
        Args:
            current_privilege_level (PrivilegeLevel): The current privilege level
            
        Returns:
            ScenarioWrapper: A fresh scenario instance that can be used as xret target
            
        Raises:
            ValueError: If no suitable scenarios are found for the privilege level
        """
        logger = get_logger()
        logger.debug(f"Looking for xret scenario from privilege level {current_privilege_level}")
        
        # Get the numeric value of the current privilege level
        current_level_value = current_privilege_level.value
        
        # Collect all eligible scenario instances from equal or lower privilege levels
        eligible_instances = []
        
        # Check all registered privilege levels that are equal or lower
        for priv_level, instances in self._privilege_level_registry.items():
            if priv_level <= current_level_value:
                eligible_instances.extend(instances)
        
        if not eligible_instances:
            raise ValueError(f"No scenarios available for xret from privilege level {current_privilege_level}")
        
        # Select a random instance from eligible ones
        selected_instance = choice(eligible_instances)
        
        # Track that this scenario instance has been returned for xret at this privilege level
        self._xret_returned_scenarios[current_level_value].add(selected_instance)
        
        # Return the selected instance
        return selected_instance

    def get_unvisited_scenarios_for_privilege_level(self, privilege_level: int) -> set:
        """
        Get the set of scenario instances from registered instances that haven't been returned by get_scenario_for_xret() 
        for the given privilege level.
        
        Args:
            privilege_level (int): The privilege level to check for unvisited scenarios
            
        Returns:
            set: A set of ScenarioWrapper instances that haven't been returned by get_scenario_for_xret()
                 for the given privilege level
        """
        logger = get_logger()
        logger.debug(f"Getting unvisited scenario instances for privilege level {privilege_level}")
        
        # Get registered instances for this privilege level
        registered_instances = set(self._privilege_level_registry[privilege_level])
        
        # Get scenario instances that have already been returned for xret at this privilege level
        returned_instances = self._xret_returned_scenarios[privilege_level]
        
        # Calculate unvisited instances (simple set difference)
        unvisited_instances = registered_instances - returned_instances
        
        logger.debug(f"Found {len(unvisited_instances)} unvisited scenario instances out of {len(registered_instances)} registered for privilege level {privilege_level}")

        # sorted list for determinism
        return sorted(unvisited_instances, key=ScenarioWrapper.get_label)

    # Functions to query scenarios
    def get_scenario_by_name(self, name: str) -> ScenarioWrapper:
        """
        Retrieve a fresh scenario instance by its function name.

        Args:
            name (str): The name of the scenario function.

        Returns:
            ScenarioWrapper: A fresh ScenarioWrapper instance or raises ValueError if not found.
        """
        for template in self._scenario_templates:
            if template.name() == name:
                return template.create_instance()

        raise ValueError(f"Scenario '{name}' not found.")


    def get_random_scenario(self, tags: Optional[Union[Dict, List]] = None, current_privilege_level: Optional[int] = None, _precondition_retries: int = 10) -> ScenarioWrapper:
        """
            Returns a fresh random scenario instance that matches the tag distribution, is random=True, satisfies the precondition, and
            takes into account priority levels (higher priority scenarios have higher selection weight).
            If no tags are provided, treat it as 100% REST tag.
            Automatically registers the selected scenario template for the current privilege level if provided.

            Args:
                tags (Optional[Dict[Tool.Tag, int]]): A dictionary of tags and their weights.
                current_privilege_level (Optional[int]): The current privilege level to filter scenarios by.
                                                       If None, no privilege level filtering is applied.
                _precondition_retries (int): The number of times to try finding a valid scenario before raising an error.

            Returns:
                ScenarioWrapper: A fresh scenario instance that fits the requirements.

            Raises:
                ValueError: If no valid scenario is found after 'retries' attempts.
        """

        # Filter templates that have random=True
        random_templates = [t for t in self._scenario_templates if t.random]

        if not random_templates:
            raise ValueError("No random scenarios available.")

        # Filter by privilege level if specified
        if current_privilege_level is not None:
            eligible_templates = []
            for template in random_templates:
                # Check if scenario can run at current privilege level
                for priv_level in template.privilege_levels:
                    if priv_level <= current_privilege_level:
                        eligible_templates.append(template)
                        break
            random_templates = eligible_templates
            
            if not random_templates:
                raise ValueError(f"No random scenarios available for privilege level {current_privilege_level}.")

        if tags is None:
            # If no tags provided, default to 100% REST
            tags = {Configuration.Tag.REST: 100}
        elif isinstance(tags, list):
            # If tags is a list, convert to dict with uniform weights
            uniform_weight = 100 / len(tags) if tags else 0  # Avoid division by zero
            tags = {tag: uniform_weight for tag in tags}
        elif isinstance(tags, dict):
            # dict is of the correct instance, do nothing
            pass
        else:
            # tags is at an invalid type
            raise TypeError(f"Expected 'tags' to be a dictionary or List, but got {type(tags).__name__}")

        '''
        Calculate Combined Weights: 
        For each template, calculate a weight based on both its priority and the requested tag distribution. 
        This combined weight can be the product of the template's priority and the distribution weight for each tag it has.
        Construct a Weighted List: 
        Create a list where each template appears with its combined weight. 
        This list will include all templates with weights that reflect both the priority and the tag distribution.
        Weighted Sampling: 
        Use a single weighted random selection based on these combined weights to choose the required number of templates.
        '''

        # Step 1: Calculate combined weights for each template
        weighted_templates_dict = {}
        total_weight = 0
        for template in random_templates:
            # calculate based on tags sum
            tag_weights = sum(tags.get(tag, 0) for tag in template.tags)
            combined_weight = Configuration.PRIORITY_WEIGHTS[template.priority] * tag_weights

            # Only add to the list if combined_weight > 0
            if combined_weight > 0:
                total_weight += combined_weight
                weighted_templates_dict[template] = combined_weight

        # Step 2: handle "direct" scenarios, calculate their weight and add to dict
        for template in random_templates:
            if str(template) in tags.keys():
                # calculate relative weight
                direct_scenario_portion = tags[str(template)] / sum(tags.values())
                all_other_portion = 1 - direct_scenario_portion
                
                # Handle case where all_other_portion is 0 (100% direct scenarios)
                if all_other_portion == 0:
                    # When there are only direct scenarios, assign weight based on priority and direct portion
                    weighted_templates_dict[template] = Configuration.PRIORITY_WEIGHTS[template.priority] * direct_scenario_portion
                else:
                    overall_weight = total_weight / all_other_portion
                    weighted_templates_dict[template] = overall_weight * direct_scenario_portion

        # Step 3: use `Tool.choices` to randomize from weighted_templates_dict

        # Create a mapping of scenarios by tag, and ensure scenarios without tags are part of REST
        if not weighted_templates_dict:
            raise RuntimeError("No valid tags found with associated scenarios.")

        for _ in range(_precondition_retries):
            candidate_template = choice(values=weighted_templates_dict)
            
            # Create a fresh instance from the template
            candidate_instance = candidate_template.create_instance(privilege_level=current_privilege_level)

            # Check precondition on the fresh instance, if it exists and is callable
            if hasattr(candidate_instance, 'precondition') and callable(candidate_instance.precondition):
                if candidate_instance.precondition():  # Call precondition if it exists
                    return candidate_instance # Return the fresh ScenarioWrapper instance
            else:
                # If there is no precondition, treat it as valid
                return candidate_instance

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


