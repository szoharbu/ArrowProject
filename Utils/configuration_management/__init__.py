from Utils.configuration_management.configuration_management import get_config_manager
from Utils.configuration_management.knob_manager import get_knob_manager
from Utils.configuration_management.knobs import Knobs


class Configuration:
    from Utils.configuration_management.enums import Architecture, Memory_types, ByteSize, Tag, Priority, PRIORITY_WEIGHTS, Frequency

    Architecture = Architecture
    Memory_types = Memory_types
    ByteSize = ByteSize
    Tag = Tag
    Priority = Priority
    PRIORITY_WEIGHTS = PRIORITY_WEIGHTS
    Frequency = Frequency

    Knobs = Knobs()



