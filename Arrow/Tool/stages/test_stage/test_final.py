
from Utils.logger_management import get_logger
from Tool.state_management import get_state_manager
from Tool.asm_libraries import end_test, asm_logger

def do_final():
    logger = get_logger()
    state_manager = get_state_manager()
    logger.info("============ do_final")

    asm_logger.AsmLogger.comment(f"in do_final, ending test body")
    end_test.end_test_asm_convention(test_pass=True)

    logger.debug("============ freeing_resources")
    states = state_manager.states_dict
    for state_id in states.keys():
        curr_state = state_manager.get_active_state()
        curr_state.register_manager.free(curr_state.base_register)


