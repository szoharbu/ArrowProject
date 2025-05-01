import importlib.util
import sys
from ....Utils.configuration_management import get_config_manager
from ....Utils.logger_management import get_logger

def read_template():
    logger = get_logger()
    logger.info("============ read_template")
    config_manager = get_config_manager()
    template_path = config_manager.get_value('template_path')

    spec = importlib.util.spec_from_file_location("template_file", template_path)
    foo = importlib.util.module_from_spec(spec)
    sys.modules["template_file"] = foo
    spec.loader.exec_module(foo)

def read_inputs():
    logger = get_logger()
    logger.info("======== read_inputs")
    read_template()
