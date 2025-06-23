import random
from Arrow.Arrow_API import AR
from Arrow.Arrow_API.resources.memory_manager import MemoryManager_API as MemoryManager
from Arrow.Arrow_API.resources.register_manager import RegisterManager_API as RegisterManager
from Arrow.Utils.configuration_management import Configuration

@AR.scenario_decorator(random=True, priority=Configuration.Priority.MEDIUM) # , tags=[Configuration.Tag.???])
def ldstcc_release_rar_check():
    barrier_label = AR.Label(postfix="sync_barrier")

    mem0 = MemoryManager.Memory(init_value=0x1234, cross_core=True, alignment=3)
    mem1 = MemoryManager.Memory(init_value=0x5678, cross_core=True, alignment=3)

    with AR.SwitchState(state_name="core_0"):
        AR.Barrier(barrier_label)
        for _ in range(10):
            AR.generate(query=(AR.Instruction.mnemonic.contains("ldsetal")), src=mem0)
            AR.generate(query=(AR.Instruction.mnemonic.contains("ldr")), src=mem1)

    with AR.SwitchState(state_name="core_1"):
        AR.Barrier(barrier_label)
        for _ in range(10):
            AR.generate(query=(AR.Instruction.mnemonic.contains("stlr")), src=mem1)
            AR.generate(query=(AR.Instruction.mnemonic.contains("ldar")), src=mem0)