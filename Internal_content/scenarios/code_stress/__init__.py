import random

from Internal_content.ingredients.feature_a import ing_A
from Utils.configuration_management import Configuration
from Arrow_API import AR
from Arrow_API.resources.memory_manager import MemoryManager_API as MemoryManager
from Tool.ingredient_management import get_ingredient_manager

'''
Scenario that will allocate 2 small code blocks, and inside a loop alternate between them.
inside each code block do several ingredients  
'''
@AR.scenario_decorator(random=True, priority=Configuration.Priority.MEDIUM, tags=[Configuration.Tag.FEATURE_A, Configuration.Tag.RECIPE])
def code_switching_scenario():
    ingredient_manager = get_ingredient_manager()
    ings_A = ingredient_manager.get_random_ingredients(count=random.randint(2, 3), tags=[Configuration.Tag.FAST, Configuration.Tag.REST])
    ings_B = ingredient_manager.get_random_ingredients(count=random.randint(2, 3), tags={Configuration.Tag.FEATURE_B:80, Configuration.Tag.REST:20})

    joint_ing = ings_B + ings_A
    AR.comment(f"Selected Ingredients: {joint_ing}")

    ingredient_manager.call_ingredients_init(joint_ing)

    # TODO:: implement an API to receive a unique identifier. using random value for now
    a, b = random.sample(range(1, 100), 2) # generate two unique numbers
    code_A = MemoryManager.MemorySegment(f"code_block_{a}", byte_size=0x500, memory_type=Configuration.Memory_types.CODE)
    code_B = MemoryManager.MemorySegment(f"code_block_{b}", byte_size=0x500, memory_type=Configuration.Memory_types.CODE)

    AR.comment(f'allocating 2 code blocks, code_A {hex(code_A.address)} and code_B {hex(code_B.address)}')

    with AR.Loop(counter=10):
        AR.comment('branching to code_A ')
        with AR.BranchToSegment(code_block=code_A):
            AR.comment(f'running ingredients {ings_A}')
            ingredient_manager.call_ingredients_body(ings_A)

        AR.comment('branching to code_B ')
        with AR.BranchToSegment(code_block=code_B):
            AR.comment(f'running ingredients {ings_B}')
            ingredient_manager.call_ingredients_body(ings_B)


    ingredient_manager.call_ingredients_final(joint_ing)

