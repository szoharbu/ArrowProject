from Utils.singleton_management import SingletonManager
from Tool.register_management.register_manager import RegisterManager, Register
#from Tool.memory_management.segment_manager import SegmentManager, MemorySegment, MemoryRange
from Tool.memory_management.memlayout.segment import MemorySegment
#from Tool.memory_management.page_manager import MMU
from Tool.memory_management.memlayout.page_table import PageTable
from Utils.configuration_management import Configuration
from abc import ABC, abstractmethod
from typing import Optional, Union


class State(ABC):
    """
    Abstract base class for processor state.
    Each state contains common attributes and architecture-specific attributes.
    """

    def __init__(self, state_name: str, 
                state_id: int,
                register_manager: RegisterManager,
                enabled_page_tables: list[PageTable],
                current_code_block: MemorySegment):
        self.state_name: str = state_name
        self.state_id: int = state_id
        self.register_manager: RegisterManager = register_manager
        self.enabled_page_tables: list[PageTable] = enabled_page_tables
        self.current_code_block: MemorySegment = current_code_block

    @abstractmethod
    def __repr__(self):
        pass

    @staticmethod
    def create_state(state_name: str, state_id: int, register_manager: RegisterManager, **kwargs) -> 'State':
        """
        Factory method to create the appropriate State subclass based on configuration.
        """
        if Configuration.Architecture.arm:
            return ARMState(state_name, state_id, register_manager, **kwargs)
        elif Configuration.Architecture.riscv:
            return RISCVState(state_name, state_id, register_manager, **kwargs)
        elif Configuration.Architecture.x86:
            return X86State(state_name, state_id, register_manager, **kwargs)
        else:
            raise ValueError(f"Unsupported architecture: {Configuration.Architecture}")


class X86State(State):
    """
    State class for x86 architecture.
    """

    def __init__(self, state_name: str, state_id: int, register_manager: RegisterManager,
                 privilege_level: int, processor_mode: str, enabled_page_tables: list[PageTable],
                 current_code_block: MemorySegment, base_register: Register, base_register_value: int):
        super().__init__(state_name, state_id, register_manager, enabled_page_tables, current_code_block)
        self.privilege_level: int = privilege_level
        self.processor_mode: str = processor_mode
        self.base_register: Register = base_register
        self.base_register_value: int = base_register_value

    def __repr__(self):
        return (f"X86 State(name={self.state_name}, "
                f"state_id={self.state_id}, "
                f"privilege_level={self.privilege_level}, "
                f"processor_mode={self.processor_mode}, "
                f"enabled_page_tables={self.enabled_page_tables}, "
                f"current_code_block={self.current_code_block}, "
                f"base_register={self.base_register}, "
                f"base_register_value={self.base_register_value}, "
                f"register_manager={self.register_manager})")

class RISCVState(State):
    """
    State class for RISCV architecture.
    """

    def __init__(self, state_name: str, state_id: int, register_manager: RegisterManager,
                 privilege_level: int, processor_mode: str, enabled_page_tables: list[PageTable],
                 current_code_block: MemorySegment, base_register: Register, base_register_value: int):
        super().__init__(state_name, state_id, register_manager, enabled_page_tables, current_code_block)
        self.privilege_level: int = privilege_level
        self.processor_mode: str = processor_mode
        self.base_register: Register = base_register
        self.base_register_value: int = base_register_value

    def __repr__(self):
        return (f"RISCV State(name={self.state_name}, "
                f"state_id={self.state_id}, "
                f"privilege_level={self.privilege_level}, "
                f"processor_mode={self.processor_mode}, "
                f"enabled_page_tables={self.enabled_page_tables}, "
                f"current_code_block={self.current_code_block}, "
                f"base_register={self.base_register}, "
                f"base_register_value={self.base_register_value}, "
                f"register_manager={self.register_manager})")
    
class ARMState(State):
    """
    State class for ARM architecture.
    """

    def __init__(self, state_name: str, state_id: int, register_manager: RegisterManager,
                 exception_level: int, execution_context: Configuration.Execution_context,
                 current_el_page_table: PageTable, enabled_page_tables: list[PageTable],
                 current_code_block: MemorySegment):
        super().__init__(state_name, state_id, register_manager, enabled_page_tables, current_code_block)
        self.current_el_level: int = exception_level
        self.execution_context: Configuration.Execution_context = execution_context
        self.current_el_page_table: PageTable = current_el_page_table

        # Per EL code block, for cases we are switching code and later want to get back to the same code block
        self.per_el_code_block: dict[int, MemorySegment] = {}
        self.per_el_code_block[self.current_el_level] = current_code_block

    def __repr__(self):
        return (f"ARM State(name={self.state_name}, "
                f"state_id={self.state_id}, "
                f"exception_level={self.current_el_level}, "
                f"execution_context={self.execution_context}, "
                f"current_el_page_table={self.current_el_page_table}, "
                f"current_code_block={self.current_code_block}, "
                #f"enabled_page_tables={self.enabled_page_tables}, "
                f"register_manager={self.register_manager})")


class State_manager:
    """
    Manages multiple states and tracks the currently active state.
    """

    def __init__(self):
        self.states_dict: dict[str, State] = {}  # Stores states by unique IDs
        self.active_state_id: str | None = None  # ID of the currently active state

    def add_state(self, state_id: str, state: State) -> None:
        """
        Add a new state to the state manager.
        :param state_id: Unique identifier for the state (could be a thread ID, name, etc.)
        :param state: Instance of the State class
        """
        if state_id in self.states_dict:
            raise ValueError(f"State with ID {state_id} already exists.")
        self.states_dict[state_id] = state
        
        # # Force initialize memory space manager for this state
        # from Tool.memory_management.memory_space_manager import get_memory_space_manager
        # memory_space_manager = get_memory_space_manager()
        # memory_space_manager.force_initialize_state(state_id)

    def create_and_add_state(self, state_id: str, state_name: str, register_manager: RegisterManager, **kwargs) -> State:
        """
        Create and add a new state using the factory method.
        :param state_id: Unique identifier for the state
        :param state_name: Name of the state
        :param register_manager: Register manager for the state
        :param kwargs: Architecture-specific parameters
        :return: The created state
        """
        state = State.create_state(state_name, len(self.states_dict), register_manager, **kwargs)
        self.add_state(state_id, state)
        return state

    # def remove_state(self, state_id: str, state: State):

    def set_active_state(self, state_id: str) -> State:
        """
        Set a state as the active state.
        :param state_id: Unique identifier for the state to set as active
        """
        if state_id not in self.states_dict:
            raise ValueError(f"State with ID {state_id} does not exist.")
        self.active_state_id = state_id
        return self.states_dict[state_id]

    def get_active_state(self) -> State:
        """
        Get the current active state.
        :return: The active state object
        """
        if self.active_state_id is None:
            raise RuntimeError("No active state set.")
        return self.states_dict[self.active_state_id]

    def get_all_states(self) -> list[str]:
        """
        Lists all state IDs managed by the StateManager.
        Returns:
            list[str]: A list of state IDs.
        """
        return list(self.states_dict.keys())

    def clear_states(self) -> None:
        """
        Clears all states from the manager.
        """
        self.states_dict.clear()
        self.active_state_id = None

    def is_active_state(self, state_id: str) -> bool:
        """
        Checks if a given state is the currently active state.

        Args:
            state_id (str): Unique identifier of the state to check.

        Returns:
            bool: True if the state is active, False otherwise.
        """
        return self.active_state_id == state_id


