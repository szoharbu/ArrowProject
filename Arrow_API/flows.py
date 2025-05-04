from peewee import Expression
from typing import Union, List, Dict, Any, Optional, Tuple
from Utils.logger_management import get_logger
from Utils.configuration_management import Configuration
from Tool.generation_management.generate import GeneratedInstruction, generate as generate_wrapper
from Tool.register_management.register import Register
from Tool.memory_management.memory_segments import CodeSegment
from Utils.APIs import choice, range_with_peak, adaptive_choice
from Tool.asm_libraries import label, asm_logger, stack, store_value
from Tool.asm_libraries.memory_array.memory_array import MemoryArray as MemoryArray_wrapper
from Tool.asm_libraries.loop.loop_base import LoopBase
from Tool.asm_libraries.loop.loop import Loop as Loop_wrapper
from Tool.asm_libraries.branch_to_segment.branch_to_segment_base import BranchToSegmentBase
from Tool.asm_libraries.branch_to_segment.branch_to_segment import BranchToSegment as BranchToSegment_wrapper
from Tool.asm_libraries.event_trigger.event_trigger_base import EventTriggerBase
from Tool.asm_libraries.event_trigger.event_trigger import EventTrigger as EventTrigger_wrapper
from Tool.asm_libraries.barrier.barrier import Barrier as Barrier_wrapper
from Tool.state_management.switch_state import SwitchState as SwitchState_wrapper

class AR:
    logger = get_logger()
    logger.info("======================== AR_API")

    from Tool.decorators.scenario_decorator import scenario_decorator
    from Tool.ingredient_management.ingredient import Ingredient
    from Tool.decorators.ingredient_decorator import ingredient_decorator

    # Instruction query
    asl_extract = True # TODO:: remove this after testing!!!!
    if Configuration.Architecture.arm and asl_extract:
        from Externals.db_manager.asl_testing.asl_models import Instruction
    else:
        from Externals.db_manager.models import Instruction

    @staticmethod
    def asm(asm_code:str, comment:str=None):
        # Calls the internal Tool.asm yet expose to users as TG.asm API
        return asm_logger.AsmLogger.asm(asm_code, comment)

    @staticmethod
    def comment(comment:str):
        # Calls the internal Tool.choice yet expose to users as TG.comment API
        return asm_logger.AsmLogger.comment(comment)

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

    @staticmethod
    def rangeWithPeak(start:int, end: int, peak: int, peak_width='normal')-> int:
        # Calls the internal Tool rangeWithPeak yet expose to users as TG.choice API
        return range_with_peak.rangeWithPeak(start, end, peak, peak_width)

    @staticmethod
    def adaptive_choice(values: Dict[Any, Union[int, Tuple[int, int]]]) -> Any:
        """
        Public API for adaptive_choice. Delegates to AdaptiveChoiceManager.
        """
        adaptive_choice_manager = adaptive_choice.get_adaptive_choice_manager()
        return adaptive_choice_manager.adaptive_choice(values)


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
    def SwitchState(
            state_name: str,
    ):
        return SwitchState_wrapper(state_name)

    @staticmethod
    def Loop(
            counter: int,
            counter_type: Optional[str] = None,
            counter_direction: Optional[str] = None,
            label: Optional[str] = None,
            additional_param: Optional[int] = None
    ) -> LoopBase:
        return Loop_wrapper(counter, counter_type,counter_direction,label)  # Return an instance of the loop class

    @staticmethod
    def EventTrigger(
            frequency: Configuration.Frequency = Configuration.Frequency.LOW,
    ) -> EventTriggerBase:
        return EventTrigger_wrapper(frequency)  # Return an instance of the loop class

    @staticmethod
    def MemoryArray(
            array_name:str,
            elements:any,
            element_size=4):
        return MemoryArray_wrapper(array_name, elements, element_size)  # Return an instance of the loop class

    @staticmethod
    def BranchToSegment(code_block: CodeSegment) -> BranchToSegmentBase:
        return BranchToSegment_wrapper(code_block)  # Return an instance of the branch_to_segment class

    @staticmethod
    def Barrier(barrier_name: str):
        return Barrier_wrapper(barrier_name)  # Return an instance of the barrier class

    @staticmethod
    def store_value_into_register(register: Register, value: int) -> None:
        # Calls the internal store_value yet expose to users as TG.store_value API
        return store_value.store_value_into_register(register, value)

    @staticmethod
    class Stack:
        @staticmethod
        def push(register_list: List[Register], comment:str=None) -> None:
            # Generate push assembly code for the given registers.
            return stack.Stack.push(register_list, comment)

        @staticmethod
        def pop(register_list: List[Register], comment:str=None) -> None:
            # Generate pop assembly code for the given registers.
            return stack.Stack.pop(register_list, comment)

        @staticmethod
        def read(offset, register, comment:str=None) -> None:
            # Generate push assembly code for the given registers.
            return stack.Stack.read(offset, register, comment)

        @staticmethod
        def write(offset, register, comment:str=None) -> None:
            # Generate pop assembly code for the given registers.
            return stack.Stack.write(offset, register, comment)