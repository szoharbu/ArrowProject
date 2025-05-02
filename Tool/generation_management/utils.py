import random

from Utils.configuration_management import Configuration, get_config_manager
from Tool.memory_management.memory import Memory
from Tool.register_management.register import Register


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
        raise ValueError(f"Invalid operand type {type(operand)}")


def find_possible_locations(operands, role, type):
    """
    Find all valid locations to insert the new operand.
    Returns:
        list of int: List of valid indices where the operand can be placed.
    """
    possible_locations = []
    index = 1   # index start from 1 not 0
    for op in operands:
        #print(f'zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz op_type {op.type}, op_role {op.role}, op_memory_role {op.memory_role}, wanted_type {type}, wanted_role {role}')
        if not op.is_operand:
            continue

        if type == "mem" and op.is_memory:
            if (op.memory_role == "base"):
                # this initial code will only handle the base, and will try to set offset to zero!
                possible_locations.append(index)
        else:
            if (op.type == type) or (type == "gpr" and op.type.startswith("gpr")) or (type == "simdfp" and op.type.startswith("simdfp")):
                if (op.role == role) or (op.role == "src_dest" and (role == "src" or role == "dest")):
                    possible_locations.append(index)
        index += 1
    if not possible_locations:
        raise ValueError(f"Couldn't find possible location that match {role} {type} operand")
    else:
        config_manager = get_config_manager()
        debug_mode = config_manager.get_value('Debug_mode')
        if debug_mode:
            print(f"   find_possible_locations for {role} {type} operand: {possible_locations}")
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
        if isinstance(src, Memory): src.type = "mem"
        src_locations = find_possible_locations(selected_instruction.operands, role="src", type=src.type)
        src_location = random.choice(src_locations)
    if dest is not None:
        if isinstance(dest, Memory): dest.type = "mem"
        dest_locations = find_possible_locations(selected_instruction.operands, role="dest", type=dest.type)
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