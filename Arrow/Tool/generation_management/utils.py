import random

from Arrow.Utils.configuration_management import Configuration
from Arrow.Tool.memory_management.memory import Memory
from Arrow.Tool.register_management.register import Register


def print_instruction(selected_instruction):
    print(f"Mnemonic: {selected_instruction.mnemonic}, Operands: {selected_instruction.operands}, "
          f"random_generate: {selected_instruction.random_generate}, architecture_modes: {selected_instruction.architecture_modes}, "
          f"Type: {selected_instruction.type_}, Group: {selected_instruction.group}, "
          f"Description: {selected_instruction.description}, Syntax: {selected_instruction.syntax}")

def get_operand_type(operand):
    """
    Maps the given operand to its type
    """
    if isinstance(operand, Memory):
        if Configuration.Architecture.riscv:
            return "offset_plus_basereg"
        else:
            return "mem"
    elif isinstance(operand, Register):
        return "reg"
    elif isinstance(operand, int):
        return "imm"
    else:
        raise ValueError("Invalid operand type")


def find_possible_locations(operands, role, type):
    """
    Find all valid locations to insert the new operand.
    Returns:
        list of int: List of valid indices where the operand can be placed.
    """
    possible_locations = []
    for i, op in enumerate(operands):
        if (op['type'] == type) and (op['role'] == role):
            possible_locations.append(i)
    if not possible_locations:
        raise ValueError(f"Couldn't find possible location that match {role} {type} operand")
    else:
        return possible_locations


def map_inputs_to_operands(selected_instruction, src, dest):
    '''
    In this section, we map src/dest inputs into relevant operands.
    The Instruction.Query have already filtered irrelevant entries and kept just the possible ones that match the input requirements,
    The below code will place them as part of the instruction generation.
    '''
    src_location = None
    dest_location = None
    if src is not None:
        src_locations = find_possible_locations(selected_instruction.operands, role="src", type=get_operand_type(src))
        src_location = random.choice(src_locations)
    if dest is not None:
        dest_locations = find_possible_locations(selected_instruction.operands, role="dest",
                                                 type=get_operand_type(dest))
        dest_location = random.choice(dest_locations)
    if dest is not None and src is not None:
        # if both src/dest input was provided, need to make sure they dont targeting the same operand
        random.shuffle(dest_locations)
        random.shuffle(src_locations)
        src_location = None
        dest_location = None
        # Assign locations without overlap
        for loc1 in src_locations:
            for loc2 in dest_locations:
                if loc1 != loc2:
                    src_location = loc1
                    dest_location = loc2
                    break
        if src_location is None or dest_location is None:
            raise ValueError(f"no valid non-overlapping locations were found")

    return src_location, dest_location