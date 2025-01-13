from Utils.logger_management import get_logger

def test_section():
    logger = get_logger()
    logger.info("======== body_section")
    #  the Body section will go over each of the cores, and will execute several scenarios.
    #  the code will switch between the different states every scenario execution

    from Submodules.content.templates.direct_template import content
    content()

    #do_boot()

    #do_body()

    #do_final()

