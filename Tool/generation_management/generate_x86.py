import random
from typing import Optional, Any, List
from Tool.db_manager.models import Instruction
from Tool.generation_management.generate import GeneratedInstruction
from Tool.generation_management.utils import map_inputs_to_operands
from Tool.frontend.sources_API import Sources
import ast

def generate_instruction_x86(
        selected_instruction: Instruction,
        src: Any = None,
        dest: Any = None,
        comment: Optional[str] = None,
) -> List[GeneratedInstruction]: # some instances might require dynamic init

    instruction_comment = comment
    instruction_list = [] # some instances might require dynamic init

    # convert the operand from a string into a list of operands
    if isinstance(selected_instruction.operands, str):
        selected_instruction.operands = ast.literal_eval(selected_instruction.operands)

    src_location, dest_location = map_inputs_to_operands(selected_instruction, src, dest)

    # evaluate operands
    evaluated_operands = []
    op_location = 0
    for operand in selected_instruction.operands:
        if src_location == op_location:
            eval_operand = src
        elif dest_location == op_location:
            eval_operand = dest
        elif operand['type'] == "reg":
            eval_operand = Sources.RegisterManager.get()
        elif operand['type'] == "imm":
            eval_operand = random.randint(0, 100000)
        elif operand['type'] == "mem":
            eval_operand = Sources.Memory(shared=True)
        else:
            raise ValueError(f"invalid operand type {operand['type']} at selected instruction {selected_instruction.mnemonic}")

        evaluated_operands.append(eval_operand)
        op_location += 1

    gen_instruction = GeneratedInstruction(mnemonic=selected_instruction.mnemonic, operands=evaluated_operands, comment=instruction_comment)

    instruction_list.append(gen_instruction)

    return instruction_list
