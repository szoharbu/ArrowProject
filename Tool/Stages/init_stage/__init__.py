from Utils.configuration_management import get_config_manager
from Utils.logger_management import get_logger

def init_section():
    logger = get_logger()
    logger.info("======== init_section")
    config_manager = get_config_manager()

    if not config_manager.is_exist("Architecture"):
        raise ValueError("Error, By this stage you must set the desired architecture (Arm, riscv, x86)")

    #init_state()
    # Add additional needed initialization here
    # Instruction loader
    # ...
