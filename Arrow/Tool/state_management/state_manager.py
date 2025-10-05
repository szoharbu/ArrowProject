from Arrow.Utils.singleton_management import SingletonManager
from Arrow.Tool.register_management.register_manager import RegisterManager, Register
#from Arrow.Tool.memory_management.segment_manager import SegmentManager, MemorySegment, MemoryRange
from Arrow.Tool.memory_management.memlayout.segment import MemorySegment
#from Arrow.Tool.memory_management.page_manager import MMU
from Arrow.Tool.memory_management.memlayout.page_table import PageTable
from Arrow.Utils.configuration_management import Configuration
from abc import ABC, abstractmethod
from typing import Optional, Union
from Arrow.Tool.memory_management.memlayout.non_paging_segment_manager import NonPagingSegmentManager


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
        
        # Abstract segment_manager interface - to be set by subclasses
        self.segment_manager = None

    @abstractmethod
    def __repr__(self):
        pass

    def get_segment_manager(self):
        return self.segment_manager

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
                 current_code_block: MemorySegment, base_register: Register, base_register_value: int,
                 stack_pointer: Optional[Register] = None):
        super().__init__(state_name, state_id, register_manager, enabled_page_tables, current_code_block)
        self.privilege_level: int = privilege_level
        self.processor_mode: str = processor_mode
        self.base_register: Register = base_register
        self.base_register_value: int = base_register_value
        self.stack_pointer: Optional[Register] = stack_pointer
        
        # Set up segment_manager based on paging status
        self._setup_segment_manager()

    def _setup_segment_manager(self):
        """Set up segment_manager for RISC-V state based on paging configuration."""
        from Arrow.Utils.configuration_management import Configuration
        
        if Configuration.Knobs.Memory.paging_enabled.get_value() and self.enabled_page_tables:
            raise NotImplementedError("RISC-V paging mode is not yet supported.")
        else:
            # Use non-paging segment manager for bare-metal case
            self.segment_manager = NonPagingSegmentManager(name=f"riscv_bare_metal_{self.state_name}")
            
            # Create multiple CODE segments like paging mode does
            # This ensures test_body.py has segments to branch between
            code_segment_count = Configuration.Knobs.Memory.code_segment_count.get_value()
            for i in range(code_segment_count):
                code_segment = self.segment_manager.allocate_memory_segment(
                    name=f"{self.state_name}_code_segment_{i}",
                    byte_size=0x1000,  # 4KB default
                    memory_type=Configuration.Memory_types.CODE,
                    exclusive_segment=False
                )
                # Set the first segment as current_code_block if not already set
                if i == 0 and self.current_code_block is None:
                    self.current_code_block = code_segment
            
            # Create default DATA segments to prevent empty sequence errors
            self.segment_manager.allocate_memory_segment(
                name=f"{self.state_name}_default_data_shared",
                byte_size=0x1000,  # 4KB default
                memory_type=Configuration.Memory_types.DATA_SHARED,
                exclusive_segment=False
            )
            self.segment_manager.allocate_memory_segment(
                name=f"{self.state_name}_default_data_preserve",
                byte_size=0x100000,  # 1MB default
                memory_type=Configuration.Memory_types.DATA_PRESERVE,
                exclusive_segment=False
            )
            # Create STACK segment - needed by test_boot.py
            self.segment_manager.allocate_memory_segment(
                name=f"{self.state_name}_stack_segment",
                byte_size=0x2000,  # 8KB to accommodate test_boot.py's 4KB allocation
                memory_type=Configuration.Memory_types.STACK,
                exclusive_segment=False  # Must be False so allocate_data_memory can find it with non_exclusive_only=True
            )
            
            # Create BOOT_CODE segment - required by test_boot.py (expects exactly one)
            self.segment_manager.allocate_memory_segment(
                name=f"{self.state_name}_boot_code",
                byte_size=0x1000,  # 4KB default
                memory_type=Configuration.Memory_types.BOOT_CODE,
                exclusive_segment=False
            )

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
    
    def get_segment_manager(self):
        return self.current_el_page_table.segment_manager

class State_manager:
    """
    Manages multiple states and tracks the currently active state.
    """

    def __init__(self):
        self.states_dict: dict[str, State] = {}  # Stores states by unique IDs
        self.active_state_id: str | None = None  # ID of the currently active state
        self.default_state_id: str | None = None  # ID of the default state (used for init and fallback)

    def add_state(self, state_id: str, state: State) -> None:
        """
        Add a new state to the state manager.
        :param state_id: Unique identifier for the state (could be a thread ID, name, etc.)
        :param state: Instance of the State class
        """
        if state_id in self.states_dict:
            raise ValueError(f"State with ID {state_id} already exists.")
        self.states_dict[state_id] = state

        # If this is the first state added, make it the default
        if self.default_state_id is None:
            self.default_state_id = state_id
        
        # # Force initialize memory space manager for this state
        # from Arrow.Tool.memory_management.memory_space_manager import get_memory_space_manager
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
            raise ValueError(f"State with ID {state_id} does not exist. valid states are {self.states_dict.keys()}")
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
        self.default_state_id = None

    def is_active_state(self, state_id: str) -> bool:
        """
        Checks if a given state is the currently active state.

        Args:
            state_id (str): Unique identifier of the state to check.

        Returns:
            bool: True if the state is active, False otherwise.
        """
        return self.active_state_id == state_id

    def set_default_state(self, state_id: str) -> None:
        """
        Set the default state ID.
        :param state_id: Unique identifier for the state to set as default
        """
        if state_id not in self.states_dict:
            raise ValueError(f"State with ID {state_id} does not exist. valid states are {self.states_dict.keys()}")
        self.default_state_id = state_id

    def get_default_state_id(self) -> str:
        """
        Get the default state ID.
        :return: The default state ID
        """
        if self.default_state_id is None:
            raise RuntimeError("No default state set.")
        return self.default_state_id

    def get_default_state(self) -> State:
        """
        Get the default state object.
        :return: The default state object
        """
        if self.default_state_id is None:
            raise RuntimeError("No default state set.")
        return self.states_dict[self.default_state_id]

    def set_active_state_to_default(self) -> State:
        """
        Set the active state to the default state.
        :return: The default state object
        """
        if self.default_state_id is None:
            raise RuntimeError("No default state set.")
        return self.set_active_state(self.default_state_id)


