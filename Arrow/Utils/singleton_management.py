
class SingletonManager:
    """
    A lightweight manager for singleton variables.

    This class provides methods to store, retrieve, reset, and remove singleton variables.
    """

    _instances = {}

    @classmethod
    def get(cls, key: str, default=None):
        """
        Get the value of a singleton variable by key.

        Args:
            key (str): The key of the singleton variable.
            default (Any): The value to return if the key does not exist. Defaults to None.

        Returns:
            Any: The value of the singleton variable, or the default value if the key does not exist.
        """
        return cls._instances.get(key, default)

    @classmethod
    def set(cls, key: str, value):
        """
        Set the value of a singleton variable.

        Args:
            key (str): The key of the singleton variable.
            value (Any): The value to set for the singleton variable.

        Raises:
            ValueError: If the key is empty or invalid.
        """
        if not key:
            raise ValueError("Key cannot be empty.")
        cls._instances[key] = value

    @classmethod
    def reset(cls):
        """
        Reset all singleton variables.

        Clears all stored keys and their associated values.
        """
        cls._instances.clear()

    @classmethod
    def reset_key(cls, key: str):
        """
        Reset a specific singleton variable by removing its value.

        Args:
            key (str): The key of the singleton variable to reset.

        Raises:
            KeyError: If the key does not exist.
        """
        if key not in cls._instances:
            raise KeyError(f"Key '{key}' not found in SingletonManager.")
        cls._instances.pop(key)

    @classmethod
    def keys(cls):
        """
        Get a list of all keys currently managed by the SingletonManager.

        Returns:
            list: A list of keys.
        """
        return list(cls._instances.keys())

    @classmethod
    def values(cls):
        """
        Get a list of all values currently stored in the SingletonManager.

        Returns:
            list: A list of values.
        """
        return list(cls._instances.values())

    @classmethod
    def items(cls):
        """
        Get a list of all key-value pairs currently managed by the SingletonManager.

        Returns:
            list: A list of tuples representing key-value pairs.
        """
        return list(cls._instances.items())
