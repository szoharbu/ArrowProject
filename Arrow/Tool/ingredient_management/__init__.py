from ...Utils.singleton_management import SingletonManager
from ...Tool.ingredient_management import ingredient, ingredient_manager

# Factory function to retrieve the IngredientManager instance
def get_ingredient_manager() -> ingredient_manager.IngredientManager:
    # Access or initialize the IngredientManager variable
    ingredient_manager_instance = SingletonManager.get("ingredient_manager_instance", default=None)
    if ingredient_manager_instance is None:
        ingredient_manager_instance = ingredient_manager.IngredientManager()
        SingletonManager.set("ingredient_manager_instance", ingredient_manager_instance)
    return ingredient_manager_instance
