
from ....Tool.asm_libraries.event_trigger.event_trigger_base import EventTriggerBase
from ....Tool.asm_libraries.event_trigger.event_trigger_x86 import EventTrigger_x86
from ....Tool.asm_libraries.event_trigger.event_trigger_riscv import EventTrigger_riscv
from ....Tool.asm_libraries.event_trigger.event_trigger_arm import EventTrigger_arm
from ....Utils.configuration_management import Configuration

def EventTrigger(
        frequency: Configuration.Frequency = Configuration.Frequency.LOW,
) -> EventTriggerBase:
    """Configure Loop with the desired architecture (Arm, riscv, x86)."""

    if Configuration.Architecture.x86:
        ET_instance = EventTrigger_x86
    elif Configuration.Architecture.riscv:
        raise ValueError((f"Functionality not implemented yet for {Configuration.Architecture.arch_str}"))
        # ET_instance = EventTrigger_riscv
    elif Configuration.Architecture.arm:
        ET_instance = EventTrigger_arm
    else:
        raise ValueError(f"Unknown Architecture requested")

    return ET_instance(frequency)  # Return an instance of the event_trigger class

