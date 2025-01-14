from Utils.logger_management import get_logger
from Utils.singleton_management import SingletonManager
from typing import Any

class ConfigManager:
    """
    A singleton-based configuration manager for storing immutable configuration values.

    Features:
    - Configuration keys can only be set once.
    - Configuration values are immutable once set.
    - Provides methods to retrieve and check for the existence of configuration keys.
    """

    def __init__(self):
        self._config = {} # Private dictionary to store configuration values
        self._logger = get_logger()
        self._logger.info("======================== ConfigManager")

    def set_value(self, key: str, value: Any) -> None:
        """
        Sets a configuration value. Raises an error if the key already exists,
        ensuring the configuration is read-only once set.
        """
        if key in self._config:
            self._logger.error(f"Attempt to modify existing key '{key}'.")
            raise ValueError(f"Configuration key '{key}' already exists and cannot be modified.")
        self._config[key] = value
        self._logger.debug(f"Configuration set: {key} = {value}")

    def get_value(self, key: str) -> Any:
        """
        Retrieves a configuration value. Raises an error if the key doesn't exist.
        """
        if key not in self._config:
            self._logger.error(f"Configuration key '{key}' not found.")
            raise KeyError(f"Configuration key '{key}' not found.")
        self._logger.debug(f"Retrieved configuration: {key} = {self._config[key]}")
        return self._config[key]

    def is_exist(self, key: str)->bool:
        """
        check a configuration value. return bool
        """
        if key not in self._config:
            return False
        else:
            return True

    def reset(self) -> None:
        """
        Resets all configuration values. Use with caution as this clears all settings.
        """
        self._logger.warning("All configuration values are being reset.")
        self._config.clear()

    def __repr__(self):
        """
        String representation of the ConfigurationManager for debugging purposes.
        """
        return f"{self.__class__.__name__}({self._config})"

# Factory function to retrieve the ConfigManager instance
def get_config_manager() -> ConfigManager:
    # Access or initialize the singleton variable
    config_manager_instance = SingletonManager.get("config_manager_instance", default=None)
    if config_manager_instance is None:
        config_manager_instance = ConfigManager()
        SingletonManager.set("config_manager_instance", config_manager_instance)
    return config_manager_instance
