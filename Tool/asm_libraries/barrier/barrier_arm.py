from Tool.asm_libraries.asm_logger import AsmLogger
from Tool.asm_libraries.label import Label
from Tool.state_management import get_current_state
from Tool.memory_management.memory import Memory
from Tool.asm_libraries.barrier.barrier_manager import get_barrier_manager

def barrier_arm(barrier_name: str):

    AsmLogger.comment(f"==== starting barrier sequence - {barrier_name} ====")

    current_state = get_current_state()
    register_manager = current_state.register_manager

    barrier_manager = get_barrier_manager()
    barrier = barrier_manager.request_barrier(barrier_name)
    barrier_nem = barrier.get_memory()

    reg1 = register_manager.get_and_reserve()
    reg2 = register_manager.get_and_reserve()
    reg3 = register_manager.get_and_reserve()
    # Get the current core ID
    AsmLogger.comment("Get the current core ID")
    AsmLogger.asm(f"mrs {reg1}, mpidr_el1")
    AsmLogger.asm(f"ubfx {reg1.as_size(32)}, {reg1.as_size(32)}, #0, #3", comment=f"Extract bits 0, 1 and 2 into w0")

    AsmLogger.comment("Calculate the bit position for this core")
    AsmLogger.asm(f"mov {reg2.as_size(32)}, #1")
    AsmLogger.asm(f"lsl {reg2.as_size(32)}, {reg2.as_size(32)}, {reg1.as_size(32)}", comment=f"w1 = 1 << core_id")

    AsmLogger.comment("Set this core's bit in the barrier vector (active low)")

    #TODO:: replace the below with an atomic operation

    AsmLogger.asm(f"adr {reg1}, {barrier_nem.unique_label}")
    AsmLogger.asm(f"ldr {reg3.as_size(32)}, [{reg1}]")
    AsmLogger.asm(f"bic {reg3.as_size(32)}, {reg3.as_size(32)}, {reg2.as_size(32)}", comment=f"Clear the bit")
    AsmLogger.asm(f"str {reg3.as_size(32)}, [{reg1}]")
    #AsmLogger.asm(f"ldclr {reg3.as_size(32)}, {reg2.as_size(32)}, [{reg1}]", comment=f"Atomic Load and Clear operation")


    spin_label = Label("spin_label")
    AsmLogger.comment("Spin until all bits are clear (active low)")
    AsmLogger.asm(f"{spin_label}:")
    AsmLogger.asm(f"ldr {reg3.as_size(32)}, {barrier_nem.unique_label}")
    AsmLogger.asm(f"cbnz {reg3.as_size(32)}, {spin_label}", comment=f"Continue spinning if any bit is set")

    AsmLogger.comment("Barrier reached - all cores have arrived")
    AsmLogger.comment(f"==== finished barrier sequence - {barrier_name} ====")