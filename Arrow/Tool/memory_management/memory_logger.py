import os
import logging
from typing import List, Dict, Any, Optional
from Arrow.Utils.configuration_management import get_config_manager, Configuration
from Arrow.Utils.logger_management import get_logger
from Arrow.Utils.singleton_management import SingletonManager
from Arrow.Tool.state_management import get_state_manager


class MemoryLogger:
    """
    Specialized logger for memory-related operations.
    Provides separate logging for memory operations with configurable output levels.
    """
    
    def __init__(self):
        self.logger = None
        self.file_handler = None
        self.console_handler = None
        self.initialized = False
        
    def _initialize(self):
        """Initialize the memory logger if not already done"""
        if self.initialized:
            return
            
        try:
            # Create dedicated memory logger
            self.logger = logging.getLogger('memory_logger')
            self.logger.setLevel(logging.DEBUG)
            self.logger.propagate = False  # Prevent propagation to root logger
            
            # Set up file handler
            config_manager = get_config_manager()
            output_dir = config_manager.get_value('output_dir_path')
            
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
                memory_debug_log = os.path.join(output_dir, "memory_debug.log")
                
                self.file_handler = logging.FileHandler(memory_debug_log, mode='w')
                self.file_handler.setLevel(logging.DEBUG)
                file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                self.file_handler.setFormatter(file_formatter)
                self.logger.addHandler(self.file_handler)
                        
            self.initialized = True
            
        except Exception as e:
            # Fallback to standard logger if memory logger setup fails
            standard_logger = get_logger()
            standard_logger.warning(f"Failed to initialize memory logger: {e}")
            self.logger = standard_logger
            self.initialized = True
    
    def log(self, message: str, level: str = "info", print_both: bool = False):
        """
        Log a memory-related message.
        
        Args:
            message: Message to log
            level: Log level (debug, info, warning, error, critical)
            print_both: If True, also log to standard logger
        """
        if not self.initialized:
            self._initialize()
        
        # Convert string level to logging constant
        level_map = {
            "debug": logging.DEBUG,
            "info": logging.INFO,
            "warning": logging.WARNING,
            "error": logging.ERROR,
            "critical": logging.CRITICAL
        }
        log_level = level_map.get(level.lower(), logging.INFO)
        
        # Check configuration to see if memory logging is enabled
        try:
            config_manager = get_config_manager()
            memory_debug_prints = config_manager.get_value('Memory_debug_prints')
            
            if memory_debug_prints is None:
                return  # Memory logging disabled
            
            # Log to memory logger
            if self.logger:
                self.logger.log(log_level, message)
            
            # Also log to standard logger if requested or if error level
            if print_both or memory_debug_prints == "info_log" or log_level >= logging.ERROR:
                standard_logger = get_logger()
                standard_logger.log(log_level, f"[MEMORY] {message}")
                
        except Exception as e:
            # Fallback to standard logger
            standard_logger = get_logger()
            standard_logger.warning(f"Memory logger error: {e}")
            standard_logger.log(log_level, f"[MEMORY] {message}")
    
    def debug(self, message: str, print_both: bool = False):
        """Log debug message"""
        self.log(message, "debug", print_both)
    
    def info(self, message: str, print_both: bool = False):
        """Log info message"""
        self.log(message, "info", print_both)
    
    def warning(self, message: str, print_both: bool = False):
        """Log warning message"""
        self.log(message, "warning", print_both)
    
    def error(self, message: str, print_both: bool = True):
        """Log error message (defaults to print_both=True)"""
        self.log(message, "error", print_both)
    
    def critical(self, message: str, print_both: bool = True):
        """Log critical message (defaults to print_both=True)"""
        self.log(message, "critical", print_both)

# Factory function to get memory logger instance
def get_memory_logger() -> MemoryLogger:
    """
    Factory function to retrieve the MemoryLogger instance.
    Uses singleton pattern for consistency with project architecture.
    """
    memory_logger_instance = SingletonManager.get("memory_logger_instance", default=None)
    if memory_logger_instance is None:
        memory_logger_instance = MemoryLogger()
        SingletonManager.set("memory_logger_instance", memory_logger_instance)
    return memory_logger_instance

def memory_log(message, level="info", print_both=False):
    """
    Convenience function for memory logging.
    
    :param message: The message to log
    :param level: The logging level (default: "info")
    :param print_both: Whether to also log to standard logger
    """
    memory_logger = get_memory_logger()
    memory_logger.log(message, level, print_both)

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

def print_memory_state(print_both=False):
    """
    Print a comprehensive summary of the current memory state across all states.
    Shows all states, pages, and segments without unmapped/unallocated regions.
    
    :param memory_space_manager: Optional MemorySpaceManager instance
    :param segment_manager: Optional SegmentManager instance
    """
    from Arrow.Tool.memory_management.memlayout.page_table_manager import get_page_table_manager
    page_table_manager = get_page_table_manager()

    memory_logger = get_memory_logger()

    memory_logger.info("\n\n\n")
    memory_logger.info("==== MEMORY STATE SUMMARY ====", print_both=print_both)
    
    
    for page_table in page_table_manager.get_all_page_tables():
        memory_logger.info(f"---- Page Table: {page_table.page_table_name}", print_both=print_both)

        page_table_entries = page_table.get_pages()
    
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
        memory_logger.info(f"------ Pages: {len(page_table_entries)} total ({len(code_pages)} code, {len(data_pages)} data, {len(other_pages)} other)", print_both=print_both)
        
        if code_pages:
            memory_logger.info(f"-------- Code Pages ({len(code_pages)}):", print_both=print_both)
            for i, page in enumerate(code_pages):
                page_size = page.end_va - page.va + 1
                memory_logger.info(f"------------ Page {i}: {page.execution_context.value}, VA:0x{page.va:x}-0x{page.end_va:x}, PA:0x{page.pa:x}, size:0x{page_size:x}", print_both=print_both)
        
        if data_pages:
            memory_logger.info(f"-------- Data Pages ({len(data_pages)}):", print_both=print_both)
            for i, page in enumerate(data_pages):
                page_size = page.end_va - page.va + 1
                memory_logger.info(f"------------ Page {i}: {page.execution_context.value}, VA:0x{page.va:x}-0x{page.end_va:x}, PA:0x{page.pa:x}, size:0x{page_size:x}", print_both=print_both)
        
        if other_pages:
            memory_logger.info(f"-------- Other Pages ({len(other_pages)}):", print_both=print_both)
            for i, page in enumerate(other_pages):
                page_size = page.end_va - page.va + 1
                memory_logger.info(f"------------ Page {i}: VA:0x{page.va:x}-0x{page.end_va:x}, PA:0x{page.pa:x}, size:0x{page_size:x}, type:{page.page_type}", print_both=print_both)
            
        # Get state allocations
        page_table_allocations = page_table.allocated_va_intervals.get_intervals()
        memory_logger.info(f"------ Memory Segments : {len(page_table_allocations)}", print_both=print_both)
        for i, alloc in enumerate(page_table_allocations):
            memory_logger.info(f"------------ Segment {i}: VA:{hex(alloc.start)}-{hex(alloc.end)}, size:{hex(alloc.size)}, type:{alloc.metadata['page_type']}", print_both=print_both)

        # segments = page_table.segment_manager.get_segments()
        # memory_logger.info(f"------ Segments : {len(segments)}", print_both=print_both)
        # for i, segment in enumerate(segments):
        #     memory_logger.info(f"------------ Segment {i}: {segment.name}, VA:0x{segment.address:x}, size:0x{segment.byte_size:x}, type:{segment.memory_type}", print_both=print_both)


    memory_logger.info("==== END MEMORY STATE SUMMARY ====", print_both=print_both)
    memory_logger.info("\n\n\n")
