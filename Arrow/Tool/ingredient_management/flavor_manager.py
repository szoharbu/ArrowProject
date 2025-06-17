import random
from typing import List, Optional, Union
import Arrow.Tool
"""

Flavor Management System Overview:

This module provides a flexible system for creating, registering, and selecting flavors.

Flavors represent different configurations and are constructed either directly with predefined attributes or via templates that apply dynamic logic.

Key Components:

1. **Flavor**:

- Represents a specific flavor with the following attributes: `name`, `description`, `weight`, and `tags`.

- Flavors can be registered directly with fixed attributes for simple use cases.

- A Flavor is predefined but doesn't have ingredients directly. Instead, it contains a tags parameter.

When a Flavor is selected, the system will use the tags and a get_ingredient(tags) function to fetch the ingredients dynamically.

2. **FlavorTemplate**:

- Abstract class that defines the logic for creating flavors with dynamic or complex behavior.

- Subclasses of `FlavorTemplate` implement custom logic in the `create_flavor()` method to generate flavors at runtime.

- This allows for dynamic customization of ingredients, weight, and other attributes upon selection, based on its logic.

3. **FlavorManager**:

- Singleton class responsible for managing the registration and selection of both direct `Flavor` instances and `FlavorTemplate` objects.

- Flavors or templates can be registered, and the `FlavorManager` will randomly select a flavor when needed. If a template is selected, its `create_flavor()` method is invoked to generate the flavor.

Usage:

- **Simple Flavors**: Directly create and register flavors with predefined attributes.

- **Flavor Templates**: Create more complex flavors dynamically by defining custom templates that encapsulate specific logic.

- The system allows seamless integration of both static and dynamic flavors, making it flexible for various scenarios.

Example:

- Register simple fixed flavors or flavor templates that generate flavors with customized behavior.

- Select a flavor, and the system will return either a pre-registered flavor or a dynamically generated one based on the logic in the flavor template.

class SimpleFlavorTemplate(FlavorTemplate):

def create_flavor(self) -> Flavor:

weight = random.randint(3, 10)

ingredients = {'A': 50, 'B': 50} if weight < 5 else {'C': 70, 'D': 30}

return Flavor(name=self.name, description=self.description, weight=weight, ingredients=ingredients)

# Registering templates and simple flavors

flavor_manager.register_flavor(

SimpleFlavorTemplate(name="Simple Flavor", description="A simple flavor with basic ingredients"))

# Directly registering simple flavors

simple_flavor = Flavor(name="Simple Fixed Flavor", description="A simple flavor with fixed ingredients",

weight=5, ingredients={'A': 40, 'B': 60})

flavor_manager.register_flavor(simple_flavor)

selected_flavor = flavor_manager.select_flavor()

print("Selected flavor:", selected_flavor)

# Listing all registered flavors or templates

print("Registered items:", flavor_manager.get_registered_items())

"""


# Singleton factory for managing and selecting flavor templates or direct flavors

class FlavorManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FlavorManager, cls).__new__(cls)
            cls._instance.flavor_templates_or_flavors = []
        return cls._instance

    def register_flavor(self, flavor_or_template: Union['Flavor', 'FlavorTemplate']):
        """Registers either a simple Flavor object or a FlavorTemplate."""
        self.flavor_templates_or_flavors.append(flavor_or_template)

    def select_flavor(self) -> Optional['Flavor']:
        """Selects a flavor from registered templates or simple flavors."""
        if not self.flavor_templates_or_flavors:
            return None
        selected = random.choice(self.flavor_templates_or_flavors)
        # If it's a FlavorTemplate, create a flavor using its logic
        if isinstance(selected, FlavorTemplate):
            return selected.create_flavor()

        # If it's a Flavor, resolve ingredients dynamically based on its tags
        if isinstance(selected, Flavor):
            selected_ingredients = Arrow.Tool.ingredient_manager.get_random_ingredients(count=selected.count, tags=selected.tags)
            return Flavor(name=selected.name, description=selected.description,
                          weight=selected.weight, ingredients=selected_ingredients)

    def get_registered_items(self) -> List[Union['FlavorTemplate', 'Flavor']]:
        """Returns the list of registered FlavorTemplate or Flavor objects."""
        return self.flavor_templates_or_flavors

# Global manager instance
flavor_manager = FlavorManager()

class Flavor:

    def __init__(self, name: str, description: Optional[str] = None,
                 weight: Optional[int] = None, count: Optional[int] = None,
                 tags: Optional = None, ingredients: Optional = None):
        self.name = name
        self.description = description if description is not None else "No description"
        self.weight = weight if weight is not None else random.randint(5, 10)
        self.count = count if count is not None else random.randint(5, 10)
        self.tags = tags
        self.ingredients = ingredients

        if tags is not None and ingredients is not None:
            raise ValueError("Flavor cannot have both 'tags' and 'ingredients'.")

        if tags is None and ingredients is None:
            raise ValueError("Flavor must have either 'tags' or 'ingredients'.")

        if ingredients is not None and count is not None:
            raise ValueError("Flavor cannot have both 'ingredients' and 'count'.")


    def __repr__(self) -> str:
        return (f"Flavor(name={self.name}, description='{self.description}', "
                f"weight={self.weight}, ingredients={self.ingredients})")

class FlavorTemplate:
    # def __init__(self, name: str, description: str):
    # self.name = name
    # self.description = description

    def create_flavor(self) -> Flavor:
        """Abstract method to create a flavor. Subclasses must implement this."""
        raise NotImplementedError("Subclasses must implement this method.")