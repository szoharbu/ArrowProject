import random
from Arrow_API import AR
from Arrow_API.resources.memory_manager import MemoryManager_API as MemoryManager
from Arrow_API.resources.register_manager import RegisterManager_API as RegisterManager
from Utils.configuration_management import Configuration

@AR.scenario_decorator(random=False, priority=Configuration.Priority.HIGH, tags=[Configuration.Tag.EXECUTION, Configuration.Tag.BRANCH])
def ARM_Branch_Prediction_Stress_scenario():
    '''
    ARM-specific branch prediction patterns that stress the branch predictor.
    Tests different branch types: conditional, indirect, and return stack buffer.
    '''
    # Pattern 1: Nested conditional branches (stresses conditional predictor)
    cond_regs = []
    for i in range(6):
        cond_reg = RegisterManager.get()
        AR.generate(dest=cond_reg, comment=f"Generate condition #{i}")
        cond_regs.append(cond_reg)
    
    # Create nested conditional structure
    AR.asm(f"cmp {cond_regs[0]}, #0", comment="First condition")
    AR.asm("bne .L_branch_1", comment="Conditional branch 1")
    
    AR.asm(f"cmp {cond_regs[1]}, {cond_regs[2]}", comment="Nested condition")
    AR.asm("bgt .L_branch_2", comment="Conditional branch 2")
    
    AR.asm(f"cmp {cond_regs[3]}, {cond_regs[4]}", comment="Deep nested condition")
    AR.asm("beq .L_branch_3", comment="Conditional branch 3")
    
    # Pattern 2: Indirect branches (stresses indirect predictor)
    jump_table_mem = MemoryManager.Memory(name="jump_table", byte_size=32, alignment=8)
    addr_reg = RegisterManager.get()
    
    AR.asm(f"ldr {addr_reg}, [{jump_table_mem.name}]", comment="Load indirect target")
    AR.asm(f"br {addr_reg}", comment="Indirect branch")
    
    # Pattern 3: Return stack buffer stress
    for i in range(8):  # ARM typically has 8-16 entry RSB
        AR.asm(f"bl .L_function_{i}", comment=f"Call function #{i}")
    
    # Labels for branch targets
    AR.asm(".L_branch_1:", comment="Branch target 1")
    AR.asm(".L_branch_2:", comment="Branch target 2") 
    AR.asm(".L_branch_3:", comment="Branch target 3")
    
    for i in range(8):
        AR.asm(f".L_function_{i}:", comment=f"Function #{i}")
        AR.asm("ret", comment=f"Return from function #{i}")

@AR.scenario_decorator(random=False, priority=Configuration.Priority.MEDIUM, tags=[Configuration.Tag.EXECUTION, Configuration.Tag.PIPELINE])
def ARM_Pipeline_Hazard_scenario():
    '''
    ARM-specific pipeline hazards including data hazards, structural hazards.
    Tests ARM's in-order and out-of-order execution characteristics.
    '''
    # Pattern 1: Data hazards (RAW dependencies)
    base_reg = RegisterManager.get()
    dep_regs = []
    
    AR.generate(dest=base_reg, comment="Initial value for dependency chain")
    
    # Create long dependency chain
    current_reg = base_reg
    for i in range(8):
        next_reg = RegisterManager.get()
        
        # Mix different instruction types to stress different execution units
        if i % 3 == 0:
            AR.asm(f"add {next_reg}, {current_reg}, #{i+1}", comment=f"ALU dependency #{i}")
        elif i % 3 == 1:
            AR.asm(f"lsl {next_reg}, {current_reg}, #{i%4}", comment=f"Shift dependency #{i}")
        else:
            AR.asm(f"mul {next_reg}, {current_reg}, {current_reg}", comment=f"MUL dependency #{i}")
        
        dep_regs.append(next_reg)
        current_reg = next_reg
    
    # Pattern 2: Structural hazards (same execution unit contention)
    mul_regs = []
    for i in range(4):
        src1_reg = RegisterManager.get()
        src2_reg = RegisterManager.get()
        dest_reg = RegisterManager.get()
        
        AR.generate(dest=src1_reg, comment=f"Mul source 1 #{i}")
        AR.generate(dest=src2_reg, comment=f"Mul source 2 #{i}")
        AR.asm(f"mul {dest_reg}, {src1_reg}, {src2_reg}", comment=f"Mul contention #{i}")
        mul_regs.append(dest_reg)
    
    # Pattern 3: Load-use hazards
    mem_reg = MemoryManager.Memory(name="load_use_mem", byte_size=32, alignment=4)
    for i in range(4):
        load_reg = RegisterManager.get()
        use_reg = RegisterManager.get()
        
        AR.asm(f"ldr {load_reg}, [{mem_reg.name}, #{i*4}]", comment=f"Load #{i}")
        AR.asm(f"add {use_reg}, {load_reg}, #1", comment=f"Immediate use #{i} - hazard")

@AR.scenario_decorator(random=False, priority=Configuration.Priority.HIGH, tags=[Configuration.Tag.MEMORY, Configuration.Tag.TLB])
def ARM_TLB_Memory_Management_scenario():
    '''
    ARM-specific TLB and memory management stress patterns.
    Tests page table walks, TLB misses, and memory ordering.
    '''
    # Create memory regions that will likely cause TLB misses
    # Use large offsets to access different pages
    page_size = 4096  # 4KB pages
    tlb_mem_regions = []
    
    for i in range(16):  # More regions than typical TLB entries
        # Create memory in different "pages" 
        tlb_mem = MemoryManager.Memory(name=f"tlb_page_{i}", byte_size=64, alignment=64)
        tlb_mem_regions.append(tlb_mem)
    
    # Pattern 1: Sequential page access (tests TLB replacement)
    access_regs = []
    for i, mem_region in enumerate(tlb_mem_regions):
        access_reg = RegisterManager.get()
        AR.asm(f"ldr {access_reg}, [{mem_region.name}]", comment=f"TLB access page #{i}")
        access_regs.append(access_reg)
    
    # Pattern 2: Random page access (stresses TLB with unpredictable pattern)
    random_indices = list(range(len(tlb_mem_regions)))
    random.shuffle(random_indices)
    
    for i, mem_idx in enumerate(random_indices[:8]):
        access_reg = RegisterManager.get()
        AR.asm(f"ldr {access_reg}, [{tlb_mem_regions[mem_idx].name}]", 
               comment=f"Random TLB access #{i} to page #{mem_idx}")
    
    # Pattern 3: Memory barrier and ordering instructions
    barrier_mem = MemoryManager.Memory(name="barrier_mem", byte_size=16, alignment=4)
    
    store_reg1 = RegisterManager.get()
    store_reg2 = RegisterManager.get()
    load_reg1 = RegisterManager.get()
    load_reg2 = RegisterManager.get()
    
    AR.generate(dest=store_reg1, comment="Value for ordered store 1")
    AR.generate(dest=store_reg2, comment="Value for ordered store 2")
    
    AR.asm(f"str {store_reg1}, [{barrier_mem.name}]", comment="Store before barrier")
    AR.asm("dmb sy", comment="Data memory barrier")
    AR.asm(f"str {store_reg2}, [{barrier_mem.name}, #4]", comment="Store after barrier")
    
    AR.asm("dsb sy", comment="Data synchronization barrier")
    AR.asm(f"ldr {load_reg1}, [{barrier_mem.name}]", comment="Load after barrier")
    AR.asm("isb", comment="Instruction synchronization barrier")
    AR.asm(f"ldr {load_reg2}, [{barrier_mem.name}, #4]", comment="Load after ISB")

@AR.scenario_decorator(random=False, priority=Configuration.Priority.MEDIUM, tags=[Configuration.Tag.FLOATING_POINT, Configuration.Tag.NEON])
def ARM_NEON_FP_Dependency_scenario():
    '''
    ARM NEON and floating-point specific dependency patterns.
    Tests vector register renaming and FP pipeline interactions.
    '''
    # Pattern 1: NEON vector dependencies
    vec_regs = []
    for i in range(8):
        vec_reg = RegisterManager.get_vector()  # Assuming NEON register API
        vec_regs.append(vec_reg)
    
    # Initialize vectors with different patterns
    init_mem = MemoryManager.Memory(name="neon_init", byte_size=128, alignment=16)
    for i, vec_reg in enumerate(vec_regs[:4]):
        AR.asm(f"ldr q{vec_reg}, [{init_mem.name}, #{i*16}]", comment=f"Load vector #{i}")
    
    # Create vector dependency chains
    AR.asm(f"add v{vec_regs[4]}.4s, v{vec_regs[0]}.4s, v{vec_regs[1]}.4s", 
           comment="Vector add dependency")
    AR.asm(f"mul v{vec_regs[5]}.4s, v{vec_regs[4]}.4s, v{vec_regs[2]}.4s", 
           comment="Vector mul dependency")
    AR.asm(f"fmla v{vec_regs[6]}.4s, v{vec_regs[5]}.4s, v{vec_regs[3]}.4s", 
           comment="Fused multiply-add dependency")
    
    # Pattern 2: NEON to scalar dependencies
    scalar_regs = []
    for i in range(4):
        scalar_reg = RegisterManager.get()
        AR.asm(f"umov {scalar_reg}, v{vec_regs[6]}.s[{i}]", comment=f"Extract lane #{i}")
        scalar_regs.append(scalar_reg)
    
    # Use extracted values in scalar operations
    result_reg = RegisterManager.get()
    AR.asm(f"add {result_reg}, {scalar_regs[0]}, {scalar_regs[1]}", comment="Scalar add from vector")
    AR.asm(f"mul {result_reg}, {result_reg}, {scalar_regs[2]}", comment="Scalar mul from vector")
    
    # Pattern 3: Floating-point specific hazards
    fp_regs = []
    for i in range(6):
        fp_reg = RegisterManager.get_fp()  # Assuming FP register API
        fp_regs.append(fp_reg)
    
    # FP dependency chain with different latencies
    AR.asm(f"fmov s{fp_regs[0]}, #{1.0}", comment="FP immediate")
    AR.asm(f"fadd s{fp_regs[1]}, s{fp_regs[0]}, s{fp_regs[0]}", comment="FP add")
    AR.asm(f"fmul s{fp_regs[2]}, s{fp_regs[1]}, s{fp_regs[1]}", comment="FP mul")
    AR.asm(f"fdiv s{fp_regs[3]}, s{fp_regs[2]}, s{fp_regs[0]}", comment="FP div (high latency)")
    AR.asm(f"fsqrt s{fp_regs[4]}, s{fp_regs[3]}", comment="FP sqrt (very high latency)")

@AR.scenario_decorator(random=False, priority=Configuration.Priority.LOW, tags=[Configuration.Tag.CACHE, Configuration.Tag.MEMORY])
def ARM_Cache_Hierarchy_Stress_scenario():
    '''
    ARM cache hierarchy stress patterns.
    Tests L1/L2/L3 cache behavior, cache line conflicts, and prefetching.
    '''
    # Pattern 1: Cache line conflict pattern
    # Create memory accesses that conflict in cache sets
    cache_line_size = 64
    cache_conflict_mem = MemoryManager.Memory(name="cache_conflict", byte_size=1024, alignment=64)
    
    # Access multiple addresses that map to same cache set
    conflict_offsets = [0, 512, 1024, 1536]  # Assuming 512-byte cache set spacing
    for i, offset in enumerate(conflict_offsets):
        access_reg = RegisterManager.get()
        AR.asm(f"ldr {access_reg}, [{cache_conflict_mem.name}, #{offset}]", 
               comment=f"Cache conflict access #{i}")
    
    # Pattern 2: Cache line bouncing between cores
    shared_cache_mem = MemoryManager.Memory(name="shared_cache", byte_size=256, 
                                          alignment=64, shared=True, cross_core=True)
    
    for i in range(4):
        bounce_reg = RegisterManager.get()
        AR.asm(f"ldr {bounce_reg}, [{shared_cache_mem.name}, #{i*64}]", 
               comment=f"Shared cache line #{i}")
        
        # Modify and store back (causes invalidation in other caches)
        AR.asm(f"add {bounce_reg}, {bounce_reg}, #1", comment="Modify cached data")
        AR.asm(f"str {bounce_reg}, [{shared_cache_mem.name}, #{i*64}]", 
               comment="Store back - cache invalidation")
    
    # Pattern 3: Streaming access pattern (tests cache bypassing)
    stream_mem = MemoryManager.Memory(name="stream_data", byte_size=2048, alignment=64)
    
    # Sequential streaming access
    for i in range(32):  # 32 * 64 = 2048 bytes
        stream_reg = RegisterManager.get()
        AR.asm(f"ldr {stream_reg}, [{stream_mem.name}, #{i*64}]", 
               comment=f"Stream access #{i}")
        
        # Use data immediately to prevent optimization
        temp_reg = RegisterManager.get()
        AR.asm(f"add {temp_reg}, {stream_reg}, #1", comment="Use streamed data") 