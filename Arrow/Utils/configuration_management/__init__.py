from Arrow.Utils.configuration_management.configuration_management import get_config_manager
from Arrow.Utils.configuration_management.knob_manager import get_knob_manager
from Arrow.Utils.configuration_management.knobs import Knobs


class Configuration:
    from Arrow.Utils.configuration_management.enums import Architecture, Memory_types, Page_types, Page_sizes, ByteSize, Tag, Priority, PRIORITY_WEIGHTS, Frequency, Execution_context
    from Arrow.Tool.asm_libraries.trickbox.trickbox_fields import TrickboxRegister
    from Arrow.Tool.asm_libraries.sysreg.sysreg_fields import SystemRegister, SystemRegisterBitField


    Architecture = Architecture
    Memory_types = Memory_types
    Page_types = Page_types
    Page_sizes = Page_sizes
    ByteSize = ByteSize
    Tag = Tag
    Priority = Priority
    PRIORITY_WEIGHTS = PRIORITY_WEIGHTS
    Frequency = Frequency
    Execution_context = Execution_context
    TrickboxRegister = TrickboxRegister
    SystemRegister = SystemRegister
    SystemRegisterBitField = SystemRegisterBitField

    Knobs = Knobs()
