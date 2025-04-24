import os
import random
from typing import Optional, Any, List, Dict
from Tool.generation_management.utils import get_operand_type
from Tool.generation_management.generated_instruction import GeneratedInstruction
from Tool.generation_management.generate_x86 import generate_x86
from Tool.generation_management.generate_riscv import generate_riscv
from Tool.generation_management.generate_arm import generate_arm
from Tool.generation_management.generate_arm_asl import generate_arm_asl
from Utils.configuration_management import Configuration, get_config_manager
from Externals.db_manager.models import get_instruction_db
from Tool.register_management.register import Register
from Tool.memory_management.memory import Memory

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
    debug_mode = config_manager.get_value('Debug_mode')
    if debug_mode:
        print(f"--------------------- generate -------------------------")

    asl_extract = True  # TODO:: remove this after testing!!!!
    if Configuration.Architecture.arm and asl_extract:
        from Externals.db_manager.asl_testing import asl_models
        from peewee import SqliteDatabase

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(base_dir, '..', 'Externals', 'db_manager', 'db', 'arm_instructions_isalib.db')

        # Check if the file exists
        if not os.path.exists(db_path):
            raise ValueError(f"SQL DB file not found: {db_path}")

        sql_db = SqliteDatabase(db_path)
        asl_models.Instruction._meta.database = sql_db
        asl_models.Operand._meta.database = sql_db

        sql_db.connect()
        Instruction = asl_models.Instruction
        Operand = asl_models.Operand
    else:
        # Get the bound Instruction model
        Instruction = get_instruction_db()

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
        # query_filter = query_filter.where(Instruction.mnemonic.contains("mul"))
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
        query_filter = add_operand_filter(query_filter, src, role="src")

    if dest is not None:
        query_filter = add_operand_filter(query_filter, dest, role="dest")

    # Fetch all matching instructions and select one at random
    instructions = list(query_filter)

    if not instructions:
        raise ValueError("No instructions found matching the specified criteria.")

    instruction_list = []
    for _ in range(instruction_count):

        # selected_instruction = random.choice(instructions)

        # modify the logic from a random choice the below logic that will select the first valid instruction, as at this stage the ASL parser is not 100% reliable
        # TODO:: remove this after the ASL parser is 100% reliable

        # print(f"   Selecting a valid instruction from {len(instructions)} instructions")
        random.shuffle(instructions)

        selected_instruction = None
        for instruction in instructions:
            if instruction.is_valid:
                selected_instruction = instruction
                break
            # else:
            #     print(f"        ⚠️   Skipping instruction!!! instruction {instruction.syntax} is not parsed correctly yet.")

        if selected_instruction is None:
            raise ValueError("No valid instructions found matching the specified criteria.")

        # print_instruction(selected_instruction)

        if Configuration.Architecture.x86:
            gen_instructions = generate_x86(selected_instruction, src, dest, comment=comment)
        elif Configuration.Architecture.riscv:
            gen_instructions = generate_riscv(selected_instruction, src, dest, comment=comment)
        elif Configuration.Architecture.arm and asl_extract:
            gen_instructions = generate_arm_asl(selected_instruction, src, dest, comment=comment)
        elif Configuration.Architecture.arm:
            gen_instructions = generate_arm(selected_instruction, src, dest, comment=comment)
        else:
            raise ValueError(f"Unknown Architecture requested")

        instruction_list.extend(gen_instructions)

    return instruction_list


def add_operand_filter(query_filter, operand, role):

    asl_extract = True  # TODO:: remove this after fixing this code!!!!
    if Configuration.Architecture.arm and asl_extract:
        from Externals.db_manager.asl_testing import asl_models
        from peewee import SqliteDatabase

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(base_dir, '..', 'Externals', 'db_manager', 'db', 'arm_instructions_isalib.db')

        # Check if the file exists
        if not os.path.exists(db_path):
            raise ValueError(f"SQL DB file not found: {db_path}")

        sql_db = SqliteDatabase(db_path)
        asl_models.Instruction._meta.database = sql_db
        asl_models.Operand._meta.database = sql_db

        sql_db.connect()
        Instruction = asl_models.Instruction
        Operand = asl_models.Operand
    else:
        # Get the bound Instruction model
        Instruction = get_instruction_db()

    # for instr in query:
    #     print(f"    Instruction: {instr.unique_id} | {instr.mnemonic} | {instr.syntax} ")
    #     extracted_operands = Operand.select().where(Operand.instruction == instr)
    #     for op in extracted_operands:
    #         print(f"      name: {op.name}, index: {op.index}, Text: {op.text}, Type: {op.type}, Role: {op.role}, Size: {op.size} ")
    # print(f"Total instructions before filter:  { len(query_filter)}")

    config_manager = get_config_manager()
    debug_mode = config_manager.get_value('Debug_mode')


    if isinstance(operand, Register):
        if debug_mode:
            print(f"   Input parameter:: {operand}, role = {role}, type = {operand.type}")

        if operand.type == "sve_pred" and (int(operand.name[1:]) >= 8):
            # if type is of Predicate (P1-P16) and op.name is higher than P7, need to make sure we are querying for width of 4 and not 3. lower Predicates can have both width 3 and 4.
            # Then join Operand if not already joined, and add filters from Operand

            query_filter = query_filter.join(Operand).where(
                (Operand.role == role) &
                (Operand.type == "sve_pred") &
                (Operand.width == 4)
            )
        elif operand.type == "gpr" or operand.type == "simdfp":
            # gpr - reg of type gpr can be used for various types of operands ("gpr_32", "gpr_64", "gpr_var"]
            # simdfp - reg of type simdfp can be used for various types of operands ("simdfp_scalar_128", "simdfp_scalar_16", "simdfp_scalar_32", "simdfp_scalar_64", "simdfp_scalar_8", "simdfp_scalar_var", "simdfp_vec"]


            query_filter = query_filter.where(
                ((Instruction.op1_role.contains("src")) & (Instruction.op1_type.startswith(operand.type))) |
                ((Instruction.op2_role.contains("src")) & (Instruction.op2_type.startswith(operand.type))) |
                ((Instruction.op3_role.contains("src")) & (Instruction.op3_type.startswith(operand.type))) |
                ((Instruction.op4_role.contains("src")) & (Instruction.op4_type.startswith(operand.type)))
            )

        else:  # sve_reg , sev_pred
            query_filter = query_filter.where(
                ((Instruction.op1_role.contains("src")) & (Instruction.op1_type == operand.type)) |
                ((Instruction.op2_role.contains("src")) & (Instruction.op2_type == operand.type)) |
                ((Instruction.op3_role.contains("src")) & (Instruction.op3_type == operand.type)) |
                ((Instruction.op4_role.contains("src")) & (Instruction.op4_type == operand.type))
            )

    elif isinstance(operand, Memory):
        if debug_mode:
            print(f"   Input parameter:: {operand},role = {role}, {type(operand)}")

        query_filter = query_filter.where(
            ((Instruction.op1_role.contains("src")) & (Instruction.op1_ismemory)) |
            ((Instruction.op2_role.contains("src")) & (Instruction.op2_ismemory)) |
            ((Instruction.op3_role.contains("src")) & (Instruction.op3_ismemory)) |
            ((Instruction.op4_role.contains("src")) & (Instruction.op4_ismemory))
        )

    return query_filter
