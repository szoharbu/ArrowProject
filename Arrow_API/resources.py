
from Utils.logger_management import get_logger

class Resources:
    logger = get_logger()
    logger.info("======================== SOURCES_API")

    # Register imports
    from Tool.register_management.register_manager_wrapper import RegisterManagerWrapper as RegisterManager

    from Tool.memory_management.memory import Memory
    from Tool.memory_management.memory_block import MemoryBlock

from Tool.state_management import get_state_manager
from Tool.register_management import register_manager

class RegisterManager:

    @staticmethod
    def get_free_registers() -> list[register_manager.Register]:
        """
        Returns a list of all free registers.
        """
        state_manager = get_state_manager()
        current_state = state_manager.get_active_state()
        return current_state.register_manager.get_free_registers()

    @staticmethod
    def get_used_registers() -> list[register_manager.Register]:
        """
        Returns a list of all reserved registers.
        """
        state_manager = get_state_manager()
        current_state = state_manager.get_active_state()
        return current_state.register_manager.get_used_registers()

    @staticmethod
    def get(reg_name:str=None) -> register_manager.Register:
        """
        Selects a random free register, don't mark them as used (reserved = False),
        and returns the selected register. If no available child is found, raise Error
        """
        state_manager = get_state_manager()
        current_state = state_manager.get_active_state()
        return current_state.register_manager.get(reg_name)

    @staticmethod
    def get_and_reserve() -> register_manager.Register:
        """
        Selects a random free register, marks them as used (reserved = True),
        and returns the selected register. If no available child is found, raise Error
        """
        state_manager = get_state_manager()
        current_state = state_manager.get_active_state()
        return current_state.register_manager.get_and_reserve()

    @staticmethod
    def reserve(register: register_manager.Register):
        """
        Sets the specified register reserve attribute to True.

        Parameters:
        - register (Register): The register to make reserve.

        """
        state_manager = get_state_manager()
        current_state = state_manager.get_active_state()
        current_state.register_manager.reserve(register)

    @staticmethod
    def free(register: register_manager.Register):
        """
        Sets the specified register reserve attribute to False.

        Parameters:
        - register (Register): The register to make free again.

        """
        state_manager = get_state_manager()
        current_state = state_manager.get_active_state()
        current_state.register_manager.free(register)

    @staticmethod
    def print_reg_status():
        state_manager = get_state_manager()
        current_state = state_manager.get_active_state()
        current_state.register_manager.print_reg_status()

