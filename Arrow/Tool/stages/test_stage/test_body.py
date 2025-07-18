from typing import Optional
from Arrow.Utils.logger_management import get_logger
from Arrow.Utils.configuration_management import Configuration
from Arrow.Tool.state_management import get_state_manager, get_current_state
from Arrow.Tool.state_management.switch_state import SwitchState
from Arrow.Tool.scenario_management import ScenarioWrapper, get_scenario_manager
from Arrow.Tool.asm_libraries.asm_logger import AsmLogger
from Arrow.Utils.APIs import choice
from Arrow.Tool.asm_libraries.branch_to_segment import branch_to_segment
from Arrow.Utils.statistics_managment import get_statistics_manager


def execute_scenario(scenario_instance):
    AsmLogger.comment(f"========================== Start scenario {scenario_instance} ====================")

    # Check if we got a ScenarioWrapper instance
    if not isinstance(scenario_instance, ScenarioWrapper):
        raise ValueError("Error: Expected a ScenarioWrapper instance but got:", type(scenario_instance))

    statistics_manager = get_statistics_manager()
    statistics_manager.increment("scenario_count")

    current_state = get_current_state()
    pre_scenario_reserved_registers = current_state.register_manager.get_used_registers()

    scenario_instance.func()  # Call the wrapped function

    post_scenario_reserved_registers = current_state.register_manager.get_used_registers()
        
    if pre_scenario_reserved_registers != post_scenario_reserved_registers:
        # find the difference between the two lists
        pre_set = set(pre_scenario_reserved_registers)
        post_set = set(post_scenario_reserved_registers)
        # Changed to post_set - pre_set to find registers that were added but not freed
        difference = post_set - pre_set
                
        raise ValueError(f"Error: Scenario {scenario_instance} has reserved registers that were not freed: {[str(reg) for reg in difference]}")


    AsmLogger.comment(f"========================== End scenario {scenario_instance} ====================")

def do_scenario(current_scenario: Optional[int], max_scenario:Optional[int]):
    logger = get_logger()
    state_manager = get_state_manager()
    current_state = state_manager.get_active_state()
    current_page_table = current_state.current_el_page_table
    scenario_manager = get_scenario_manager()


    available_blocks = current_page_table.segment_manager.get_segments(pool_type=Configuration.Memory_types.CODE, non_exclusive_only=True)
    # Filter the list to exclude the current code block
    available_blocks_without_current = [block for block in available_blocks if block != current_state.current_code_block]
    # Randomly select from the filtered list
    selected_block = choice.choice(values=available_blocks_without_current)

    selected_scenario = scenario_manager.get_random_scenario(tags=dict(Configuration.Knobs.Template.scenario_query.get_value()))

    info_str = f"BODY:: Running {current_state.state_name}, scenario {current_scenario}(:{max_scenario}), scenario {selected_scenario}"
    logger.info(info_str)
    AsmLogger.comment(info_str)

    two_way_branch = choice.choice(values=[True, False])
    if two_way_branch:
        with branch_to_segment.BranchToSegment(selected_block):
            execute_scenario(selected_scenario)
    else:
        branch_to_segment.BranchToSegment(selected_block).one_way_branch()
        execute_scenario(selected_scenario)


def do_body():
    logger = get_logger()
    state_manager = get_state_manager()
    available_states = state_manager.states_dict
    logger.info("============ do_body")

    per_core_scenario_count = {}
    for state_id in available_states:
        core = state_id
        per_core_scenario_count[core] = (1, int(Configuration.Knobs.Template.scenario_count)) # TODO:: replace this with per state knob state_manager.scenario_count

        with SwitchState(core):
            AsmLogger.comment(f"========================= core {core} - TEST BODY - start =====================")

    state_manager.set_active_state("core_0")
    available_cores = list(available_states.keys())
    while available_cores:
        # go over each of the cores, execute scenarios as long as there is what to execute
        # once a certain core reach out its max scenario count, he will be removed from the list

        # Iterate over a copy of the list to avoid modifying the list during iteration
        for core in available_cores[:]:  # Create a shallow copy of the list
            with SwitchState(core):
                current_scenario, max_scenario = per_core_scenario_count.get(core)
                per_core_scenario_count[core] = (current_scenario + 1, max_scenario)
                if current_scenario == max_scenario:
                    available_cores.remove(core)
                do_scenario(current_scenario, max_scenario)

    available_cores = list(available_states.keys())
    for core in available_cores:
        with SwitchState(core):
            AsmLogger.comment(f"========================= core {core} - TEST BODY - end =====================")
