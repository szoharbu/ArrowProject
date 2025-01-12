import logging
import os
from Utils.singleton_management import SingletonManager

class Logger:
    """
    A two-stage logger_management that initially stores logs in memory and later writes them to a file.

    Features:
    - Stage 1: Logs are buffered in memory (up to a specified capacity).
    - Stage 2: Once a log file is provided, buffered logs are written to the file,
               and subsequent logs are directly written to the file.
    """

    def __init__(self, buffer_size: int = 100):
        """
        Initializes the Logger.

        Args:
            buffer_size (int): The maximum number of log entries that can be stored in memory.
        """
        self.buffer = []  # List to temporarily store log messages
        self.buffer_size = buffer_size  # Capacity of the memory buffer
        self.logger = logging.getLogger("Logger")  # Create a logger_management instance
        self.logger.setLevel(logging.DEBUG)  # Set the default log level to DEBUG
        self.file_handler = None  # Placeholder for the file handler (to be set later)

        # Set up a memory-only handler for Stage 1
        stream_handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        stream_handler.setFormatter(formatter)
        stream_handler.emit = self._emit_to_memory  # Override 'emit' to store logs in memory
        self.logger.addHandler(stream_handler)

    def _print_to_console(self, record: logging.LogRecord):
        """
        Prints log messages selectively to the console based on log levels.

        Args:
            record (LogRecord): The log record to print.
        """
        if record.levelno >= logging.INFO:  # Only INFO, WARNING, ERROR, CRITICAL
            print(f"{record.levelname} - {record.msg}")

    def _emit_to_memory(self, record: logging.LogRecord):
        """
        Custom emit function to store log records in memory.
        Logs will also be printed selectively to the screen.

        Args:
            record (LogRecord): A log record to be stored.

        Raises:
            BufferError: If the buffer exceeds its maximum capacity.
        """
        # Store the raw log record instead of the formatted log message
        if len(self.buffer) >= self.buffer_size:
            raise BufferError("Log buffer capacity exceeded!")
        self.buffer.append(record)  # Store the raw record

    def _emit_to_log_and_screen(self, record: logging.LogRecord):
        """
        Custom emit function to log to both file and console.

        Args:
            record (LogRecord): The log record to handle.
        """
        # First, write the log to the file using the default FileHandler emit method
        if self.file_handler:
            logging.FileHandler.emit(self.file_handler, record)

        # Then print to the console for INFO level or higher
        self._print_to_console(record)

    def setup_file_logging(self, log_file: str):
        """
        Configures the logger_management to write logs to a specified file.

        - Flushes all buffered logs to the file.
        - Replaces the memory handler with a file handler.

        Args:
            log_file (str): Path to the log file.
        """
        # If file logging is already set up, do nothing
        if self.file_handler:
            return

        # Ensure the log file's directory exists
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        # Create a file handler to write logs to the file
        self.file_handler = logging.FileHandler(log_file, mode='w')
        self.file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.file_handler.setFormatter(formatter)

        # Replace the memory handler with the custom file handler that logs to both file and console
        self.logger.handlers = [self.file_handler]

        # Attach the custom emit method to log to both file and console
        self.file_handler.emit = self._emit_to_log_and_screen # Override 'emit' to store logs into both file and screen

        # Flush all buffered memory logs to the file and print selectively to the screen
        for record in self.buffer:
            self.file_handler.emit(record)  # Write to file with the correct format
            #self._print_to_console(record)  # Print selectively to the console

        self.buffer = []  # Clear the memory buffer


    def get_logger(self) -> logging.Logger:
        """
        Retrieves the logger_management instance for use in the application.

        Returns:
            logging.Logger: The logger_management instance.
        """
        return self.logger

    @staticmethod
    def clean_logger():
        """
        remove all handlers associated with the logger.
        """
        logger = logging.getLogger("Logger")
        handlers = logger.handlers[:]
        for handler in handlers:
            handler.close()
            logger.removeHandler(handler)


# Factory function to retrieve or create the logger instance
def get_logger(get_manager: bool = False):
    """
    Factory function to retrieve the logger instance.

    Args:
        get_manager (bool): If True, returns the Logger manager instance.

    Returns:
        logging.Logger or Logger: The logger instance or the Logger manager instance.
    """
    logger_instance = SingletonManager.get("logger_instance", default=None)
    if logger_instance is None:
        log_manager_instance = Logger(buffer_size=100)
        logger_instance = log_manager_instance.get_logger()
        SingletonManager.set("log_manager_instance", log_manager_instance)
        SingletonManager.set("logger_instance", logger_instance)

    if get_manager:
        return SingletonManager.get("log_manager_instance", default=None)
    else:
        return logger_instance