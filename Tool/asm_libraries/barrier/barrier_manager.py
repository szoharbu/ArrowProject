from Utils.singleton_management import SingletonManager
from Tool.state_management import get_current_state
from Tool.memory_management.memory_operand import Memory
from Tool.asm_libraries.asm_logger import AsmLogger


class Barrier:
    def __init__(self, name: str):
        self.name = name
        self._registered_cores = set()  # Set of cores registered to use this barrier
        barrier_memory_name = f"{self.name}_barrier_vector"

        # this is a cross-core memory, so it will be allocated in all cores.
        self.memory = Memory(name=barrier_memory_name, init_value=0xff, byte_size=4, cross_core=True, alignment=3)

    def __str__(self):
        return f"Barrier(name='{self.name}', registered_cores={self._registered_cores})"

    def is_core_registered(self, core_id: str) -> bool:
        """Check if a core is registered to use this barrier."""
        return core_id in self._registered_cores

    def register_core(self, core_id: str):
        """Register a core to use this barrier."""
        self._registered_cores.add(core_id)

    def get_memory(self) -> Memory:
        curr_state = get_current_state()

        """Get the memory object associated with this barrier."""
        return self.memory

    def get_all_registered_cores(self) -> list[str]:
        """Get all registered cores."""
        return list(self._registered_cores)


class BarrierManager:
    def __init__(self):
        self.barriers = {}  # Dictionary mapping barrier names to Barrier objects

    def create_barrier(self, name: str) -> Barrier:
        """Create a new barrier with the specified name."""
        if name in self.barriers.keys():
            raise ValueError(f"Barrier '{name}' already exists")

        current_state = get_current_state()
        core_id = current_state.state_id

        barrier = Barrier(name)
        barrier.register_core(core_id)
        self.barriers[name] = barrier
        return barrier

    def get_barrier(self, name: str) -> Barrier:
        """Get an existing barrier by name and register the current core if needed."""
        if name not in self.barriers.keys():
            raise ValueError(f"Barrier '{name}' does not exist")

        current_state = get_current_state()
        core_id = current_state.state_id

        barrier = self.barriers[name]
        if not barrier.is_core_registered(core_id):
            barrier.register_core(core_id)
        else:
            raise ValueError(f"Core {core_id} already registered to use barrier '{name}'")

        return barrier

    def request_barrier(self, name: str) -> Barrier:
        """Request access to a barrier for the current core. Creates the barrier if it doesn't exist."""
        if name in self.barriers.keys():
            return self.get_barrier(name)
        else:
            return self.create_barrier(name)

    def get_all_barriers(self) -> list[Barrier]:
        """Get all barriers."""
        return list(self.barriers.values())


# Factory function to retrieve the BarrierManager instance
def get_barrier_manager() -> BarrierManager:
    # Access or initialize the singleton variable
    barrier_manager_instance = SingletonManager.get("barrier_manager_instance", default=None)
    if barrier_manager_instance is None:
        barrier_manager_instance = BarrierManager()
        SingletonManager.set("barrier_manager_instance", barrier_manager_instance)
    return barrier_manager_instance
