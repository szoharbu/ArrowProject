from peewee import Expression
from typing import Union, List, Dict, Any, Optional
from Utils.logger_management import get_logger
from Utils.configuration_management import get_config_manager
from Tool.generation_management.generate import GeneratedInstruction, generate as generate_wrapper
from Tool.memory_management.memory_segments import CodeSegment
from Tool.asm_libraries import label, asm_logger
from Tool.asm_libraries.branch_to_segment.branch_to_segment_base import BranchToSegmentBase
from Tool.asm_libraries.branch_to_segment.branch_to_segment import BranchToSegment as BranchToSegment_wrapper
from Tool.frontend import choice


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
    def Label(postfix: str):
        # Calls the internal Tool.Label yet expose to users as TG.Label API
        return label.Label(postfix)

    @staticmethod
    def choice(
            values: Union[Dict[Any, int], List[Any]],
            name: Optional[str] = None,
    ) -> Any:
        # Calls the internal Tool choice yet expose to users as TG.choice API
        return choice.choice(values, name)

    # @staticmethod
    def generate(
            instruction_count: Optional[int] = 1,
            query: Optional[Expression|Dict] = None,
            src: Any = None,
            dest: Any = None,
            comment: Optional[str] = None,
    ) -> List[GeneratedInstruction]:
        return generate_wrapper(instruction_count, query, src, dest, comment)

    @staticmethod
    def BranchToSegment(code_block: CodeSegment) -> BranchToSegmentBase:
        return BranchToSegment_wrapper(code_block)  # Return an instance of the branch_to_segment class