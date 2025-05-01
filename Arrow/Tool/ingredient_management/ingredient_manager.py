
import random
from typing import Optional, Dict, List, Union
from ...Utils.logger_management import get_logger
from ...Utils.configuration_management import Configuration
from ...Tool.state_management import get_state_manager
from ...Tool.state_management.switch_state import switch_code
from ...Tool.asm_libraries.asm_logger import AsmLogger
from ...Utils.APIs.choice import choice



# Helper function to ensure all stages are treated as generators
def to_generator(fn):
    """
    Converts a non-generator function into a generator.
    Returns:
        generator: A generator object ready to be consumed.
    """
    # Handle the case where the function is None.
    # This creates a generator that simply yields once and does nothing.
    if fn is None:
        def wrapper():
            yield  # Ensures it's treated as a generator

        return wrapper()

    # Check if the input is a callable function or already a generator
    if callable(fn):
        def wrapper():
            result = fn()  # Call the function

            # Check if the result of the function call is a generator
            if hasattr(result, '__iter__') and not isinstance(result, str):
                # If it's a generator, yield all its items
                yield from result
            else:
                # If it's not a generator, yield control once
                yield

        return wrapper()

    # If fn is already a generator, return it as is
    return fn


# Ingredient manager to maintain the pool
class IngredientManager:
    def __init__(self):
        self._ingredients_pool = []
        self._ingredients_instances_pool =  {}    # Cache to store instances of ingredients

    def __str__(self):
        return f"zohar: {self._ingredients_pool}"

    def add_ingredient(self, ingredient_class):
        """Register an ingredient into the pool."""

        # Check for duplicate class names
        if any(existing_ingredient.__name__ == ingredient_class.__name__ for existing_ingredient in self._ingredients_pool):
            raise ValueError(
                f"An ingredient class with the name '{ingredient_class.__name__}' already exists in the pool. "
                f"Conflicting classes : {ingredient_class}."
            )

        logger = get_logger()
        logger.debug(f"Add new ingredient {ingredient_class}")
        self._ingredients_pool.append(ingredient_class)

    def get_random_ingredients(self, count:int = 1, tags: Optional[Union[Dict[Configuration.Tag, int],List[Configuration.Tag]]] = None, _precondition_retries: int = 10): #  -> List[Ingredient]:
        """
            Randomly select number of ingredients that matches the tag distribution, is random=True, satisfies the precondition, and
            takes into account priority levels (higher priority ingredients have higher selection weight).
            If no tags are provided, treat it as 100% REST tag.

            Args:
                count (int): number of ingredients to return
                tags (Optional[Dict[Tool.Tag, int]]): A dictionary of tags and their weights.
                _precondition_retries (int): The number of times to try finding a valid ingredient before raising an error.

            Returns:
                List(Ingredient): A list of valid ingredients that fits the requirements.

            Raises:
                ValueError: If no valid ingredients are found after 'retries' attempts.
        """
        logger = get_logger()

        # Filter ingredients that have random=True
        random_ingredients = [s for s in self._ingredients_pool if s.random]
        if not random_ingredients:
            raise ValueError("No random ingredient available.")

        if tags is None:
            # If no tags provided, default to 100% REST
            tags = {Configuration.Tag.REST: 100}
        elif (isinstance(tags, list)):
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
        for ingredient in random_ingredients:
            # calculate based on tags sum
            tag_weights = sum(tags.get(tag, 0) for tag in ingredient.tags)
            combined_weight = Configuration.PRIORITY_WEIGHTS[ingredient.priority] * tag_weights

            # Only add to the list if combined_weight > 0
            if combined_weight > 0:
                # print(f" --- ingredient {ingredient}, priority = {ingredient.priority}, tags = {ingredient.tags}")
                # print(f"               combined_weight {combined_weight} = priority_weight({PRIORITY_WEIGHTS[ingredient.priority]}) * tag_weight({tag_weights})")
                total_weight += combined_weight
                weighted_objects_dict[ingredient] = combined_weight

        # Step 2: handle "direct" ingredients, calculate their weight and add to dict

        for ingredient in random_ingredients:
            if str(ingredient) in tags.keys():
                # calculate relative weight
                direct_ingredient_portion = tags[str(ingredient)] / sum(tags.values())
                all_other_portion = 1 - direct_ingredient_portion
                overall_weight = total_weight / all_other_portion
                weighted_objects_dict[ingredient] = overall_weight * direct_ingredient_portion

        # Step 3: use `Tool.choices` to randomize from weighted_objects_dict

        # Create a mapping of ingredient by tag, and ensure ingredients without tags are part of REST
        if not weighted_objects_dict:
            raise RuntimeError("No valid tags found with associated ingredients.")


        selected_ingredients = []
        attempts = 0
        while len(selected_ingredients) < count and attempts < _precondition_retries:
            attempts += 1

        #for _ in range(_precondition_retries):
            candidate = choice(values=weighted_objects_dict)

            # Check precondition, if it exists and not None (yet allow False)
            if hasattr(candidate, 'precondition') and not candidate.precondition is None:
                if callable(candidate.precondition):
                    if candidate.precondition():  # Call precondition if it exists
                        selected_ingredients.append(candidate) # add the Selected ingredient
                else: # bool precondition
                    if candidate.precondition:  # check if precondition is true
                        selected_ingredients.append(candidate) # add the Selected ingredient
            else:
                # If there is no precondition, treat it as valid
                selected_ingredients.append(candidate)

        if len(selected_ingredients) < count:
            raise RuntimeError(f"Failed to retrieve {count} elements after {_precondition_retries} retries.")

        logger.debug(f"get_random_ingredient:: selected ingredient is {selected_ingredients}")
        return selected_ingredients



    # Call Init Phase
    def call_ingredients_init(self, ingredients):
        logger = get_logger()
        logger.debug(f"call_ingredient_init:: ingredients: {ingredients}")
        state_manager = get_state_manager()

        # calling boot_stages along-side init_stages, although they are going to a different code blocks
        init_stages = []
        # Gather all init and boot stages from all selected ingredients
        for ing in ingredients:
            # Create a new instance and store it in the cache
            self._ingredients_instances_pool[ing] = ing()  # Calls __init__ once

        # executing boot stages
        current_state = state_manager.get_active_state()
        current_code_block = state_manager.get_active_state().current_code_block
        boot_block = current_state.memory_manager.get_segments(pool_type=Configuration.Memory_types.BOOT_CODE)[0]

        have_boot_section = False
        for ing in ingredients:
            if hasattr(self._ingredients_instances_pool[ing], 'boot'):
                have_boot_section = True
                break

        if have_boot_section:
            switch_code(boot_block)
            AsmLogger.comment(f"== Ingredient <TBD_ingredient_name> boot code start")

            for ing in ingredients:
                if hasattr(self._ingredients_instances_pool[ing], 'boot'):
                    AsmLogger.comment(f"== Ingredient boot:: taken from ingredient {ing}")
                    self._ingredients_instances_pool[ing].boot()

            AsmLogger.comment(f"== Ingredient <TBD_ingredient_name> boot code ends")
            switch_code(current_code_block)

        for ing in ingredients:
            init_stage = to_generator(self._ingredients_instances_pool[ing].init)
            init_stages.append((self._ingredients_instances_pool[ing], init_stage)) # added ingredient to the tuple that contain the ingredient and its stage

        first_call = True
        # Interleave execution between yields
        while init_stages:
            random.shuffle(init_stages)  # shuffle order of selected ingredients
            for staged_tuple in init_stages.copy():
                ing = staged_tuple[0]
                stage = staged_tuple[1]

                if first_call:
                    AsmLogger.comment(f"== Ingredient init:: starting with ingredient {ing}")
                    first_call = False
                else:
                    AsmLogger.comment(f"== Ingredient init:: switching to next ingredient {ing}")

                try:
                    next(stage)
                except StopIteration:
                    check_and_remove_comment_from_asmunit_list(ingredient_name=str(ing))

                    init_stages.remove(staged_tuple)

        AsmLogger.comment(f"== Ingredient init:: finished all ingredients")  # Notify that all ingredients are done finished

    # Call Body Phase
    def call_ingredients_body(self, ingredients):
        stages = []
        # Gather body stages from all selected ingredients
        for ing in ingredients:
            # Check if we already have an instance
            if ing not in self._ingredients_instances_pool:
                raise ValueError(f"Error, calling {ing} ingredient.body without ingredient.init ")

            # Now we can call the body method on the cached instance
            body_stage = to_generator(self._ingredients_instances_pool[ing].body)
            stages.append((self._ingredients_instances_pool[ing], body_stage)) # added ingredient to the tuple that contain the ingredient and its stage

        first_call = True
        # Interleave execution between yields
        while stages:
            random.shuffle(stages) # shuffle order of selected ingredients
            for staged_tuple in stages.copy():
                ing = staged_tuple[0]
                stage = staged_tuple[1]

                if first_call:
                    AsmLogger.comment(f"== Ingredient body:: starting with ingredient {ing}")
                    first_call = False
                else:
                    AsmLogger.comment(f"== Ingredient body:: switching to next ingredient {ing}")

                try:
                    next(stage)
                except StopIteration:
                    check_and_remove_comment_from_asmunit_list(ingredient_name=str(ing))
                    stages.remove(staged_tuple)

        AsmLogger.comment(f"== Ingredient body:: finished all ingredients")  # Notify that all ingredients are done finished

    # Call final Phase
    def call_ingredients_final(self, ingredients):
        stages = []
        # Gather final stages from all selected ingredients
        for ing in ingredients:
            # Check if we already have an instance
            if ing not in self._ingredients_instances_pool:
                raise ValueError(f"Error, calling {ing} ingredient.final without ingredient.init ")

            # Now we can call the final method on the cached instance
            final_stage = to_generator(self._ingredients_instances_pool[ing].final)
            stages.append((self._ingredients_instances_pool[ing], final_stage)) # added ingredient to the tuple that contain the ingredient and its stage

        first_call = True
        # Interleave execution between yields
        while stages:
            random.shuffle(stages)  # shuffle order of selected ingredients
            for staged_tuple in stages.copy():
                ing = staged_tuple[0]
                stage = staged_tuple[1]

                if first_call:
                    AsmLogger.comment(f"== Ingredient final:: starting with ingredient {ing}")
                    first_call = False
                else:
                    AsmLogger.comment(f"== Ingredient final:: switching to next ingredient {ing}")

                try:
                    next(stage)
                except StopIteration:
                    check_and_remove_comment_from_asmunit_list(ingredient_name=str(ing))
                    stages.remove(staged_tuple)
        AsmLogger.comment(f"== Ingredient final:: finished all ingredients")  # Notify that all ingredients are done finished

def check_and_remove_comment_from_asmunit_list(ingredient_name:str):
    # For cases the ingredient ends with a 'yield', the flow will go an additional step, and will end of commenting "switching to ing_i" followed by "Finished ing_i"
    # This is not needed, yet we can't tell if the ingredient ended before printing the "switching to ing_i"
    # so, in case we reach the end of ing_i with a redundant "switching to ing_i" comment, we will pop out the last element of the AsmUnit

    state_manager = get_state_manager()
    current_code_block = state_manager.get_active_state().current_code_block

    last_element = current_code_block.asm_units_list[-1]  # get the last element
    pattern = f"switching to next ingredient {ingredient_name}"  # Define the regex pattern
    if pattern in str(last_element):  # Simpler than regex for exact matches
        current_code_block.asm_units_list.pop()
