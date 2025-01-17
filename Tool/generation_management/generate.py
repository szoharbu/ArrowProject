import random
from typing import Optional, Any, List, Dict
from Tool.generation_management.utils import get_operand_type
from Tool.generation_management.generated_instruction import GeneratedInstruction
from Tool.generation_management.generate_x86 import generate_x86
from Tool.generation_management.generate_riscv import generate_riscv
from Tool.generation_management.generate_arm import generate_arm
from Utils.configuration_management import Configuration
from Externals.db_manager.models import get_instruction_db
from peewee import Expression, fn

# @staticmethod
def generate(
        instruction_count: Optional[int] = 1,
        query: Optional[Expression|Dict] = None,
        src: Any = None,
        dest: Any = None,
        comment: Optional[str] = None,
) -> List[GeneratedInstruction]:
    """
    Generates an instruction with the given mnemonic and operands.

    Parameters:
    - instruction_count (int) : number of instructions to generate.
    - query (Optional[Expression|Dict]) : Peewee query from instructions.db
    - mnemonic (str): The mnemonic of the instruction.
    - src,dest: optional operands for the instruction.
    - comment (str): postfix comment.

    Returns:
    - Instruction: The generated instruction.
    """

    # Get the bound Instruction model
    Instruction = get_instruction_db()

    # Start with a base query for instructions
    query_filter = Instruction.select()

    # Filter out all random_generate=False instructions
    query_filter = query_filter.where(Instruction.random_generate == True)

    # If query is an existing Expression or dict, add it to the query_filter
    if query:
        if isinstance(query, Expression):
            # If query is a single expression, apply it directly
            query_filter = query_filter.where(query)
        elif isinstance(query, dict):
            # If query is a dictionary, construct conditions from key-value pairs
            for key, value in query.items():
                if hasattr(Instruction, key):
                    query_filter = query_filter.where(getattr(Instruction, key) == value)
        else:
            raise ValueError("Invalid query format. Expected Expression or dict.")


    # Add operand-based filters (if provided)
    operands = []
    if src is not None:
        operands.append(("src", get_operand_type(src)))
    if dest is not None:
        operands.append(("dest", get_operand_type(dest)))

    for operand_role,operand_type in operands:
        query_filter = query_filter.where(
            fn.json_valid(Instruction.operands) & (
                    ((fn.json_extract(Instruction.operands, '$[0].type') == operand_type) &
                     (fn.json_extract(Instruction.operands, '$[0].role') == operand_role)) |
                    ((fn.json_extract(Instruction.operands, '$[1].type') == operand_type) &
                     (fn.json_extract(Instruction.operands, '$[1].role') == operand_role)) |
                    ((fn.json_extract(Instruction.operands, '$[2].type') == operand_type) &
                     (fn.json_extract(Instruction.operands, '$[2].role') == operand_role))
            )
        )
        # for inst in list(query_filter):
        #     print_instruction(inst)

    # Fetch all matching instructions and select one at random
    instructions = list(query_filter)

    if not instructions:
        raise ValueError("No instructions found matching the specified criteria.")

    instruction_list = []
    for _ in range(instruction_count):
        selected_instruction = random.choice(instructions)

        #print_instruction(selected_instruction)

        if Configuration.Architecture.x86:
            gen_instructions = generate_x86(selected_instruction, src, dest, comment=comment)
        elif Configuration.Architecture.riscv:
            gen_instructions = generate_riscv(selected_instruction, src, dest, comment=comment)
        elif Configuration.Architecture.arm:
            gen_instructions = generate_arm(selected_instruction, src, dest, comment=comment)
        else:
            raise ValueError(f"Unknown Architecture requested")

        instruction_list.extend(gen_instructions)

    return instruction_list

