import random
from typing import Optional, Any, List
from Externals.db_manager.models import Instruction
from Arrow.Tool.generation_management.generate import GeneratedInstruction
from Arrow.Tool.generation_management.utils import map_inputs_to_operands
from Arrow.Tool.state_management import get_state_manager
from Arrow.Tool.memory_management.memory_operand import Memory
import ast

def generate_riscv(
        selected_instruction: Instruction,
        src: Any = None,
        dest: Any = None,
        comment: Optional[str] = None,
) -> List[GeneratedInstruction]: # some instances might require dynamic init
    '''
    RISC-V learning:
    - In the ISA-DB, we joined the two memory operands offset(base_reg) as a single "offset_plus_basereg" operand
        Instruction Format Consistency:
        In RISC-V, all load and store instructions that access memory follow the same format: offset(base_reg).
        There’s no concept of accessing memory without specifying both an offset and a base register.
        No Complex Addressing Modes:
        Unlike some other architectures, RISC-V does not have complex memory addressing modes, such as indexed or scaled addressing (like base + index * scale + offset found in x86).
        RISC-V memory addressing is intentionally kept simple to improve instruction decoding and reduce hardware complexity.
    - In Most of the memory usages, the Tool will plant a dynamic_init instruction to place that memory address in a temp register
        this is done to avoid using memories offset due to their formatting requirements and my lack of knowledge.
    - In RISC-V register, the registers are always accessed as full-width entities (e.g., x1 is always treated as a full 32-bit or 64-bit register).
        Instructions like ADD and ADDW determine how much of the register's data to operate on, but they always store the result in the full register.
        There are no sub-registers or overlapping regions like RAX/EAX/AX/AL in x86.
    '''

    state_manager = get_state_manager()
    current_state = state_manager.get_active_state()

    instruction_comment = comment
    instruction_list = [] # some instances might require dynamic init

    # convert the operand from a string into a list of operands
    if isinstance(selected_instruction.operands, str):
        selected_instruction.operands = ast.literal_eval(selected_instruction.operands)

    # set True or False if one of the operands has memory type
    memory_usage = any(operand['type'] == "offset_plus_basereg" for operand in selected_instruction.operands)
    if memory_usage:
        if src is not None and isinstance(src, Memory):
            memory_operand = src
        elif dest is not None and isinstance(dest, Memory):
            memory_operand = dest
        else:
            memory_operand = Memory(shared=True)

        # setting an address register to be used as part of the dynamic_init if a memory operand is used
        dynamic_init_memory_address_reg = current_state.register_manager.get_and_reserve()

        comment = f"dynamic init: loading {dynamic_init_memory_address_reg} for next instruction"
        if memory_operand.reused_memory:
            comment = f"dynamic init: loading {dynamic_init_memory_address_reg} with reused memory {memory_operand.memory_block.unique_label} for next instruction"

        dynamic_init_instruction = GeneratedInstruction(mnemonic='la', operands=[dynamic_init_memory_address_reg, memory_operand.memory_block.unique_label], comment=comment)
        instruction_list.append(dynamic_init_instruction)

    src_location, dest_location = map_inputs_to_operands(selected_instruction, src, dest)

    # evaluate operands
    evaluated_operands = []
    op_location = 0
    for operand in selected_instruction.operands:
        if src_location == op_location:
            if isinstance(src, Memory):
                eval_operand = memory_operand.format_reg_as_label(dynamic_init_memory_address_reg)
            else:
                eval_operand = src
        elif dest_location == op_location:
            if isinstance(dest, Memory):
                eval_operand = memory_operand.format_reg_as_label(dynamic_init_memory_address_reg)
            else:
                eval_operand = dest
        elif operand['type'] == "reg":
            eval_operand = current_state.register_manager.get()
        elif operand['type'] == "imm":
            random_imm = generate_random_imm_with_size(operand['size'])
            eval_operand = random_imm
        elif operand['type'] == "offset_plus_basereg":
            # For every memory usage, we will plant a dynamic_init instruction to place that memory address in a temp register
            # this is done to avoid using memories offset due to their formatting requirements and my lack of knowledge.
            # TODO:: need to improve that logic and integrate offset allocation and avoid dynamic_init where possible!
            eval_operand = memory_operand.format_reg_as_label(dynamic_init_memory_address_reg)
        elif operand['type'] == "offset_imm":
            eval_operand = random.randint(0, 100)
        else:
            raise ValueError(f"invalid operand type {operand['type']} at selected instruction {selected_instruction.mnemonic}")

        evaluated_operands.append(eval_operand)
        op_location += 1

    gen_instruction = GeneratedInstruction(mnemonic=selected_instruction.mnemonic, operands=evaluated_operands, comment=instruction_comment)
    instruction_list.append(gen_instruction)

    if memory_usage:
        current_state.register_manager.free(dynamic_init_memory_address_reg)

    return instruction_list


def generate_random_imm_with_size(size_description):
    """
    Generates a random number based on the given size description.
    The size description should be in the form of '<bit>_bit_<signed/unsigned>'.
    Example: '5_bit_unsigned', '12_bit_signed'.

    Parameters:
    size_description (str): The size description to parse, like '5_bit_unsigned', '12_bit_signed'

    Returns:
    int: A random integer within the specified range.
    """

    # Extract the number of bits and whether it's signed or unsigned
    size_parts = size_description.lower().split('_')
    bits = int(size_parts[0])  # First part is the bit size

    # TODO:: fix this workaround!!
    # TODO:: fix this workaround!!
    # TODO:: fix this workaround!!
    # There might be an issue with the assembler RARS I'm using
    # 12-bit unsigned should ranges from 0-0xfff, yet for some reason, instructions that exceed 0x7ff failed "0x800": Unsigned value is too large to fit into a sign-extended immediate
    # 20-bit signed should ranges is huge, yet "auipc t0, -0x800" passes while "auipc t0, -0x801" fails on "-0x801": operand is out of range
    # so, as a work-around, if bits is larger then 10, I'm setting it to 10
    # TODO:: need to check why is that and refactor this code
    if bits > 10:
        bits = 10
    # TODO:: fix this workaround!!
    # TODO:: fix this workaround!!
    # TODO:: fix this workaround!!

    is_signed = True if size_parts[-1] == 'signed' else False  # Last part indicates whether it's signed or unsigned

    if is_signed:
        # Signed range: -(2^(n-1)) to (2^(n-1) - 1)
        min_val = -(2 ** (bits - 1))
        max_val = (2 ** (bits - 1)) - 1
    else:
        # Unsigned range: 0 to (2^n - 1)
        min_val = 0
        max_val = (2 ** bits) - 1

    # Return a random value within the computed range
    return random.randint(min_val, max_val)
