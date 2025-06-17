# memlayout
A lightweight, dependency-free Python library for managing memory layouts through interval-based allocation. Provides efficient address space management, alignment handling, and metadata tracking for systems programming, memory managers, and embedded applications.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              CLASS DIAGRAM                                      │
└─────────────────────────────────────────────────────────────────────────────────┘

                    ┌────────────────────────────────────┐
                    │        PageTableManager            │
                    │  (Singleton)                       │
                    ├────────────────────────────────────┤
                    │ + pa_intervals: IntervalLib        │
                    │ + PageTables: Dict[str, PageTable] │
                    │ + create_page_table()              │
                    │ + allocate_page_for_mmu()          │
                    │ + allocate_shared_page()           │
                    └────────────────────────────────────┘
                                     │ 
                                     │ manages 1..*
                                     ▼
                    ┌────────────────────────────────────┐
                    │            PageTable               │
                    ├────────────────────────────────────┤
                    │ + name: str                        │
                    │ + core_id: str                     │
                    │ + exception_level: EL              │
                    │ + va_intervals: IntervalLib        │
                    │ + page_table_entries: List[Page]   │           manage
                    │ + segment_manager: SegmentManager  │◆────────────────────────◆ ┌────────────────────────────────────┐
                    │ + allocate_va_interval()           │                            │           SegmentManager           │
                    │ + allocate_cross_core_page()       │                            ├────────────────────────────────────┤       
                    │ + map_va_to_pa()                   │                            │ + name: str                        │
                    │ + add_page()                       │                            │ ...                                │
                    └────────────────────────────────────┘                            │ ...                                │
                                     │                                                │ ...                                │
                                     │ contains 0..*                                  │ ...                                │ 
                                     ▼                                                └────────────────────────────────────┘
                    ┌─────────────────────────────────┐                                               │
                    │            Page                 │                                               │ contains 0..*
                    ├─────────────────────────────────┤                                               ▼  
                    │ + va: int                       │                                ┌─────────────────────────────────┐
                    │ + pa: int                       │                                │            Segment              │
                    │ + size: int                     │                                ├─────────────────────────────────┤
                    │ + page_type: PageType           │                                │ + name: str                     │
                    │ + permissions: int              │                                │ ...                             │
                    │ + custom_attributes: Dict       │                                │ ...                             │
                    │ + execution_context: EL         │                                │ ...                             │
                    └─────────────────────────────────┘                                │ ...                             │
                                                                                       │ ...                             │
                                                                                       │ ...                             │
                                                                                       └─────────────────────────────────┘