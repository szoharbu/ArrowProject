

from Utils.configuration_management import Configuration, get_config_manager
config_manager = get_config_manager()

# Check if not already set from command-line
if not config_manager.is_exist("Architecture"):
    config_manager.set_value("Architecture", "riscv")
Configuration.Knobs.Config.core_count.set_value(1)