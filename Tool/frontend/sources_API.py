
from Utils.logger_management import get_logger

class Sources:
    logger = get_logger()
    logger.info("======================== SOURCES_API")

    # Register imports
    from Tool.register_management.register_manager_wrapper import RegisterManagerWrapper as RegisterManager

    from Tool.memory_management.memory import Memory
    from Tool.memory_management.memory_block import MemoryBlock