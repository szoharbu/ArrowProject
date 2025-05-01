import random

from ....Internal_content.ingredients.feature_a import ing_A
from ....Utils.configuration_management import Configuration
from ....Arrow_API import AR
from ....Arrow_API.resources.memory_manager import MemoryManager_API as MemoryManager
from ....Tool.ingredient_management import get_ingredient_manager


@AR.scenario_decorator(random=True, priority=Configuration.Priority.MEDIUM, tags=[Configuration.Tag.FEATURE_A, Configuration.Tag.RECIPE])
def code_switching_scenario():
    '''
    Scenario that will allocate 2 small code blocks, and inside a loop alternate between them.
    inside each code block do several ingredients
    '''
    ingredient_manager = get_ingredient_manager()
    ings_A = ingredient_manager.get_random_ingredients(count=random.randint(2, 3), tags=[Configuration.Tag.FAST, Configuration.Tag.REST])
    ings_B = ingredient_manager.get_random_ingredients(count=random.randint(2, 3), tags={Configuration.Tag.FEATURE_B:80, Configuration.Tag.REST:20})

    joint_ing = ings_B + ings_A
    AR.comment(f"Selected Ingredients: {joint_ing}")

    ingredient_manager.call_ingredients_init(joint_ing)

    code_A = MemoryManager.MemorySegment(f"code_switch_A", byte_size=0x500, memory_type=Configuration.Memory_types.CODE)
    code_B = MemoryManager.MemorySegment(f"code_switch_B", byte_size=0x500, memory_type=Configuration.Memory_types.CODE)

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



@AR.scenario_decorator(random=True, priority=Configuration.Priority.HIGH)
def nested_code_sequence():
    """
    A scenario that generate a nested branching sequence,
    and at each level decide if it wants to recursively enter deeper
    """
    iterations = random.randint(5,20)
    max_depth = random.randint(4,6)

    generate_nested_branch(depth=0, max_depth=max_depth, current_iteration=0, max_iteration=iterations)


def generate_nested_branch(depth, max_depth, current_iteration, max_iteration):
    if current_iteration >= max_iteration:
        AR.comment("Max iteration reached. only generate instructions or exit")

    code = MemoryManager.MemorySegment(
        f"nested_code_sequence_{current_iteration}", byte_size=0x100, memory_type=Configuration.Memory_types.CODE
    )

    AR.comment(f'branching to code {code}')
    with AR.BranchToSegment(code_block=code):
        AR.comment(f'inside code {code}')

        while True: # keep selecting action until explicitly return

            #print(f"zzzzzzzzzzz depth {depth}, iteration {current_iteration}  (max_depth {max_depth}, max_iteration {max_iteration})")
            '''    
                Set action probabilities based on constraints
                - At early iterations, "go_deeper" is more likely.
                - As iteration nears its end (70% progress), "exit" becomes more likely.
                - At depth 0, "exit" is not allowed.
                - At max depth, "go_deeper" is not allowed.
                - At max iteration, "go_deeper" is disabled.
            '''
            if depth == 0:
                # Can't exit at depth 0
                action_weights = {"generate_random_instruction": 30, "go_deeper": 50}
            elif depth == max_depth or current_iteration >= max_iteration:
                # Can't go deeper if max depth reached or max iterations used
                action_weights = {"generate_random_instruction": 30, "exit": 70}
            elif current_iteration >= 0.7 * max_iteration:
                # After 70% progress, favor exits more
                action_weights = {"generate_random_instruction": 30, "go_deeper": 20, "exit": 50}
            else:
                # Normal case, favoring going deeper
                action_weights = {"generate_random_instruction": 30, "go_deeper": 40, "exit": 30}

            # disable "go_deeper" when at max iterations
            if current_iteration >=max_iteration:
                action_weights = {"generate_random_instruction": 30, "exit": 70}

            action = AR.choice(values=action_weights)
            AR.comment(f"action selected : {action}")

            if action == "generate_random_instruction":
                AR.generate(instruction_count=random.randint(1, 3))
                continue  # stay in the loop and pick another action
            elif action == "go_deeper":
                depth, current_iteration = generate_nested_branch(depth + 1, max_depth, current_iteration + 1, max_iteration)
            else: # exit
                AR.comment(f'exiting code {code}')
                return depth-1, current_iteration+1  # ensure we return at depth 0
