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
    def __init__(self, start_address, total_size):
        """
        Initialize memory with a single large interval.
        :param start_address: starting address of the memory space in bytes.
        :param total_size: Total size of the memory space in bytes.

        PLEASE NOTICE:: Each interval consist of [start, size]
        """
        self.start_address = start_address
        self.total_size = total_size
        # Start with the whole memory space as a single free interval
        self.free_intervals = [(start_address, total_size)]
        self.used_intervals = []

    def allocate(self, size):
        """
        Allocate a memory block of a given size from free intervals.
        The block is selected randomly from the free intervals and placed at a random location within it.
        :param size: Size of the memory block to allocate in bytes.
        :return: The allocated memory interval (start, size).
        """
        if size <= 0 or size > self.total_size:
            raise ValueError("Invalid block size")

        # Filter free intervals where the size is greater than or equal to the requested size
        available_intervals = [interval for interval in self.free_intervals if interval[1] >= size]

        if not available_intervals:
            raise MemoryError("No suitable free intervals available")

        # Randomly select one of the available intervals
        selected_interval = random.choice(available_intervals)
        start, interval_size = selected_interval

        '''
            [50000, 60000]
            random(50000, 
        '''

        # Randomize the position within the selected interval
        max_start = start + interval_size - size
        random_start = random.randint(start, max_start)  # Random start within the valid range of this interval
        allocated_interval = (random_start, size)

        # Split the selected interval into pre and post-allocated parts
        before_alloc = (start, random_start - start) if random_start > start else None
        after_alloc = (random_start + size, interval_size - (
                    random_start + size - start)) if random_start + size < start + interval_size else None

        # Remove the selected free interval
        self.free_intervals.remove(selected_interval)

        # Add the remaining free parts back, if they exist
        if before_alloc and before_alloc[1] > 0:
            self.free_intervals.append(before_alloc)
        if after_alloc and after_alloc[1] > 0:
            self.free_intervals.append(after_alloc)

        # Add the allocated block to the used pool
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
