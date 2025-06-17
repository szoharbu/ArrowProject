from typing import Dict, Any, Optional, Tuple
class Interval:
    """
    Represents a memory interval with metadata support.
    """
    
    def __init__(self, start: int, size: int, metadata: Dict[str, Any] = None):
        """
        Initialize an interval with optional metadata.
        
        :param start: Starting address of the interval
        :param size: Size of the interval in bytes
        :param metadata: Metadata dictionary (can include memory_type, purpose, etc.)
        """
        self.start = start
        self.size = size
        self.metadata = metadata or {}
        
    @property
    def end(self) -> int:
        """End address of the interval (exclusive)"""
        return self.start + self.size
    
    def __repr__(self) -> str:
        return f"Interval(start=0x{self.start:x}, size=0x{self.size:x}, metadata={self.metadata})"
    
    def __str__(self) -> str:
        meta_str = ", ".join(f"{k}={v}" for k, v in self.metadata.items()) if self.metadata else "no metadata"
        # Show inclusive end address (last address that's actually part of the interval)
        inclusive_end = self.start + self.size - 1
        return f"[0x{self.start:x}-0x{inclusive_end:x}] size=0x{self.size:x} ({meta_str})"
    
    def contains(self, start: int, size: int) -> bool:
        """Check if this interval fully contains the given region"""
        return self.start <= start and start + size <= self.end
    
    def overlaps(self, start: int, size: int) -> bool:
        """Check if this interval overlaps with the given region"""
        return not (self.end <= start or self.start >= start + size)
    
    def is_adjacent(self, other: 'Interval') -> bool:
        """Check if this interval is adjacent to another interval"""
        return self.end == other.start or other.end == self.start
    
    def can_merge_with(self, other: 'Interval') -> bool:
        """Check if this interval can be merged with another (adjacent and compatible metadata)"""
        return self.is_adjacent(other) and self.metadata == other.metadata
    
    def merge_with(self, other: 'Interval') -> 'Interval':
        """Merge this interval with another adjacent interval"""
        if not self.can_merge_with(other):
            raise ValueError("Cannot merge non-adjacent or incompatible intervals")
        
        new_start = min(self.start, other.start)
        new_end = max(self.end, other.end)
        new_size = new_end - new_start
        
        return Interval(new_start, new_size, self.metadata.copy())
    
    def split_at(self, split_start: int, split_size: int) -> Tuple[Optional['Interval'], 'Interval', Optional['Interval']]:
        """
        Split this interval at the given position.
        Returns (before_interval, split_interval, after_interval)
        Any of these can be None if they would have zero size.
        """
        if not self.contains(split_start, split_size):
            raise ValueError("Split region is not fully contained in this interval")
        
        split_end = split_start + split_size
        
        # Before interval
        before = None
        if split_start > self.start:
            before = Interval(self.start, split_start - self.start, self.metadata.copy())
        
        # Split interval (the requested part)
        split_interval = Interval(split_start, split_size, self.metadata.copy())
        
        # After interval
        after = None
        if split_end < self.end:
            after = Interval(split_end, self.end - split_end, self.metadata.copy())
        
        return before, split_interval, after
    
    def matches_criteria(self, criteria: Dict[str, Any]) -> bool:
        """Check if this interval matches the given metadata criteria"""
        if not criteria:
            return True
        
        for key, value in criteria.items():
            if key not in self.metadata or self.metadata[key] != value:
                return False
        return True
    
    def to_tuple(self) -> Tuple[int, int]:
        """Convert to (start, size) tuple for backward compatibility"""
        return (self.start, self.size)
    
    @classmethod
    def from_tuple(cls, interval_tuple: Tuple[int, int], metadata: Dict[str, Any] = None) -> 'Interval':
        """Create an Interval from a (start, size) tuple"""
        start, size = interval_tuple
        return cls(start, size, metadata)
