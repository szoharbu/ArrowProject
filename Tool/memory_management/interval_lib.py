import random

'''
Here's a conceptual design:

1. Memory Interval Representation:
We'll represent memory intervals using tuples, where an interval is represented as (start, size).

2. Free and Used Pools:
free_intervals: A list (or set) of free intervals.
used_intervals: A list (or set) of used intervals.
3. Basic Functions:
Initialization: Define the initial memory space.
Allocate Block: Find a random free interval, slice it to match the requested size, and move it to the used pool.
Free Block: Move an interval from the used pool back to the free pool.
'''

class IntervalLib:
    def __init__(self, start_address, total_size, is_empty=False):
        """
        Initialize memory with a single large interval or empty.
        :param start_address: starting address of the memory space in bytes.
        :param total_size: Total size of the memory space in bytes.
        :param is_empty: If True, initialize with no free intervals

        PLEASE NOTICE:: Each interval consist of [start, size]
        """
        self.start_address = start_address
        self.total_size = total_size
        
        # Start with the whole memory space as a single free interval or with empty free intervals
        if is_empty:
            self.free_intervals = []
        else:
            self.free_intervals = [(start_address, total_size)]
            
        self.used_intervals = []

    def _find_suitable_intervals(self, size, alignment=1):
        """
        Find all intervals where the requested size will fit, considering alignment.
        
        :param size: Size of the memory block in bytes
        :param alignment: Memory alignment requirement
        :return: List of (interval, aligned_start, max_start) tuples
        """
        if size <= 0:
            return []
            
        suitable_intervals = []
        
        # Filter free intervals where the size is greater than or equal to the requested size
        for interval in self.free_intervals:
            start, interval_size = interval
            
            if interval_size >= size:
                # Handle alignment
                if alignment > 1:
                    # Calculate first aligned address in the interval
                    first_aligned = (start + alignment - 1) & ~(alignment - 1)
                    
                    # Calculate last possible aligned address that fits the block
                    max_start = start + interval_size - size
                    last_aligned = max_start & ~(alignment - 1)
                    
                    if first_aligned <= last_aligned:
                        suitable_intervals.append((interval, first_aligned, last_aligned))
                else:
                    # No alignment needed
                    max_start = start + interval_size - size
                    suitable_intervals.append((interval, start, max_start))
                    
        return suitable_intervals

    def find_region(self, size, alignment_bits=None):
        """
        Find a region of the given size in the free intervals.
        Returns the start address of a suitable region, or None if not found.
        
        :param size: Size of the region needed (in bytes)
        :param alignment_bits: If provided, the allocated memory block will have its lower X bits set to 0
        :return: (start, size) tuple or None if not found
        """
        if size <= 0:
            return None
            
        # Handle alignment
        if alignment_bits is None:
            alignment_bits = 0
        if alignment_bits < 0:
            return None
        # Calculate alignment value (2^alignment_bits)
        alignment = 1 << alignment_bits if alignment_bits > 0 else 1
        
        # Find suitable intervals
        suitable_intervals = self._find_suitable_intervals(size, alignment)
        
        if not suitable_intervals:
            return None
            
        # Select an interval - randomized
        if len(suitable_intervals) > 1:
            chosen_idx = random.randrange(0, len(suitable_intervals))
        else:
            chosen_idx = 0
            
        interval, first_aligned, last_aligned = suitable_intervals[chosen_idx]
        start, interval_size = interval
        
        # Determine the position within the interval - always randomized
        if alignment > 1 and first_aligned != last_aligned:
            # Count number of possible positions
            count = ((last_aligned - first_aligned) // alignment) + 1
            
            # Choose a random position mathematically
            random_offset = random.randint(0, count - 1) * alignment
            position_start = first_aligned + random_offset
        elif alignment <= 1:
            # Randomize the position within the selected interval
            max_start = start + interval_size - size
            position_start = random.randint(start, max_start)
        else:
            # Just use first aligned position if there's only one option
            position_start = first_aligned
        
        return (position_start, size)
        
    def allocate(self, size, alignment_bits=None):
        """
        Allocate a memory block of a given size from free intervals.
        The block is selected randomly and removed from the free pool.
        
        :param size: Size of the memory block to allocate in bytes
        :param alignment_bits: If provided, the allocated memory block will have its lower X bits set to 0
        :return: The allocated memory interval (start, size)
        """
        if size <= 0 or size > self.total_size:
            raise ValueError("Invalid block size")
            
        # Find a region using our randomized finder
        region = self.find_region(size, alignment_bits)
        
        if region is None:
            raise MemoryError("No suitable free intervals available")
            
        random_start, alloc_size = region
        
        # Find the interval that contains this region
        containing_interval = None
        for interval in self.free_intervals:
            int_start, int_size = interval
            int_end = int_start + int_size
            
            if int_start <= random_start and random_start + alloc_size <= int_end:
                containing_interval = interval
                break
                
        if not containing_interval:
            raise RuntimeError("Internal error: region not found in free intervals")
            
        start, interval_size = containing_interval
            
        # Split the selected interval into pre and post-allocated parts
        before_alloc = (start, random_start - start) if random_start > start else None
        after_alloc = (random_start + size, interval_size - (
                    random_start + size - start)) if random_start + size < start + interval_size else None

        # Remove the selected free interval
        self.free_intervals.remove(containing_interval)

        # Add the remaining free parts back, if they exist
        if before_alloc and before_alloc[1] > 0:
            self.free_intervals.append(before_alloc)
        if after_alloc and after_alloc[1] > 0:
            self.free_intervals.append(after_alloc)

        # Add the allocated block to the used pool
        allocated_interval = (random_start, size)
        self.used_intervals.append(allocated_interval)

        return allocated_interval

    def free(self, interval):
        """
        Free a previously allocated interval.
        :param interval: The interval to free (start, size).
        """
        if interval not in self.used_intervals:
            raise ValueError("Interval not found in used intervals")

        # Remove from used intervals and add back to free intervals
        self.used_intervals.remove(interval)
        self.free_intervals.append(interval)

        # In a more advanced version, we could also merge adjacent free intervals here

    def get_free_intervals(self):
        """
        Get the list of current free intervals.
        :return: List of free intervals.
        """
        return self.free_intervals

    def get_used_intervals(self):
        """
        Get the list of current used intervals.
        :return: List of used intervals.
        """
        return self.used_intervals
        
    # New methods for region management
    
    def add_region(self, start, size):
        """
        Add a region to the free intervals pool.
        
        :param start: Start address of the region
        :param size: Size of the region in bytes
        :return: True if added successfully, False otherwise
        """
        # Check if region is valid
        if size <= 0:
            return False
            
        new_interval = (start, size)
        new_end = start + size
        
        # Check if the region can be merged with existing free intervals
        # This helps prevent fragmentation and ensures better randomization
        merged = False
        merged_intervals = []
        remaining_intervals = []
        
        for interval in self.free_intervals:
            int_start, int_size = interval
            int_end = int_start + int_size
            
            # Check if regions are adjacent or overlapping
            if (int_start <= new_end and int_end >= start):
                # Merge the intervals
                merged = True
                merged_start = min(start, int_start)
                merged_end = max(new_end, int_end)
                merged_size = merged_end - merged_start
                merged_intervals.append((merged_start, merged_size))
            else:
                # Keep non-merged intervals
                remaining_intervals.append(interval)
                
        if merged:
            # Replace old intervals with merged ones
            self.free_intervals = remaining_intervals
            
            # Add all merged intervals
            for merged_interval in merged_intervals:
                self.free_intervals.append(merged_interval)
                
            # Further merge any adjacent merged intervals
            self._merge_adjacent_intervals()
            return True
        else:
            # No merging needed, just add the new interval
            self.free_intervals.append(new_interval)
            return True
            
    def _merge_adjacent_intervals(self):
        """Helper method to merge any adjacent intervals in the free pool"""
        if not self.free_intervals or len(self.free_intervals) < 2:
            return
            
        # Sort intervals by start address for easier merging
        self.free_intervals.sort(key=lambda interval: interval[0])
        
        # Merge adjacent intervals
        i = 0
        while i < len(self.free_intervals) - 1:
            curr_start, curr_size = self.free_intervals[i]
            curr_end = curr_start + curr_size
            
            next_start, next_size = self.free_intervals[i+1]
            
            # If intervals are adjacent
            if curr_end == next_start:
                # Merge them
                merged_size = curr_size + next_size
                self.free_intervals[i] = (curr_start, merged_size)
                # Remove the next interval
                del self.free_intervals[i+1]
            else:
                i += 1
        
    def remove_region(self, start, size):
        """
        Remove a region from the free intervals pool.
        If the region overlaps with existing free intervals, split them accordingly.
        
        :param start: Start address of the region to remove
        :param size: Size of the region in bytes
        :return: True if removed (or partially removed), False if no overlap
        """
        if size <= 0:
            return False
            
        region_end = start + size
        modified = False
        
        # Create a new list for updated free intervals
        new_free_intervals = []
        
        for interval in self.free_intervals:
            int_start, int_size = interval
            int_end = int_start + int_size
            
            # No overlap case - keep the interval as is
            if region_end <= int_start or start >= int_end:
                new_free_intervals.append(interval)
                continue
                
            modified = True
            
            # Check if we need to create a left fragment
            if start > int_start:
                left_size = start - int_start
                new_free_intervals.append((int_start, left_size))
                
            # Check if we need to create a right fragment
            if region_end < int_end:
                right_size = int_end - region_end
                new_free_intervals.append((region_end, right_size))
                
        # Update free intervals list
        self.free_intervals = new_free_intervals
        return modified
        
    def is_region_available(self, start, size):
        """
        Check if a specific region is fully contained within free intervals.
        
        :param start: Start address of the region
        :param size: Size of the region in bytes
        :return: True if the entire region is available, False otherwise
        """
        if size <= 0:
            return True
            
        region_end = start + size
        
        # Check each free interval
        for interval in self.free_intervals:
            int_start, int_size = interval
            int_end = int_start + int_size
            
            # If the region is fully contained in this interval, it's available
            if start >= int_start and region_end <= int_end:
                return True
                
        return False
