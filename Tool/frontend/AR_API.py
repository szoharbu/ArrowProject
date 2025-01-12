from typing import Union, List, Dict, Any, Optional
from Utils.logger_management import get_logger
from Utils.configuration_management import get_config_manager
from Tool.frontend import choice, asm_logger

class AR:
    logger = get_logger()
    logger.info("======================== AR_API")

    config_manager = get_config_manager()

    @staticmethod
    def asm(asm_code:str, comment:str=None):
        # Calls the internal Tool.asm yet expose to users as TG.asm API
        return asm_logger.AsmLogger.print_asm_line(asm_code, comment)

    @staticmethod
    def comment(comment:str):
        # Calls the internal Tool.choice yet expose to users as TG.comment API
        return asm_logger.AsmLogger.print_comment_line(comment)

    @staticmethod
    def choice(
            values: Union[Dict[Any, int], List[Any]],
            name: Optional[str] = None,
    ) -> Any:
        # Calls the internal Tool choice yet expose to users as TG.choice API
        return choice.choice(values, name)
