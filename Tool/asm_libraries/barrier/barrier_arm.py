from Tool.asm_libraries.asm_logger import AsmLogger
from Tool.asm_libraries.label import Label
from Tool.state_management import get_current_state
from Tool.memory_management.memory_memory import Memory
from Tool.asm_libraries.barrier.barrier_manager import get_barrier_manager

def barrier_arm(barrier_name: str):

    AsmLogger.comment(f"==== starting barrier sequence - {barrier_name} ====")

    current_state = get_current_state()
    register_manager = current_state.register_manager

    barrier_manager = get_barrier_manager()
    barrier = barrier_manager.request_barrier(barrier_name)
    barrier_mem = barrier.get_memory()

    reg1 = register_manager.get_and_reserve()
    reg2 = register_manager.get_and_reserve()
    reg3 = register_manager.get_and_reserve()
    # Get the current core ID from MPIDR_EL1
    AsmLogger.asm(f"mrs {reg1}, mpidr_el1")
    
    # Create a simple sequential core ID mapping for this 4-core system:
    # 0x81000000 -> 0, 0x81000001 -> 1, 0x81010000 -> 2, 0x81010001 -> 3
    
    # Extract Aff0 (core within cluster) - bits [7:0]
    AsmLogger.asm(f"and {reg2.as_size(32)}, {reg1.as_size(32)}, #0xff", comment="Extract Aff0 (core within cluster)")
    
    # Extract Aff2 (cluster ID) - bits [23:16] 
    AsmLogger.asm(f"lsr {reg3}, {reg1}, #16", comment="Shift right by 16 to get Aff2 in lower bits")
    AsmLogger.asm(f"and {reg3.as_size(32)}, {reg3.as_size(32)}, #0xff", comment="Extract Aff2 (cluster ID)")
    
    # Create sequential core ID: (cluster_id * 2) + core_in_cluster
    # This gives: cluster0_core0=0, cluster0_core1=1, cluster1_core0=2, cluster1_core1=3
    AsmLogger.asm(f"lsl {reg3.as_size(32)}, {reg3.as_size(32)}, #1", comment="cluster_id * 2 (2 cores per cluster)")
    AsmLogger.asm(f"add {reg1.as_size(32)}, {reg2.as_size(32)}, {reg3.as_size(32)}", comment="sequential_core_id = core_in_cluster + (cluster_id * 2)")

    AsmLogger.comment("Calculate the bit position for this core")
    AsmLogger.asm(f"mov {reg2.as_size(32)}, #1")
    AsmLogger.asm(f"lsl {reg2.as_size(32)}, {reg2.as_size(32)}, {reg1.as_size(32)}", comment=f"w1 = 1 << unique_core_id")

    AsmLogger.comment("Set this core's bit in the barrier vector (active low)")

    #TODO:: replace the below with an atomic operation

    #AsmLogger.asm(f"adr {reg1}, {barrier_mem.get_label()}")
    #AsmLogger.asm(f"adrp {reg1}, {barrier_mem.get_label()}", comment=f"Get page address (±4GB range)")
    #AsmLogger.asm(f"add {reg1}, {reg1}, :lo12:{barrier_mem.get_label()}", comment=f"Add page offset")
    # Modify the below with PC-relative literal loads
    AsmLogger.asm(f"ldr {reg1}, ={barrier_mem.get_label()}")
    AsmLogger.asm(f"stclr {reg2.as_size(32)}, [{reg1}]")

    spin_label = Label("spin_label")
    AsmLogger.comment("Spin until all bits are clear (active low)")
    AsmLogger.asm(f"{spin_label}:")
    #AsmLogger.asm(f"ldr {reg3.as_size(32)}, {barrier_mem.get_label()}")
    AsmLogger.asm(f"ldr {reg3.as_size(32)}, [{reg1}]")
    AsmLogger.asm(f"cbnz {reg3.as_size(32)}, {spin_label}", comment=f"Continue spinning if any bit is set")

    AsmLogger.comment("Barrier reached - all cores have arrived")
    AsmLogger.comment(f"==== finished barrier sequence - {barrier_name} ====")

    register_manager.free(reg1)
    register_manager.free(reg2)
    register_manager.free(reg3)