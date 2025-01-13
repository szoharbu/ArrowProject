
from Utils.logger_management import get_logger

class Sources:
    logger = get_logger()
    logger.info("======================== SOURCES_API")

    # Register imports
    from Tool.register_management.register_manager_wrapper import RegisterManagerWrapper as RegisterManager