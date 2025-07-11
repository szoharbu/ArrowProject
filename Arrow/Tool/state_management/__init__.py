from Arrow.Utils.singleton_management import SingletonManager

# Factory function to retrieve or create the State_manager instance
def get_state_manager():
    """
    Factory function to retrieve the State_manager instance.
    """
    from Arrow.Tool.state_management.state_manager import State_manager

    state_manager_instance = SingletonManager.get("state_manager_instance", default=None)
    if state_manager_instance is None:
        state_manager_instance = State_manager()
        SingletonManager.set("state_manager_instance", state_manager_instance)
    return state_manager_instance

def get_current_state():
    """
    Utility for a very common usage
    """
    state_manager = get_state_manager()
    return state_manager.get_active_state()
