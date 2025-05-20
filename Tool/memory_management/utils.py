import os
import logging
from typing import List, Dict, Any, Optional
from Utils.configuration_management import get_config_manager, Configuration
from Utils.logger_management import get_logger
from Tool.state_management import get_state_manager

# Memory log file handler (will be initialized on first use)
_memory_log_handler = None
_memory_logger = None

def memory_log(message, level="info", print_both=False):
    """
    Log memory-related information based on configured log flavor.
    
    :param message: The message to log
    :param level: The logging level (default: "info"), can be "debug", "info", "warning", "error", "critical"
    """
    global _memory_log_handler, _memory_logger
    
    # Convert string level to logging module level integers
    if isinstance(level, str):
        level_map = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL
        }
        # Default to INFO if level string is not recognized
        level = level_map.get(level.lower(), logging.INFO)
    
    # Get the configuration
    config_manager = get_config_manager()
    memory_debug_prints = config_manager.get_value('Memory_debug_prints')
    
    # If logging is disabled, return immediately
    if memory_debug_prints is None:
        return
    
    # Get the standard logger for info_log output
    logger = get_logger()
    
    # If we should also log to the standard log
    if memory_debug_prints == "info_log" or level == logging.ERROR or print_both:
        logger.log(level, message)
    
    # Initialize memory logger if it hasn't been done yet
    if _memory_logger is None:
        _memory_logger = logging.getLogger('memory_logger')
        _memory_logger.setLevel(logging.DEBUG)
        
        # Prevent the logger from propagating messages to the root logger
        _memory_logger.propagate = False
        
        # Setup the log file handler if not already done
        if _memory_log_handler is None:
            try:
                output_dir = config_manager.get_value('output_dir_path')
                if output_dir:
                    memory_debug_log = os.path.join(output_dir, "memory_debug.log")
                    
                    # Create directory if it doesn't exist
                    os.makedirs(os.path.dirname(memory_debug_log), exist_ok=True)
                    
                    # Create and configure the file handler
                    _memory_log_handler = logging.FileHandler(memory_debug_log)
                    _memory_log_handler.setLevel(logging.DEBUG)
                    formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
                    _memory_log_handler.setFormatter(formatter)
                    _memory_logger.addHandler(_memory_log_handler)
                    
                    # Log initialization
                    _memory_logger.info("Memory logging initialized")
            except Exception as e:
                # If there's an error setting up the file logger, log to the standard logger
                logger.warning(f"Failed to initialize memory log file: {e}")
                # Create a console handler as fallback
                console_handler = logging.StreamHandler()
                console_handler.setLevel(logging.DEBUG)
                formatter = logging.Formatter('MEMORY: %(message)s')
                console_handler.setFormatter(formatter)
                _memory_logger.addHandler(console_handler)
    
    # Log to memory logger
    if _memory_logger is not None:
        _memory_logger.log(level, message)

def print_intervals_summary(interval_name: str, intervals, verbose: bool = False):
    """
    Print summary of memory intervals
    
    :param interval_name: Name of the interval type
    :param intervals: The interval object containing free_intervals
    :param verbose: If True, prints more detailed information
    """
    memory_log(f"  {interval_name} regions: {len(intervals.free_intervals)}")
    
    if verbose and intervals.free_intervals:
        for i, interval in enumerate(intervals.free_intervals):
            start, size = interval
            memory_log(f"    Region {i}: 0x{start:x}-0x{start+size-1:x}, size:0x{size:x}")

def print_page_summary(pages, prefix="", verbose=False, page_type=None):
    """
    Print summary of memory pages
    
    :param pages: List of Page objects
    :param prefix: String prefix for indentation
    :param verbose: If True, print detailed information
    :param page_type: Optional filter for page type
    """
    if page_type:
        filtered_pages = [p for p in pages if p.page_type == page_type]
        type_str = f" {page_type}"
    else:
        filtered_pages = pages
        type_str = ""
        
    memory_log(f"{prefix}{type_str} Pages ({len(filtered_pages)}):")
    
    if verbose:
        for i, page in enumerate(filtered_pages):
            memory_log(f"{prefix}  Page {i}: {page}")

def print_pages_by_type(pages, prefix="", verbose=False):
    """
    Print pages grouped by their type
    
    :param pages: List of Page objects
    :param prefix: String prefix for indentation
    :param verbose: If True, print detailed information
    """
    # Group pages by type
    code_pages = []
    data_pages = []
    other_pages = []
    
    for page in pages:
        if page.page_type == Configuration.Page_types.TYPE_CODE:
            code_pages.append(page)
        elif page.page_type == Configuration.Page_types.TYPE_DATA:
            data_pages.append(page)
        else:
            other_pages.append(page)
    
    # Print each group
    print_page_summary(code_pages, prefix, verbose, "Code")
    print_page_summary(data_pages, prefix, verbose, "Data")
    
    if other_pages:
        print_page_summary(other_pages, prefix, verbose, "Other")

def print_allocation_summary(allocations, prefix="", verbose=False):
    """
    Print summary of memory allocations
    
    :param allocations: List of MemoryAllocation objects
    :param prefix: String prefix for indentation
    :param verbose: If True, print detailed information
    """
    memory_log(f"{prefix}Allocations: {len(allocations)}")
    
    for i, alloc in enumerate(allocations):
        page_str = f", spans {len(alloc.covered_pages)} pages" if hasattr(alloc, 'covered_pages') and alloc.covered_pages else ""
        memory_log(f"{prefix}  Alloc {i}: VA:0x{alloc.va_start:x}-0x{alloc.va_start+alloc.size-1:x}, "
                  f"PA:0x{alloc.pa_start:x}, size:0x{alloc.size:x}, type:{alloc.page_type}{page_str}")
        
        if verbose and hasattr(alloc, 'covered_pages') and alloc.covered_pages:
            memory_log(f"{prefix}    Covered Pages:")
            for j, page in enumerate(alloc.covered_pages):
                memory_log(f"{prefix}      Page {j}: {page}")

def print_segments_summary(segments, prefix="", verbose=False):
    """
    Print summary of memory segments
    
    :param segments: List of MemorySegment objects
    :param prefix: String prefix for indentation
    :param verbose: If True, print detailed information
    """
    memory_log(f"{prefix}Segments: {len(segments)}")
    
    for i, segment in enumerate(segments):
        page_info = f", spans {len(segment.covered_pages)} pages" if hasattr(segment, 'covered_pages') and segment.covered_pages else ""
        memory_log(f"{prefix}  Segment {i}: {segment.name}, VA:0x{segment.address:x}, size:0x{segment.byte_size:x}, "
                 f"type:{segment.memory_type}{page_info}")
        
        if verbose and hasattr(segment, 'covered_pages') and segment.covered_pages:
            memory_log(f"{prefix}    Covered Pages:")
            for j, page in enumerate(segment.covered_pages):
                memory_log(f"{prefix}      Page {j}: {page}")
                
        # If it's a data segment with data units, show them too
        if verbose and hasattr(segment, 'data_units_list') and segment.data_units_list:
            memory_log(f"{prefix}    Data Units: {len(segment.data_units_list)}")
            for j, data_unit in enumerate(segment.data_units_list):
                memory_log(f"{prefix}      Unit {j}: {data_unit}")

def print_segments_by_type(segments, prefix="", verbose=False):
    """
    Print segments grouped by their type
    
    :param segments: List of MemorySegment objects
    :param prefix: String prefix for indentation
    :param verbose: If True, print detailed information
    """
    # Group segments by type
    code_segments = []
    data_segments = []
    
    for segment in segments:
        if segment.memory_type in [Configuration.Memory_types.CODE, 
                                 Configuration.Memory_types.BOOT_CODE, 
                                 Configuration.Memory_types.BSP_BOOT_CODE]:
            code_segments.append(segment)
        else:
            data_segments.append(segment)
    
    memory_log(f"{prefix}Code segments: {len(code_segments)}")
    print_segments_summary(code_segments, prefix + "  ", verbose)
    
    memory_log(f"{prefix}Data segments: {len(data_segments)}")
    print_segments_summary(data_segments, prefix + "  ", verbose)

def convert_int_value_to_bytes(init_value, element_size):
    """
    Convert a large integer into a list of bytes, ensuring the block size is respected.
    Returns a list of integers, each representing a byte.
    """
    byte_representation = []

    # Calculate the number of bytes needed to represent the value
    num_bytes = (init_value.bit_length() + 7) // 8

    # Collect bytes into a list (little-endian order)
    for i in range(num_bytes):
        byte_representation.append((init_value >> (i * 8)) & 0xFF)

    # Pad with zeros if the init_value is smaller than the element size
    while len(byte_representation) < element_size:
        byte_representation.append(0)

    return byte_representation


def convert_bytes_to_words(byte_representation):
    """
    Convert a list of bytes (integers) into a list of words (and smaller chunks if needed).
    Returns a list of tuples in the format (value, type) where type is "word" or "byte".
    """
    word_size = 4  # Number of bytes per word
    words = []  # List to hold the result
    num_bytes = len(byte_representation)

    idx = 0
    while idx < num_bytes:
        # If enough bytes are available for a word
        if idx + word_size <= num_bytes:
            # Combine 4 bytes into a word (little-endian order)
            word_value = 0
            for i in range(word_size):
                word_value |= byte_representation[idx + i] << (i * 8)
            words.append((word_value, "word"))
            idx += word_size
        else:
            # Handle remaining bytes
            remaining_bytes = num_bytes - idx
            byte_value = 0
            for i in range(remaining_bytes):
                byte_value |= byte_representation[idx + i] << (i * 8)
            words.append((byte_value, "byte"))
            idx += remaining_bytes

    return words

def print_memory_state(memory_space_manager=None, memory_manager=None, print_both=False):
    """
    Print a comprehensive summary of the current memory state across all states.
    Shows all states, pages, and segments without unmapped/unallocated regions.
    
    :param memory_space_manager: Optional MemorySpaceManager instance
    :param memory_manager: Optional MemoryManager instance
    """
    # Import here to avoid circular imports
    from Tool.memory_management.memory_space_manager import get_memory_space_manager
    
    # Get memory space manager if not provided
    if memory_space_manager is None:
        memory_space_manager = get_memory_space_manager()
    
    state_manager = get_state_manager()
    memory_log("\n\n\n")
    memory_log("==== MEMORY STATE SUMMARY ====", print_both=print_both)
    
    # 1. Summarize states and their pages
    memory_log(f"Total states: {len(state_manager.states_dict)}", print_both=print_both)
    
    for state_name, state in state_manager.states_dict.items():
        state_manager.set_active_state(state_name)
        state = state_manager.get_active_state()
        memory_log(f"---- State: {state_name}", print_both=print_both)
        
        # Get page table entries if available
        if hasattr(state, 'page_table_manager'):
            page_table_entries = state.page_table_manager.get_page_table_entries()
            
            # Group pages by type
            code_pages = []
            data_pages = []
            other_pages = []
            
            for page in page_table_entries:
                if page.page_type == Configuration.Page_types.TYPE_CODE:
                    code_pages.append(page)
                elif page.page_type == Configuration.Page_types.TYPE_DATA:
                    data_pages.append(page)
                else:
                    other_pages.append(page)
            
            # Print page summaries
            memory_log(f"-------- Pages: {len(page_table_entries)} total ({len(code_pages)} code, {len(data_pages)} data, {len(other_pages)} other)", print_both=print_both)
            
            if code_pages:
                memory_log(f"------------ Code Pages ({len(code_pages)}):", print_both=print_both)
                for i, page in enumerate(code_pages):
                    page_size = page.end_va - page.va + 1
                    memory_log(f"---------------- Page {i}: VA:0x{page.va:x}-0x{page.end_va:x}, PA:0x{page.pa:x}, size:0x{page_size:x}", print_both=print_both)
            
            if data_pages:
                memory_log(f"------------ Data Pages ({len(data_pages)}):", print_both=print_both)
                for i, page in enumerate(data_pages):
                    page_size = page.end_va - page.va + 1
                    memory_log(f"---------------- Page {i}: VA:0x{page.va:x}-0x{page.end_va:x}, PA:0x{page.pa:x}, size:0x{page_size:x}", print_both=print_both)
            
            if other_pages:
                memory_log(f"------------ Other Pages ({len(other_pages)}):", print_both=print_both)
                for i, page in enumerate(other_pages):
                    page_size = page.end_va - page.va + 1
                    memory_log(f"---------------- Page {i}: VA:0x{page.va:x}-0x{page.end_va:x}, PA:0x{page.pa:x}, size:0x{page_size:x}, type:{page.page_type}", print_both=print_both)
        else:
            memory_log(f"------------ No page table manager available for this state", print_both=print_both)
        
        # Get state allocations
        if state_name in memory_space_manager.state_allocated_va_intervals:
            state_allocations = [a for a in memory_space_manager.allocations 
                              if memory_space_manager.state_allocated_va_intervals[state_name].is_region_available(a.va_start, a.size)]
            
            memory_log(f"-------- Memory Segments : {len(state_allocations)}", print_both=print_both)
            for i, alloc in enumerate(state_allocations):
                page_str = f", spans {len(alloc.covered_pages)} pages" if hasattr(alloc, 'covered_pages') and alloc.covered_pages else ""
                memory_log(f"---------------- Segment {i}: VA:0x{alloc.va_start:x}-0x{alloc.va_start+alloc.size-1:x}, "
                         f"PA:0x{alloc.pa_start:x}, size:0x{alloc.size:x}, type:{alloc.page_type}{page_str}", print_both=print_both)
    
    # 2. List all memory segments if a memory manager was provided
    if memory_manager is not None and hasattr(memory_manager, "memory_segments"):
        memory_log("\n--- Memory Segments ---", print_both=print_both)
        
        # Group segments by type
        code_segments = []
        data_segments = []
        
        for segment in memory_manager.memory_segments:
            if segment.memory_type in [Configuration.Memory_types.CODE, 
                                    Configuration.Memory_types.BOOT_CODE, 
                                    Configuration.Memory_types.BSP_BOOT_CODE]:
                code_segments.append(segment)
            else:
                data_segments.append(segment)
        
        memory_log(f"Total segments: {len(memory_manager.memory_segments)} ({len(code_segments)} code, {len(data_segments)} data)", print_both=print_both)
        
        if code_segments:
            memory_log(f"Code Segments:", print_both=print_both)
            for i, segment in enumerate(code_segments):
                memory_log(f"  {i}: {segment.name}, VA:0x{segment.address:x}-0x{segment.address+segment.byte_size-1:x}, "
                        f"size:0x{segment.byte_size:x}, type:{segment.memory_type}", print_both=print_both)
        
        if data_segments:
            memory_log(f"Data Segments:", print_both=print_both)
            for i, segment in enumerate(data_segments):
                memory_log(f"  {i}: {segment.name}, VA:0x{segment.address:x}-0x{segment.address+segment.byte_size-1:x}, "
                        f"size:0x{segment.byte_size:x}, type:{segment.memory_type}", print_both=print_both)
                
                # List data units if available
                if hasattr(segment, 'data_units_list') and segment.data_units_list:
                    memory_log(f"    Data Units: {len(segment.data_units_list)}", print_both=print_both)
                    for j, data_unit in enumerate(segment.data_units_list[:5]):  # Show only first 5 to avoid excessive output
                        memory_log(f"      Unit {j}: {data_unit}", print_both=print_both)
                    if len(segment.data_units_list) > 5:
                        memory_log(f"      ... and {len(segment.data_units_list) - 5} more data units", print_both=print_both)
    
    memory_log("==== END MEMORY STATE SUMMARY ====", print_both=print_both)
    memory_log("\n\n\n")
