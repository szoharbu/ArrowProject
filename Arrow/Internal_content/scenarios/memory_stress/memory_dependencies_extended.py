import random
from Arrow.Arrow_API import AR
from Arrow.Arrow_API.resources.memory_manager import MemoryManager_API as MemoryManager
from Arrow.Arrow_API.resources.register_manager import RegisterManager_API as RegisterManager
from Arrow.Utils.configuration_management import Configuration

@AR.scenario_decorator(random=False, priority=Configuration.Priority.HIGH, tags=[Configuration.Tag.MEMORY, Configuration.Tag.BYPASS])
def Load_Store_Queue_LSQ_Contention_scenario():
    '''
    Memory instructions create dynamic dependencies and LSQ contention.
    Tests bypass network stress when multiple instructions try to forward values.
    Pattern: Multiple loads/stores accessing related memory locations with dependencies
    '''
    # Create a series of memory locations that will cause LSQ contention
    base_mem = MemoryManager.Memory(name="lsq_base", byte_size=64, alignment=8)
    queue_depth = random.randint(4, 8)
    
    # Generate interleaved loads and stores to create contention
    load_regs = []
    store_regs = []
    
    for i in range(queue_depth):
        # Create dependent loads
        load_reg = RegisterManager.get()
        offset = i * 8
        AR.asm(f"ldr {load_reg}, [{base_mem.name}, #{offset}]", comment=f"Load #{i} - LSQ entry")
        load_regs.append(load_reg)
        
        # Create dependent stores using previous loads
        if i > 0:
            store_reg = load_regs[i-1]
            AR.asm(f"str {store_reg}, [{base_mem.name}, #{offset+32}]", comment=f"Store #{i} - depends on Load #{i-1}")
            
        # Add computational dependency to stress bypass
        if i > 1:
            compute_reg = RegisterManager.get()
            AR.asm(f"add {compute_reg}, {load_regs[i]}, {load_regs[i-1]}", comment="Bypass stress computation")
            load_regs.append(compute_reg)

@AR.scenario_decorator(random=False, priority=Configuration.Priority.MEDIUM, tags=[Configuration.Tag.MEMORY, Configuration.Tag.FORWARDING])
def Store_Forwarding_Bypass_Stress_scenario():
    '''
    Tests store forwarding and memory bypass stress patterns.
    When loads depend on previous stores, bypassing logic tries to forward data.
    Stresses the pipeline when bypass fails or partial forwarding occurs.
    '''
    # Create memory region for store forwarding tests
    forward_mem = MemoryManager.Memory(name="forward_region", byte_size=32, alignment=4)
    
    # Pattern 1: Perfect store-to-load forwarding
    store_reg1 = RegisterManager.get()
    load_reg1 = RegisterManager.get()
    AR.generate(dest=store_reg1, comment="Generate value for store")
    AR.asm(f"str {store_reg1}, [{forward_mem.name}]", comment="Store for forwarding")
    AR.asm(f"ldr {load_reg1}, [{forward_mem.name}]", comment="Load should forward from store")
    
    # Pattern 2: Partial forwarding (different sizes)
    store_reg2 = RegisterManager.get()
    load_reg2 = RegisterManager.get()
    AR.generate(dest=store_reg2, comment="Generate value for partial forward")
    AR.asm(f"str {store_reg2}, [{forward_mem.name}, #4]", comment="32-bit store")
    AR.asm(f"ldrh {load_reg2}, [{forward_mem.name}, #4]", comment="16-bit load - partial forward")
    
    # Pattern 3: Store forwarding with address dependency
    addr_reg = RegisterManager.get()
    store_reg3 = RegisterManager.get()
    load_reg3 = RegisterManager.get()
    AR.generate(dest=addr_reg, comment="Generate dynamic address")
    AR.generate(dest=store_reg3, comment="Generate store value")
    AR.asm(f"str {store_reg3}, [{forward_mem.name}, {addr_reg}]", comment="Store with computed address")
    AR.asm(f"ldr {load_reg3}, [{forward_mem.name}, {addr_reg}]", comment="Load with same computed address")

@AR.scenario_decorator(random=False, priority=Configuration.Priority.HIGH, tags=[Configuration.Tag.MEMORY, Configuration.Tag.SPECULATION])
def Memory_Disambiguation_Chain_Reaction_scenario():
    '''
    Tests memory disambiguation when memory accesses depend on unresolved prior stores.
    Creates speculation expansion and delayed memory disambiguation.
    '''
    # Create multiple memory regions with potential aliasing
    mem_regions = []
    for i in range(3):
        mem = MemoryManager.Memory(name=f"disambig_mem_{i}", byte_size=16, alignment=4)
        mem_regions.append(mem)
    
    # Create address registers that may alias
    addr_regs = []
    for i in range(4):
        addr_reg = RegisterManager.get()
        AR.generate(dest=addr_reg, comment=f"Address register #{i}")
        addr_regs.append(addr_reg)
    
    # Generate ambiguous store-load sequences
    for i in range(len(addr_regs)):
        store_val = RegisterManager.get()
        load_val = RegisterManager.get()
        
        AR.generate(dest=store_val, comment=f"Value for ambiguous store #{i}")
        
        # Store to potentially aliased address
        mem_idx = i % len(mem_regions)
        AR.asm(f"str {store_val}, [{mem_regions[mem_idx].name}, {addr_regs[i]}]", 
               comment=f"Ambiguous store #{i}")
        
        # Load from potentially aliased address (different index to create ambiguity)
        load_mem_idx = (i + 1) % len(mem_regions)
        load_addr_idx = (i + 2) % len(addr_regs)
        AR.asm(f"ldr {load_val}, [{mem_regions[load_mem_idx].name}, {addr_regs[load_addr_idx]}]",
               comment=f"Ambiguous load #{i} - may alias with store")
        
        # Use loaded value to create dependency chain
        if i > 0:
            compute_reg = RegisterManager.get()
            AR.asm(f"add {compute_reg}, {load_val}, {store_val}", comment="Dependency chain")

@AR.scenario_decorator(random=False, priority=Configuration.Priority.MEDIUM, tags=[Configuration.Tag.MEMORY, Configuration.Tag.ATOMIC])
def Atomic_Memory_Dependency_scenario():
    '''
    Tests atomic memory operations and their dependency patterns.
    Focuses on exclusive access patterns and memory ordering constraints.
    '''
    # Create shared memory for atomic operations
    atomic_mem = MemoryManager.Memory(name="atomic_region", byte_size=16, alignment=8, shared=True)
    
    # Pattern 1: Load-exclusive/Store-exclusive pairs
    exclusive_reg1 = RegisterManager.get()
    exclusive_reg2 = RegisterManager.get()
    status_reg = RegisterManager.get()
    
    AR.asm(f"ldxr {exclusive_reg1}, [{atomic_mem.name}]", comment="Load exclusive")
    AR.asm(f"add {exclusive_reg2}, {exclusive_reg1}, #1", comment="Modify exclusive value")
    AR.asm(f"stxr {status_reg}, {exclusive_reg2}, [{atomic_mem.name}]", comment="Store exclusive")
    AR.asm(f"cbnz {status_reg}, .-12", comment="Retry if exclusive failed")
    
    # Pattern 2: Atomic RMW operations with dependencies
    atomic_regs = []
    for i in range(3):
        src_reg = RegisterManager.get()
        dest_reg = RegisterManager.get()
        AR.generate(dest=src_reg, comment=f"Atomic source #{i}")
        AR.asm(f"ldadd {src_reg}, {dest_reg}, [{atomic_mem.name}, #{i*4}]", 
               comment=f"Atomic add #{i}")
        atomic_regs.append(dest_reg)
    
    # Create dependency chain using atomic results
    chain_reg = RegisterManager.get()
    AR.asm(f"add {chain_reg}, {atomic_regs[0]}, {atomic_regs[1]}", comment="Chain atomic results")
    AR.asm(f"add {chain_reg}, {chain_reg}, {atomic_regs[2]}", comment="Continue chain")

@AR.scenario_decorator(random=False, priority=Configuration.Priority.LOW, tags=[Configuration.Tag.MEMORY, Configuration.Tag.PREFETCH])
def Memory_Prefetch_Dependency_scenario():
    '''
    Tests prefetch instructions and their interaction with memory dependencies.
    Focuses on prefetch timing and cache behavior impact on execution.
    '''
    # Create memory regions for prefetch testing
    prefetch_mem = MemoryManager.Memory(name="prefetch_region", byte_size=256, alignment=64)
    
    # Issue prefetch instructions for different cache levels
    for i in range(4):
        offset = i * 64  # Cache line aligned
        AR.asm(f"prfm pldl1keep, [{prefetch_mem.name}, #{offset}]", 
               comment=f"Prefetch cache line #{i}")
    
    # Create delayed access pattern to test prefetch effectiveness
    access_regs = []
    for i in range(4):
        # Add some computational delay
        delay_reg1 = RegisterManager.get()
        delay_reg2 = RegisterManager.get()
        AR.generate(dest=delay_reg1, comment="Delay computation")
        AR.generate(dest=delay_reg2, comment="Delay computation")
        AR.asm(f"mul {delay_reg1}, {delay_reg1}, {delay_reg2}", comment="Multiply delay")
        
        # Access the prefetched memory
        access_reg = RegisterManager.get()
        offset = i * 64
        AR.asm(f"ldr {access_reg}, [{prefetch_mem.name}, #{offset}]", 
               comment=f"Access prefetched line #{i}")
        access_regs.append(access_reg)
    
    # Create dependencies using accessed data
    result_reg = RegisterManager.get()
    AR.asm(f"add {result_reg}, {access_regs[0]}, {access_regs[1]}", comment="Combine prefetched data")
    AR.asm(f"add {result_reg}, {result_reg}, {access_regs[2]}", comment="Continue combination")

@AR.scenario_decorator(random=False, priority=Configuration.Priority.HIGH, tags=[Configuration.Tag.MEMORY, Configuration.Tag.SIMD])
def SIMD_Memory_Dependency_scenario():
    '''
    Tests SIMD/NEON memory operations and their dependency patterns.
    Includes vector loads/stores and inter-lane dependencies.
    '''
    # Create SIMD-aligned memory regions
    simd_mem = MemoryManager.Memory(name="simd_region", byte_size=128, alignment=16)
    
    # Pattern 1: Vector load dependencies
    vec_regs = []
    for i in range(4):
        vec_reg = RegisterManager.get_vector()  # Assuming vector register API exists
        offset = i * 16
        AR.asm(f"ldr q{vec_reg}, [{simd_mem.name}, #{offset}]", 
               comment=f"Vector load #{i}")
        vec_regs.append(vec_reg)
    
    # Pattern 2: Inter-vector dependencies
    result_vec = RegisterManager.get_vector()
    AR.asm(f"add v{result_vec}.4s, v{vec_regs[0]}.4s, v{vec_regs[1]}.4s", 
           comment="Vector addition dependency")
    AR.asm(f"mul v{result_vec}.4s, v{result_vec}.4s, v{vec_regs[2]}.4s", 
           comment="Vector multiplication dependency")
    
    # Pattern 3: Vector-to-scalar dependencies
    scalar_reg = RegisterManager.get()
    AR.asm(f"umov {scalar_reg}, v{result_vec}.s[0]", comment="Extract scalar from vector")
    
    # Pattern 4: Scatter-gather style accesses
    for i in range(4):
        lane_reg = RegisterManager.get()
        AR.asm(f"umov {lane_reg}, v{vec_regs[3]}.s[{i}]", comment=f"Extract lane #{i}")
        AR.asm(f"ldr w{RegisterManager.get()}, [{simd_mem.name}, {lane_reg}]", 
               comment=f"Indirect load using lane #{i}") 