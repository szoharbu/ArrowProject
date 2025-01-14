import inspect
import os
from typing import Optional
from Utils.configuration_management import get_config_manager
from Utils.logger_management import get_logger

def normalize_path(path):
    """Helper function to normalize paths to absolute, lowercase, and consistent separator format."""
    return os.path.normpath(os.path.abspath(path)).lower()

def get_last_user_context():
    # Get config values and normalize paths
    config_manager = get_config_manager()
    content_dir_path = normalize_path(config_manager.get_value('content_dir_path'))
    template_file = normalize_path(config_manager.get_value('template_path'))
    test_stage_path = normalize_path('Tool/stages/test_stage')
    memory_segments_path = normalize_path('Tool/memory_management/memory_segments.py') # initial code label is create there

    # Capture the stack once as the below code might go over it twice, and it has performance penalty
    stack_snapshot = inspect.stack()

    # Traverse the call stack and look for the first instance of user code
    for frame_info in stack_snapshot:
        filename_abs = normalize_path(frame_info.filename)

        # Check for matches in Content directory first
        if content_dir_path in filename_abs:
            # Create a relative path from content_directory
            relative_path = os.path.relpath(filename_abs, content_dir_path)
            return filename_abs, relative_path.replace(os.sep, '/'), frame_info.lineno

        if template_file in filename_abs:
            filename_abs = normalize_path(frame_info.filename)
            shortened_path = "/".join(filename_abs.split(os.sep)[-2:])
            return filename_abs, shortened_path, frame_info.lineno

    # Fallback: check for first instance of Tool code like boot, scenario wrapper and such (e.g., test_stage)
    for frame_info in stack_snapshot:
        filename_abs = normalize_path(frame_info.filename)
        if (test_stage_path in filename_abs) or (memory_segments_path in filename_abs):
            filename_abs = normalize_path(frame_info.filename)
            shortened_path = "/".join(filename_abs.split(os.sep)[-2:])
            return filename_abs, shortened_path, frame_info.lineno

    raise ValueError("Inspect failed to find last_user_context")


class DataUnit:
    def __init__(
            self,
            byte_size: int,
            memory_segment_id:str,
            memory_block_id:str,
            address: Optional[int] = None,
            name:str=None,
            init_value_byte_representation: list[int]=None,
    ):
        """
        Initializes an DataUnit from shared or preserved blocks. later be published into the date_usage file
        """
        self.name = name
        self.address = address
        self.byte_size = byte_size
        self.memory_block_id = memory_block_id
        self.memory_segment_id = memory_segment_id
        self.init_value_byte_representation = init_value_byte_representation

        #extract context to generated data
        self.file_name, self.file_name_shortened_path, self.line_number = get_last_user_context()

        config_manager = get_config_manager()
        execution_platform = config_manager.get_value('Execution_platform')

        if self.init_value_byte_representation is not None:
            formatted_bytes = ", ".join(f"0x{byte:02x}" for byte in self.init_value_byte_representation)
        else:
            formatted_bytes = "None"

        self.data_unit_str = f"[name:{self.name}, memory_block:{self.memory_block_id}, memory_segment:{self.memory_segment_id}, "
        if address is not None:
            self.data_unit_str += f"address:{hex(self.address)}, "
        self.data_unit_str += f"byte_size:{self.byte_size}, init_value:{formatted_bytes}, file: {self.file_name_shortened_path}, line: {self.line_number}]"
        #print(self.data_unit_str)
        #logger = get_logger()
        #logger.debug(f"DataUnit generated: {self.data_unit_str}")

    def __str__(self):
        return self.data_unit_str
