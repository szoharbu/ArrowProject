import os
import random
from typing import Optional, Any, List, Dict
from Arrow.Tool.generation_management.utils import get_operand_type
from Arrow.Tool.generation_management.generated_instruction import GeneratedInstruction
from Arrow.Tool.generation_management.generate_x86 import generate_x86
from Arrow.Tool.generation_management.generate_riscv import generate_riscv
#from Arrow.Tool.generation_management.generate_arm import old_generate_arm
from Arrow.Tool.generation_management.generate_arm_asl import generate_arm_asl
from Arrow.Utils.configuration_management import Configuration, get_config_manager
from Externals.db_manager.models import get_instruction_db
from Arrow.Tool.register_management.register import Register
from Arrow.Tool.memory_management.memory_operand import Memory

from peewee import Expression, fn


# @staticmethod
def generate(
        instruction_count: Optional[int] = 1,
        query: Optional[Expression | Dict] = None,
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

    config_manager = get_config_manager()
    instruction_debug_prints = config_manager.get_value('Instruction_debug_prints')
    if instruction_debug_prints:
        print(f"--------------------- generate -------------------------")

    # Get optimized database connection (handles ARM ASL case automatically)
    db_models = get_instruction_db()
    
    if isinstance(db_models, dict):
        # ARM ASL case - returns dict with Instruction and Operand
        Instruction = db_models['Instruction']
        Operand = db_models['Operand']
    else:
        # Standard case - returns Instruction model only
        Instruction = db_models
        Operand = None

    # Start with a base query for instructions
    query_filter = Instruction.select()

    # # Print all instructions
    # query_filter = query_filter[20:30]
    # for instr in list(query_filter):
    #     print(f"   Instruction: {instr.syntax}")
    #     # Sort the operands list by index
    #     sorted_operands = sorted(instr.operands, key=lambda op: op.index)
    #     for op in sorted_operands:
    #         if op.index != -1:
    #             print(f"     Operand{op.index}: text: {op.text}, Category: {op.type_category}, Index: {op.index}, Type: {op.type}, Role: {op.role}, Size: {op.size}, Width: {op.width} ")
    #         else:
    #             print(f"     attribute: text: {op.text}, Category: {op.type_category}, Type: {op.type}, Role: {op.role}, Size: {op.size}, Width: {op.width} ")
    # exit()

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
    if src is not None:
        query_filter = add_operand_filter(query_filter, src, role="src", Instruction=Instruction, Operand=Operand)
    if dest is not None:
        query_filter = add_operand_filter(query_filter, dest, role="dest", Instruction=Instruction, Operand=Operand)

    instruction_count_in_db = query_filter.count()
    if instruction_count_in_db == 0:
        raise ValueError("No instructions found matching the specified criteria.")

    instruction_list = []
    for _ in range(instruction_count):
        # Use database OFFSET to get a random instruction (including invalid ones)
        # Try up to 10 times to find a valid instruction (same retry logic as before)
        selected_instruction = None
        for attempt in range(15):
            random_offset = random.randint(0, instruction_count_in_db - 1)
            candidate_instruction = query_filter.offset(random_offset).limit(1).first()
           
            if candidate_instruction and candidate_instruction.is_valid:
                selected_instruction = candidate_instruction
                break
            elif candidate_instruction:
                # Log invalid instructions (same as original behavior)
                if instruction_debug_prints:
                    print(f"        ⚠️   Skipping instruction!!! instruction {candidate_instruction.syntax} is not parsed correctly yet.")
       
        if not selected_instruction:
            raise ValueError("No valid instructions found matching the specified criteria after multiple attempts.")

        # Generate the instruction based on architecture
        if Configuration.Architecture.x86:
            gen_instructions = generate_x86(selected_instruction, src, dest, comment=comment)
        elif Configuration.Architecture.riscv:
            gen_instructions = generate_riscv(selected_instruction, src, dest, comment=comment)
        elif Configuration.Architecture.arm:
            gen_instructions = generate_arm_asl(selected_instruction, src, dest, comment=comment)
        else:
            raise ValueError(f"Unknown Architecture requested")

        instruction_list.extend(gen_instructions)

    return instruction_list


def add_operand_filter(query_filter, operand, role, Instruction, Operand):
    """Add operand-based filters to the query using provided Instruction and Operand models"""

    config_manager = get_config_manager()
    instruction_debug_prints = config_manager.get_value('Instruction_debug_prints')

    if isinstance(operand, Register):
        if instruction_debug_prints:
            print(f"   Input parameter:: {operand}, role = {role}, type = {operand.type}")

        if operand.type == "sve_pred" and (int(operand.name[1:]) >= 8):
            # if type is of Predicate (P1-P16) and op.name is higher than P7, need to make sure we are querying for width of 4 and not 3. lower Predicates can have both width 3 and 4.
            # Then join Operand if not already joined, and add filters from Operand
            if Operand is None:
                raise ValueError("Operand model not available for sve_pred filtering")
                
            query_filter = query_filter.join(Operand).where(
                (Operand.role == role) &
                (Operand.type == "sve_pred") &
                (Operand.width == 4) &
                (Operand.is_memory == False)
            )
        elif operand.type == "gpr" or operand.type == "simdfp":
            # gpr - reg of type gpr can be used for various types of operands ("gpr_32", "gpr_64", "gpr_var"]
            # simdfp - reg of type simdfp can be used for various types of operands ("simdfp_scalar_128", "simdfp_scalar_16", "simdfp_scalar_32", "simdfp_scalar_64", "simdfp_scalar_8", "simdfp_scalar_var", "simdfp_vec"]
            query_filter = query_filter.where(
                ((Instruction.op1_role.contains(role)) & (Instruction.op1_type.startswith(operand.type)) & (Instruction.op1_ismemory == False)) |
                ((Instruction.op2_role.contains(role)) & (Instruction.op2_type.startswith(operand.type)) & (Instruction.op2_ismemory == False)) |
                ((Instruction.op3_role.contains(role)) & (Instruction.op3_type.startswith(operand.type)) & (Instruction.op3_ismemory == False)) |
                ((Instruction.op4_role.contains(role)) & (Instruction.op4_type.startswith(operand.type)) & (Instruction.op4_ismemory == False))
            )
        else:  # sve_reg , sev_pred
            query_filter = query_filter.where(
                ((Instruction.op1_role.contains(role)) & (Instruction.op1_type == operand.type) & (Instruction.op1_ismemory == False)) |
                ((Instruction.op2_role.contains(role)) & (Instruction.op2_type == operand.type) & (Instruction.op2_ismemory == False)) |
                ((Instruction.op3_role.contains(role)) & (Instruction.op3_type == operand.type) & (Instruction.op3_ismemory == False)) |
                ((Instruction.op4_role.contains(role)) & (Instruction.op4_type == operand.type) & (Instruction.op4_ismemory == False))
            )

    elif isinstance(operand, Memory):
        if instruction_debug_prints:
            print(f"   Input parameter:: {operand}, role = {role}, type = {type(operand)}")

        query_filter = query_filter.where(
            ((Instruction.op1_role.contains(role)) & (Instruction.op1_ismemory == True)) |
            ((Instruction.op2_role.contains(role)) & (Instruction.op2_ismemory == True)) |
            ((Instruction.op3_role.contains(role)) & (Instruction.op3_ismemory == True)) |
            ((Instruction.op4_role.contains(role)) & (Instruction.op4_ismemory == True))
        )

    return query_filter

