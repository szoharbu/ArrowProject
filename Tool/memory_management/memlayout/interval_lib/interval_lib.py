import random
from typing import Dict, Any, Optional, List, Tuple, Union, Callable
from .interval import Interval

'''
IntervalLib - Pure Interval Management Utility

This library provides generic interval management without allocation state tracking.
It maintains a single list of intervals and provides operations to:
- Add/remove regions
- Find suitable regions
- Split/merge intervals
- Query by metadata

The caller is responsible for managing allocation states (unmapped/mapped/allocated).
'''

class IntervalLib:
    """
    Pure interval management utility.
    
    Maintains a single list of intervals and provides operations to manipulate them.
    Does not track allocation state - that's the caller's responsibility.
    """
    
    def __init__(self, start_address: int = None, total_size: int = None, 
                 default_metadata: Dict[str, Any] = None):
        """
        Initialize interval library.
        
        :param start_address: If provided, initialize with a single interval covering this range
        :param total_size: Size of the initial interval
        :param default_metadata: Default metadata for new intervals
        """
        self.intervals: List[Interval] = []
        self.default_metadata = default_metadata or {}
        
        # Initialize with a single interval if parameters provided
        if start_address is not None and total_size is not None:
            self.add_region(start_address, total_size, self.default_metadata.copy())

    def add_region(self, start: int, size: int, metadata: Dict[str, Any] = None) -> bool:
        """
        Add a region to the interval list.
        
        :param start: Start address of the region
        :param size: Size of the region in bytes
        :param metadata: Metadata for the region
        :return: True if added successfully, False otherwise
        """
        if size <= 0:
            return False
            
        # Use default metadata if none provided
        final_metadata = self.default_metadata.copy()
        if metadata:
            final_metadata.update(metadata)
            
        new_interval = Interval(start, size, final_metadata)
        
        # Try to merge with existing intervals
        merged_intervals = [new_interval]
        remaining_intervals = []
        
        for interval in self.intervals:
            # Check if intervals can be merged
            merged_any = False
            for i, merged_interval in enumerate(merged_intervals):
                if merged_interval.can_merge_with(interval):
                    merged_intervals[i] = merged_interval.merge_with(interval)
                    merged_any = True
                    break
            
            if not merged_any:
                remaining_intervals.append(interval)
        
        # Update intervals
        self.intervals = remaining_intervals + merged_intervals
        
        # Further merge any adjacent intervals
        self._merge_adjacent_intervals()
        return True

    def remove_region(self, start: int, size: int) -> bool:
        """
        Remove a region from the interval list.
        If the region overlaps with existing intervals, split them accordingly.
        
        :param start: Start address of the region to remove
        :param size: Size of the region in bytes
        :return: True if removed (or partially removed), False if no overlap
        """
        if size <= 0:
            return False
            
        modified = False
        new_intervals = []
        
        for interval in self.intervals:
            # No overlap case - keep the interval as is
            if not interval.overlaps(start, size):
                new_intervals.append(interval)
                continue
                
            modified = True
            
            # Check if we need to create fragments
            if interval.contains(start, size):
                # Split the interval
                before, _, after = interval.split_at(start, size)
                if before:
                    new_intervals.append(before)
                if after:
                    new_intervals.append(after)
            elif start <= interval.start and start + size >= interval.end:
                # Remove entire interval (it's fully contained in the region to remove)
                pass  # Don't add it to new_intervals
            elif start <= interval.start:
                # Partial overlap at the beginning
                remaining_start = start + size
                remaining_size = interval.end - remaining_start
                if remaining_size > 0:
                    remaining = Interval(remaining_start, remaining_size, interval.metadata.copy())
                    new_intervals.append(remaining)
            else:
                # Partial overlap at the end
                remaining_size = start - interval.start
                if remaining_size > 0:
                    remaining = Interval(interval.start, remaining_size, interval.metadata.copy())
                    new_intervals.append(remaining)
        
        # Update intervals list
        self.intervals = new_intervals
        return modified

    def find_region(self, size: int, alignment_bits: int = None, 
                   criteria: Dict[str, Any] = None, 
                   custom_filter: Callable[[Interval], bool] = None) -> Optional[Tuple[int, int]]:
        """
        Find a region of the given size that matches the criteria.
        
        :param size: Size of the region needed (in bytes)
        :param alignment_bits: If provided, the region will be aligned to 2^alignment_bits
        :param criteria: Metadata criteria that the interval must match
        :param custom_filter: Optional custom filter function
        :return: (start, size) tuple or None if not found
        """
        if size <= 0:
            return None
            
        # Handle alignment
        alignment = 1 << alignment_bits if alignment_bits and alignment_bits > 0 else 1
        
        # Find suitable intervals
        suitable_intervals = self._find_suitable_intervals(size, alignment, criteria, custom_filter)
        
        if not suitable_intervals:
            return None
            
        # Select an interval - randomized
        chosen_idx = random.randrange(0, len(suitable_intervals)) if len(suitable_intervals) > 1 else 0
        interval, first_aligned, last_aligned = suitable_intervals[chosen_idx]
        
        # Determine the position within the interval - always randomized
        if alignment > 1 and first_aligned != last_aligned:
            # Count number of possible positions
            count = ((last_aligned - first_aligned) // alignment) + 1
            # Choose a random position
            random_offset = random.randint(0, count - 1) * alignment
            position_start = first_aligned + random_offset
        elif alignment <= 1:
            # Randomize the position within the selected interval
            max_start = interval.start + interval.size - size
            position_start = random.randint(interval.start, max_start)
        else:
            # Just use first aligned position if there's only one option
            position_start = first_aligned
        
        return (position_start, size)

    def split_region(self, start: int, size: int) -> Optional[Interval]:
        """
        Split a region from intervals without removing it.
        Returns the split interval if successful.
        
        :param start: Start address of the region to split
        :param size: Size of the region
        :return: The split interval or None if not possible
        """
        if size <= 0:
            return None
        
        # Find the interval that contains this region
        containing_interval = None
        for interval in self.intervals:
            if interval.contains(start, size):
                containing_interval = interval
                break
        
        if not containing_interval:
            return None
        
        # Split the interval
        before, split_interval, after = containing_interval.split_at(start, size)
        
        # Remove the original interval
        self.intervals.remove(containing_interval)
        
        # Add back the fragments
        if before:
            self.intervals.append(before)
        if after:
            self.intervals.append(after)
        
        return split_interval

    def contains_region(self, start: int, size: int, criteria: Dict[str, Any] = None) -> bool:
        """
        Check if a specific region is fully contained within intervals matching criteria.
        
        :param start: Start address of the region
        :param size: Size of the region in bytes
        :param criteria: Metadata criteria that the interval must match
        :return: True if the entire region is available, False otherwise
        """
        if size <= 0:
            return True
        
        # Check each interval
        for interval in self.intervals:
            # Check criteria compatibility
            if criteria and not interval.matches_criteria(criteria):
                continue
            
            # If the region is fully contained in this interval, it's available
            if interval.contains(start, size):
                return True
                
        return False

    def get_intervals(self, criteria: Dict[str, Any] = None, 
                     custom_filter: Callable[[Interval], bool] = None) -> List[Interval]:
        """
        Get intervals matching the given criteria.
        
        :param criteria: Metadata criteria to filter by
        :param custom_filter: Optional custom filter function
        :return: List of matching Interval objects
        """
        result = []
        
        for interval in self.intervals:
            # Check criteria
            if criteria and not interval.matches_criteria(criteria):
                continue
            
            # Check custom filter
            if custom_filter and not custom_filter(interval):
                continue
            
            result.append(interval)
        
        return result

    def get_total_size(self, criteria: Dict[str, Any] = None) -> int:
        """
        Get total size of intervals matching criteria.
        
        :param criteria: Metadata criteria to filter by (None means all intervals)
        :return: Total size in bytes
        """
        total = 0
        for interval in self.intervals:
            if criteria is None or interval.matches_criteria(criteria):
                total += interval.size
        return total

    def get_intervals_as_tuples(self, criteria: Dict[str, Any] = None) -> List[Tuple[int, int]]:
        """
        Get intervals as (start, size) tuples for backward compatibility.
        
        :param criteria: Metadata criteria to filter by
        :return: List of (start, size) tuples
        """
        return [interval.to_tuple() for interval in self.get_intervals(criteria)]

    def update_metadata(self, start: int, size: int, metadata: Dict[str, Any]) -> bool:
        """
        Update metadata for intervals that overlap with the given region.
        
        :param start: Start address of the region
        :param size: Size of the region
        :param metadata: Metadata to update/add
        :return: True if any intervals were updated
        """
        if size <= 0:
            return False
        
        updated = False
        for interval in self.intervals:
            if interval.overlaps(start, size):
                interval.metadata.update(metadata)
                updated = True
        
        return updated

    def clear(self):
        """Clear all intervals."""
        self.intervals.clear()

    def is_empty(self) -> bool:
        """Check if there are no intervals."""
        return len(self.intervals) == 0

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the intervals."""
        if not self.intervals:
            return {"count": 0, "total_size": 0, "metadata_types": {}}
        
        total_size = sum(interval.size for interval in self.intervals)
        
        # Count metadata types
        metadata_counts = {}
        for interval in self.intervals:
            for key, value in interval.metadata.items():
                if key not in metadata_counts:
                    metadata_counts[key] = {}
                if value not in metadata_counts[key]:
                    metadata_counts[key][value] = 0
                metadata_counts[key][value] += 1
        
        return {
            "count": len(self.intervals),
            "total_size": total_size,
            "metadata_types": metadata_counts,
            "size_range": (min(i.size for i in self.intervals), max(i.size for i in self.intervals))
        }

    # Private helper methods
    
    def _find_suitable_intervals(self, size: int, alignment: int = 1, 
                               criteria: Dict[str, Any] = None,
                               custom_filter: Callable[[Interval], bool] = None):
        """
        Find all intervals where the requested size will fit, considering alignment and criteria.
        
        :param size: Size of the memory block in bytes
        :param alignment: Memory alignment requirement
        :param criteria: Metadata criteria that the interval must match
        :param custom_filter: Optional custom filter function
        :return: List of (interval, aligned_start, max_start) tuples
        """
        if size <= 0:
            return []
            
        suitable_intervals = []
        
        for interval in self.intervals:
            # Check criteria compatibility
            if criteria and not interval.matches_criteria(criteria):
                continue
            
            # Check custom filter
            if custom_filter and not custom_filter(interval):
                continue
            
            if interval.size >= size:
                # Handle alignment
                if alignment > 1:
                    # Calculate first aligned address in the interval
                    first_aligned = (interval.start + alignment - 1) & ~(alignment - 1)
                    
                    # Calculate last possible aligned address that fits the block
                    max_start = interval.start + interval.size - size
                    last_aligned = max_start & ~(alignment - 1)
                    
                    if first_aligned <= last_aligned:
                        suitable_intervals.append((interval, first_aligned, last_aligned))
                else:
                    # No alignment needed
                    max_start = interval.start + interval.size - size
                    suitable_intervals.append((interval, interval.start, max_start))
                    
        return suitable_intervals

    def _merge_adjacent_intervals(self):
        """Helper method to merge any adjacent intervals with compatible metadata."""
        if not self.intervals or len(self.intervals) < 2:
            return
            
        # Sort intervals by start address for easier merging
        self.intervals.sort(key=lambda interval: interval.start)
        
        # Merge adjacent intervals
        i = 0
        while i < len(self.intervals) - 1:
            current = self.intervals[i]
            next_interval = self.intervals[i + 1]
            
            # If intervals can be merged
            if current.can_merge_with(next_interval):
                # Merge them
                merged = current.merge_with(next_interval)
                self.intervals[i] = merged
                # Remove the next interval
                del self.intervals[i + 1]
            else:
                i += 1

    def find_and_remove(self, size: int, alignment_bits: int = None, 
                       metadata_filter: Callable[[Dict[str, Any]], bool] = None) -> Tuple[int, int]:
        """
        Find a suitable region and immediately remove it from the intervals.
        This is a convenience method that combines find_region() and remove_region().
        
        Args:
            size: Required size in bytes
            alignment_bits: Alignment requirement (power of 2)
            metadata_filter: Optional function to filter intervals by metadata
            
        Returns:
            Tuple of (start_address, actual_size) if found and removed
            
        Raises:
            ValueError: If no suitable region is found
        """
        result = self.find_region(size, alignment_bits, metadata_filter)
        if result is None:
            alignment_str = f" with alignment {alignment_bits}" if alignment_bits else ""
            raise ValueError(f"Could not find region of size {size}{alignment_str}")
            
        start_address, found_size = result
        
        # Remove the exact size requested, not the found_size
        self.remove_region(start_address, size)
        
        return (start_address, size)
