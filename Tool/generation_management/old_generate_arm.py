import random
from typing import Optional, Any, List
from Externals.db_manager.models import Instruction
from Tool.asm_libraries.label import Label
from Tool.generation_management.generate import GeneratedInstruction
from Tool.generation_management.utils import map_inputs_to_operands
from Utils.APIs.choice import choice
# from Tool.frontend.sources_API import Sources
from Tool.memory_management.memory_memory import Memory
from Tool.state_management import get_current_state

import ast

def generate_arm(
        selected_instruction: Instruction,
        src: Any = None,
        dest: Any = None,
        comment: Optional[str] = None,
) -> List[GeneratedInstruction]: # some instances might require dynamic init

    current_state = get_current_state()
    RegisterManager = current_state.register_manager

    instruction_comment = comment
    instruction_list = [] # some instances might require dynamic init

    # convert the operand from a string into a list of operands
    if isinstance(selected_instruction.operands, str):
        selected_instruction.operands = ast.literal_eval(selected_instruction.operands)

    print(f"selected_instruction: {selected_instruction}")
    # set True or False if one of the operands has memory type
    memory_usage = any(operand['type'] == "mem" for operand in selected_instruction.operands)
    if memory_usage:
        '''
        For every memory usage, we will plant a dynamic_init instruction to place that memory address in a temp register
        this is done to avoid using memories offset due to their formatting requirements and my lack of knowledge.
        '''
        print(f"memory_usage!!! selected_instruction: {selected_instruction.mnemonic}")
        if src is not None and isinstance(src, Memory):
            memory_operand = src
        elif dest is not None and isinstance(dest, Memory):
            memory_operand = dest
        else:
            # TODO:: add logic to calculate alignment based on the instruction, operand size, etc.
            memory_operand = Memory(shared=True, alignment=3)

        # setting an address register to be used as part of the dynamic_init if a memory operand is used
        dynamic_init_memory_address_reg = RegisterManager.get_and_reserve()
        comment = f"dynamic init: loading {dynamic_init_memory_address_reg} for next instruction"
        if memory_operand.reused_memory:
            comment = f"dynamic init: loading {dynamic_init_memory_address_reg} with reused memory {memory_operand.unique_label} for next instruction"

        dynamic_init_instruction = GeneratedInstruction(mnemonic='ldr', operands=[dynamic_init_memory_address_reg, f"={memory_operand._memory_initial_seed_id}"], comment=comment)

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
            eval_operand = RegisterManager.get()
        elif operand['type'] == "imm":
            optional_number = generate_random_immediate_for_instruction(selected_instruction.mnemonic)
            if optional_number is None:
                size_in_bits = int(operand['size'])
                # Calculate the maximum value based on the given bit size
                #max_value = (1 << size_in_bits) - 1  # This is 2^bits - 1
                max_value = (1 << 12) - 1  # This is 2^12 - 1
                eval_operand = random.randint(0, max_value)
                #eval_operand = f"#{hex(random.randint(0, max_value))}"
            else:
                eval_operand = optional_number
                #eval_operand = f"#{hex(optional_number)}"

        elif operand['type'] == "mem":
            # For every memory usage, we will plant a dynamic_init instruction to place that memory address in a temp register
            # this is done to avoid using memories offset due to their formatting requirements and my lack of knowledge.
            # TODO:: need to improve that logic and integrate offset allocation and avoid dynamic_init where possible!
            eval_operand = memory_operand.format_reg_as_label(dynamic_init_memory_address_reg)
        elif operand['type'] == "label":
            eval_operand = Label(postfix=f"generate")
        elif operand['type'] == "condition":
            random_condition = choice(values=["EQ","LT","LE","GT","GE"]) # NEQ create invalid condition?
            eval_operand = random_condition
        else:
            raise ValueError(f"invalid operand type {operand['type']} at selected instruction {selected_instruction.mnemonic}")

        evaluated_operands.append(eval_operand)
        op_location += 1

    gen_instruction = GeneratedInstruction(mnemonic=selected_instruction.mnemonic, operands=evaluated_operands, comment=instruction_comment)
    instruction_list.append(gen_instruction)

    if memory_usage:
        RegisterManager.free(dynamic_init_memory_address_reg)

    return instruction_list


def generate_random_immediate_for_instruction(mnemonic:str):
    # Handle common cases for ARM AArch64 instructions (ORR, AND, EOR, MOV, etc.)

    if mnemonic in ['ORR', 'AND', 'EOR', 'MOV']:
        # For ORR, AND, EOR, MOV, generate a 12-bit value and rotate it
        base_immediate = random.randint(0, 0xFFF)  # 12-bit value (0 to 4095)
        rotation = random.randint(0, 31)  # Rotate between 0 and 31
        # Apply the rotation and make sure it fits within a 32-bit word
        rotated_immediate = (base_immediate << rotation) & 0xFFFFFF
        return rotated_immediate

    if mnemonic in ['ROR']:
        # For ROR value, range is between 0 to 63
        rotated_immediate = random.randint(0, 63)  # Rotate between 0 and 31
        return rotated_immediate

    elif mnemonic in ['LSL', 'LSR', 'ASR']:
        # For shift instructions, generate a shift value (0-31)
        shift_value = random.randint(0, 31)  # Shift value between 0 and 31
        return shift_value

    elif mnemonic == 'MOVK':
        # MOVK (move constant to a register) has different behavior, valid 16-bit halfword immediate
        immediate = random.randint(0, 0xFFFF)  # 16-bit value
        return immediate

    elif mnemonic == 'MOVZ':
        # MOVZ (move zero-extended) has a 16-bit immediate
        immediate = random.randint(0, 0xFFFF)  # 16-bit value
        return immediate

    elif mnemonic == 'LDR' or mnemonic == 'STR':
        # For LDR and STR, you can use a valid address (for example, 4-byte aligned)
        # We will return an example address (e.g., aligned 4-byte address)
        address = random.randint(0, 0xFFFFFFFF) & ~0x3  # Ensure the address is 4-byte aligned
        return address

    else:
        return None
