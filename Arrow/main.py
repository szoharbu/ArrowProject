import os
import time
import traceback
from Utils.logger_management import get_logger

def main(args=None):
    start_time = time.time()

    logger = get_logger()
    log_manager = get_logger(get_manager=True)

    base_dir = os.path.dirname(os.path.abspath(__file__))
    log_file = os.path.join(base_dir,'output','test.log')
    log_manager.setup_file_logging(log_file)

    logger.info("==== Arrow main")

    try:
        #read_inputs()          # Read inputs, read template, read configuration, ARM/riscv, ...
        #evaluate_section() # review all configs and knobs, set them according to some logic and seal them ... register here also set the asm_logger
        #init_section()           # initialize the state, register, memory and other managers.
        #test_section()           # boot, body (foreach core, foreach scenario), test final

        logger.info("Test generated successful :)")
        dump_time(start_time, "Test generation")

        #final_section()         # post flows?

    except Exception as e:
        logger.warning("Test failed :(")
        dump_time(start_time, "Test total")
        logger.error(f"Error: {e}")
        logger.error(traceback.format_exc())
    else:
        # Test was successful
        dump_time(start_time, "Test total")
        logger.info("Test was successful :)\n")
        logger.info("Mission accomplished...")

    return True


def dump_time(start_time, message_header):
    logger = get_logger()
    current_time = time.time()  # Capture current time
    duration = current_time - start_time # Calculate duration
    logger.info(f'{message_header} took {duration:.2f} seconds')


if __name__ == "__main__":
    main()
