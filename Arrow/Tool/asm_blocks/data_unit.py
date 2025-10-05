import inspect
import os
from typing import Optional
from Arrow.Utils.configuration_management import get_config_manager
from Arrow.Utils.logger_management import get_logger

def get_function_from_frame(frame_info):
    """Extract the function object from a FrameInfo object"""
    # frame_info is a FrameInfo object from inspect.stack()
    # We need to access the actual frame object
    frame = frame_info.frame
    code = frame.f_code
    
    # Try to find the function in locals/globals by name
    name = code.co_name
    
    
    # Check frame locals
    if name in frame.f_locals:
        obj = frame.f_locals[name]
        if callable(obj) and hasattr(obj, '__code__') and obj.__code__ is code:
            return obj
    
    # Check frame globals
    if name in frame.f_globals:
        obj = frame.f_globals[name]
        if callable(obj) and hasattr(obj, '__code__') and obj.__code__ is code:
            return obj
    
    # For methods, check if there's a 'self' or 'cls'
    for var_name in ('self', 'cls'):
        if var_name in frame.f_locals:
            instance_or_class = frame.f_locals[var_name]
            if hasattr(instance_or_class, name):
                method = getattr(instance_or_class, name)
                # For bound methods, get the underlying function
                if hasattr(method, '__func__'):
                    if method.__func__.__code__ is code:
                        return method.__func__
                elif hasattr(method, '__code__') and method.__code__ is code:
                    return method
    
    return None

def get_last_user_context():
    """
    Find the location where AR.generate() or AR.asm() was called to attribute generated code.
    This looks for Arrow API entry points in the call stack rather than user/Arrow boundaries.
    """
    # Lazy imports to avoid circular dependency
    from Arrow.Tool.asm_blocks.asm_unit import AsmUnit
    
    # Capture the stack once for performance
    stack_snapshot = inspect.stack()
    
    # Search for AR API calls in the stack by checking file path and function name
    # This is more reliable than trying to extract function objects from frames
    for i, frame_info in enumerate(stack_snapshot):
        
        # Check if this is an AR API method by its location and name
        # The AR API methods are in Arrow/Arrow_API/flows.py
        if frame_info.filename.endswith("Arrow/Arrow_API/flows.py"):
            if frame_info.function in ["generate", "asm", "comment"]:
                # Found an AR API call! Now get the caller (one frame up)
                if i + 1 < len(stack_snapshot):
                    caller_frame = stack_snapshot[i + 1]

                    # Create a shortened path for the comment
                    shortened_path = "/".join(caller_frame.filename.split(os.sep)[-2:])

                    return caller_frame.filename, shortened_path, caller_frame.lineno

    constructors = {
        AsmUnit.__init__,
        DataUnit.__init__,
    }

    # Search for AR API calls in the stack
    for i, frame_info in enumerate(stack_snapshot):
        
        # Check if the function is one of our AR API methods
        if get_function_from_frame(frame_info) in constructors:
            # Found an AR API call! Now get the caller (one frame up)
            if i + 2 < len(stack_snapshot):
                caller_frame = stack_snapshot[i + 2]

                # Create a shortened path for the comment
                shortened_path = "/".join(caller_frame.filename.split(os.sep)[-2:])

                return caller_frame.filename, shortened_path, caller_frame.lineno

    # Hard error if we can't find any AR API entry point
    raise ValueError("get_last_user_context failed: No AR API entry point found in call stack. "
                    "Expected to find AR.generate(), AR.asm(), or other AR API methods.")


class DataUnit:
    def __init__(
            self,
            byte_size: int,
            memory_segment_id: str,
            memory_segment,
            memory_block_id: str,
            name: str = None,
            address: Optional[int] = None,
            alignment: Optional[int] = None,
            init_value_byte_representation: list[int] = None,
            pa_address: Optional[int] = None,
            segment_offset: Optional[int] = None,
    ):
        """
        Initializes an DataUnit from shared or preserved blocks. later be published into the date_usage file
        """
        self.name = name
        self.address = address
        self.pa_address = pa_address
        self.segment_offset = segment_offset
        self.byte_size = byte_size
        self.memory_block_id = memory_block_id
        self.memory_segment = memory_segment
        self.memory_segment_id = memory_segment_id
        self.alignment = alignment
        self.init_value_byte_representation = init_value_byte_representation

        # extract context to generated data
        self.file_name, self.file_name_shortened_path, self.line_number = get_last_user_context()

        if self.init_value_byte_representation is not None:
            formatted_bytes = ", ".join(f"0x{byte:02x}" for byte in self.init_value_byte_representation)
        else:
            formatted_bytes = "None"

        self.data_unit_str = f"[name:{self.name}, memory_block:{self.memory_block_id}, memory_segment_name:{self.memory_segment_id}, "
        if address is not None:
            self.data_unit_str += f"address:{hex(self.address)}, pa_address:{hex(self.pa_address)}, segment_offset:{hex(self.segment_offset)}, "
        self.data_unit_str += f"byte_size:{self.byte_size}, alignment:{self.alignment}, init_value:{formatted_bytes}, file: {self.file_name_shortened_path}, line: {self.line_number}]"
        # print(self.data_unit_str)
        # logger = get_logger()
        # logger.debug(f"DataUnit generated: {self.data_unit_str}")

    def __str__(self):
        return self.data_unit_str
