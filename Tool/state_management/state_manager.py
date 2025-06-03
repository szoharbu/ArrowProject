from Utils.singleton_management import SingletonManager
from Tool.register_management.register_manager import RegisterManager, Register
from Tool.memory_management.segment_manager import SegmentManager, MemorySegment, MemoryRange
from Tool.memory_management.page_manager import MMU
from Utils.configuration_management import Configuration

class State:
    """
    Represents the state for a logical unit (e.g., a core or VM context).
    Each state contains attributes such as privilege level, processor mode, memory and register managers, and control knobs.
    """

    def __init__(self, state_name: str, state_id: int, privilege_level: int, execution_context: Configuration.Execution_context, processor_mode: str, register_manager: RegisterManager,
                 current_el_mmu: MMU, enabled_mmus: list[MMU], segment_manager: SegmentManager, current_code: MemorySegment, base_register: Register, base_register_value: int, memory_range: MemoryRange):
        self.state_name: str = state_name
        self.state_id: int = state_id
        self.privilege_level: int = privilege_level
        self.processor_mode: str = processor_mode
        self.register_manager: RegisterManager = register_manager
        self.execution_context: Configuration.Execution_context = execution_context         # ARM's exception level
        self.current_el_mmu: MMU = current_el_mmu           # ARM's MMU for the exception level. each state has per-el mmu, and the state_manager will track the current el_mmu
        self.enabled_mmus: list[MMU] = enabled_mmus
        self.segment_manager: SegmentManager = segment_manager
        self.current_code_block:MemorySegment = current_code
        self.base_register: Register = base_register
        self.base_register_value:int = base_register_value
        self.memory_range:MemoryRange = memory_range

    def __repr__(self):
        state_str = f"State(name={self.state_name}, "
        state_str += f"state_id={self.state_id}, "
        if Configuration.Architecture.arm:
            state_str += f"exception_level={self.privilege_level}, "
            state_str += f"execution_context={self.execution_context}, "
            state_str += f"current_el_mmu={self.current_el_mmu}, "
            state_str += f"enabled_mmus={self.enabled_mmus}, "
        else:
            state_str += f"privilege_level={self.privilege_level}, "
            state_str += f"processor_mode={self.processor_mode}, "
            state_str += f"current_code={self.current_code_block}, "
            state_str += f"base_register={self.base_register}, "
            state_str += f"base_register_value={self.base_register_value}, "
        state_str += f"register_manager={self.register_manager}, "
        state_str += f"segment_manager={self.segment_manager}, "
        state_str += f"memory_range={self.memory_range}"

        return state_str



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

    # def remove_state(self, state_id: str, state: State):

    def set_active_state(self, state_id: str) -> None:
        """
        Set a state as the active state.
        :param state_id: Unique identifier for the state to set as active
        """
        if state_id not in self.states_dict:
            raise ValueError(f"State with ID {state_id} does not exist.")
        self.active_state_id = state_id

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


