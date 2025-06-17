from Arrow.Utils.configuration_management import Configuration, get_config_manager
from Arrow.Utils.logger_management import get_logger

from Arrow.Tool.stages.test_stage import test_boot, test_body, test_final

def test_section():
    logger = get_logger()
    logger.info("======== body_section")
    #  the Body section will go over each of the cores, and will execute several scenarios.
    #  the code will switch between the different states every scenario execution

    test_boot.do_boot()

    test_body.do_body()

    test_final.do_final()

