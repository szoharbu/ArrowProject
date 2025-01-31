import random
from Arrow_API import AR
from Arrow_API.resources.memory_manager import MemoryManager_API as MemoryManager
from Arrow_API.resources.register_manager import RegisterManager_API as RegisterManager
from Utils.configuration_management import Configuration

'''
some well-known assembly-level execution stress models that expand dependency graphs with memory dependencies and bypass stress:
1. Data Flow Graph (DFG) Expansion
    A directed graph representing instruction dependencies at execution time.
    Expands as more instructions depend on previous results.
    Used in compiler optimizations, dependency tracking, and out-of-order execution modeling.
2. Memory Dependency Graph (MDG)
    Tracks load-store dependencies across execution cycles.
    Expands as memory accesses increase, especially with dependent loads.
    Bypass stress occurs when the processor fails to forward values efficiently.
3. Load-Store Queue (LSQ) Contention
    Memory instructions (loads & stores) create dynamic dependencies.
    Causes bypass network stress when multiple instructions try to forward values.
4. Register Dependency Expansion (RAW Hazards in ALU Ops)
    A chain of arithmetic operations depending on previous registers.
    Expands execution stress until results are committed or forwarded.
5. Speculative Execution Dependency Graph
    Expands as speculative instructions execute before their validity is confirmed.
    Contraction happens when mispredictions flush the pipeline.
6. Store Forwarding & Memory Bypass Stress
    When load instructions depend on previous stores, bypassing logic tries to forward data.
    If the bypass fails, the pipeline stalls, creating dependency expansion.
7. Chain Reaction in Dependency Tracking (Memory Disambiguation)
    Occurs when memory accesses depend on unresolved prior stores.
    Speculation expands the execution window, delaying memory disambiguation.

check if relevant to ARM?
1. Reservation Station (RS) Dependency Propagation
    Used in Tomasulo’s algorithm for register renaming and out-of-order execution.
    Tracks instruction dependencies in dynamic execution.
    Memory dependencies cause delays if values aren't bypassed properly.
2. Reorder Buffer (ROB) Expansion
    Tracks instruction completion order in out-of-order execution.
    Expands as more uncommitted instructions are present.
    Contraction occurs when instructions retire and clear resources.
3. Execution Dependency Chains (Micro-op Fusion & Split Dependencies)
    Some x86 instructions are internally split into multiple micro-ops.
    If dependencies form between fused and non-fused instructions, execution stalls increase.

'''

@AR.scenario_decorator(random=True, priority=Configuration.Priority.MEDIUM, tags=[Configuration.Tag.MEMORY])
def Data_Flow_Graph_DFG_Expansion_scenario():
    '''
    A directed graph representing instruction dependencies at execution time.
    Expands as more instructions depend on previous results.
    1. Initialize first instruction (root node)
    2. Expand dependencies by generating multiple dependent instructions
    3. Each dependent instruction expands further with new dependencies
    4. Continue expansion until a threshold is reached
    5. Contract by resolving dependencies and completing instructions
    '''
    #          [Load A]
    #        /     |     \
    #    [B]     [C]      [D]   (First Expansion)
    #  / | \    / | \    / | \
    #[E][F][G][H][I][J][K][L][M]  (Second Expansion)

    max_depth = random.randint(2,4)  # How deep the dependency tree expands
    num_dependents = random.randint(2,4)  # Number of dependent instructions per instruction

    # Initialize Root Instruction
    root_mem = MemoryManager.Memory(name="root_memory", init_value=random.randint(0, 0x1000))
    dest_reg = RegisterManager.get()
    AR.generate(query=(AR.Instruction.group == "load"), src=root_mem, dest=dest_reg, comment="root load instruction")
    curr_resources = [dest_reg]

    # Expansion Phase: Each instruction generates X new dependent instructions
    for depth in range(max_depth):  # Loop through expansion levels
        next_resources = []  # Store resources for the next level

        for resource in curr_resources:  # Expand each instruction at the current level
            for i in range(num_dependents):
                dest_reg = RegisterManager.get()
                AR.generate(src=resource, dest=dest_reg, comment=f"using {resource} dependency")
                next_resources.append(dest_reg)
        curr_resources = next_resources # move to the next level
