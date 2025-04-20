import random
import ast
from typing import Optional, Any, List
from Externals.db_manager.asl_testing.asl_models import Instruction
from Tool.asm_libraries.label import Label
from Tool.generation_management.generate import GeneratedInstruction
from Tool.generation_management.utils import map_inputs_to_operands
from Utils.APIs.choice import choice
# from Tool.frontend.sources_API import Sources
from Tool.memory_management.memory import Memory
from Tool.state_management import get_current_state
from Utils.configuration_management import get_config_manager


def generate_arm_asl(
        selected_instruction: Instruction,
        src: Any = None,
        dest: Any = None,
        comment: Optional[str] = None,
) -> List[GeneratedInstruction]:  # some instances might require dynamic init

    current_state = get_current_state()
    RegisterManager = current_state.register_manager
    config_manager = get_config_manager()

    instruction_comment = comment
    instruction_list = []  # some instances might require dynamic init

    # convert the operand from a string into a list of operands
    if isinstance(selected_instruction.operands, str):
        selected_instruction.operands = ast.literal_eval(selected_instruction.operands)

    debug_mode = config_manager.get_value('Debug_mode')
    if debug_mode:
        print(f"   Selected Instruction: {selected_instruction.syntax}")

    # Sort the operands list by index
    sorted_operands = sorted(selected_instruction.operands, key=lambda op: op.index)

    if debug_mode:
        for op in sorted_operands:
            op_info_str = f"text: {op.text}, Category: {op.type_category}, Type: {op.type}, Role: {op.role}, Size: {op.size}, Width: {op.width}, extensions: {op.extensions}, is_valid: {op.is_valid}"
            if op.is_operand:
                print(f"        - operand {op.index} : {op_info_str}")
                # if op.is_valid:
                #     print(f"        - valid operand {op.index} : {op_info_str}")
                # else:
                #     print(f"        - invalid operand {op.index} : {op_info_str}")
            else:
                print(f"        - attribute : {op_info_str}")

    # set True or False if one of the operands has memory type
    memory_usage = any(operand.type == "mem" for operand in selected_instruction.operands)
    if memory_usage:
        '''
        For every memory usage, we will plant a dynamic_init instruction to place that memory address in a temp register
        this is done to avoid using memories offset due to their formatting requirements and my lack of knowledge.
        '''
        if src is not None and isinstance(src, Memory):
            memory_operand = src
        elif dest is not None and isinstance(dest, Memory):
            memory_operand = dest
        else:
            memory_operand = Memory(shared=True)

        # setting an address register to be used as part of the dynamic_init if a memory operand is used
        dynamic_init_memory_address_reg = RegisterManager.get_and_reserve()
        comment = f"dynamic init: loading {dynamic_init_memory_address_reg} for next instruction"
        if memory_operand.reused_memory:
            comment = f"dynamic init: loading {dynamic_init_memory_address_reg} with reused memory {memory_operand.unique_label} for next instruction"

        dynamic_init_instruction = GeneratedInstruction(mnemonic='ldr', operands=[dynamic_init_memory_address_reg,
                                                                                  f"={memory_operand._memory_initial_seed_id}"],
                                                        comment=comment)

        instruction_list.append(dynamic_init_instruction)

    src_location, dest_location = map_inputs_to_operands(selected_instruction, src, dest)

    # evaluate operands
    evaluated_operands = []
    op_location = 1
    zdn_register = None
    extensions_index = None

    for op in sorted_operands:
        if not op.is_operand:
            continue
        if not op.is_valid:
            raise TypeError(f"Invalid operand type {op}, please check the instruction and operands in the database")
        if src_location == op_location:
            if debug_mode:
                print(f"   src_location == op_location == {op_location}")
            if isinstance(src, Memory):
                eval_operand = memory_operand.format_reg_as_label(dynamic_init_memory_address_reg)
            else:
                eval_operand = src.as_size(op.size)
                if debug_mode:
                    print(
                        f"    src is {src}, size is {op.size}, src.as_size(op.size): {src.as_size(op.size)}  ==> eval_operand: {eval_operand}")
        elif dest_location == op_location:
            if debug_mode:
                print(f"   dest_location == op_location == {op_location}")
            if isinstance(dest, Memory):
                eval_operand = memory_operand.format_reg_as_label(dynamic_init_memory_address_reg)
            else:
                eval_operand = dest.as_size(op.size)
                if debug_mode:
                    print(
                        f"    dest is {dest}, size is {op.size}, dest.as_size(op.size): {dest.as_size(op.size)}  ==> eval_operand: {eval_operand}")

        elif op.type_category == "register":
            if op.type == "reg" or "gpr_" in op.type:
                if op.type == "gpr_var":
                    size = random.choice([32, 64])
                    eval_operand = RegisterManager.get(reg_type="gpr").as_size(size)
                else:
                    eval_operand = RegisterManager.get(reg_type="gpr").as_size(op.size)
            elif "simdfp_scalar" in op.type:
                eval_operand = RegisterManager.get(reg_type="simdfp").as_size(op.size)
            elif "simdfp_vec" in op.type:
                eval_operand = RegisterManager.get(reg_type="simdfp").as_size(op.size)
            elif op.type == "sve_reg":
                eval_operand = RegisterManager.get(reg_type="sve_reg")
                if op.syntax == "Zdn":
                    if zdn_register is None:
                        # first time we see Zdn, we need to create a new register
                        zdn_register = eval_operand
                    else:
                        # we already have a Zdn register, we need to use the same one
                        eval_operand = zdn_register
            elif op.type == "sve_pred":
                if op.width == 4:
                    eval_operand = RegisterManager.get(reg_type="sve_pred")
                elif op.width == 3:
                    # if width is 3, we need to check if there are any free predicate registers available at the range of p0-p7
                    eval_operand = RegisterManager.get(reg_type="sve_pred_low")
                else:
                    raise ValueError(f"Invalid width for SVE predicate register: {op.width}")
            else:
                eval_operand = "UNKNOWN"

        elif op.type_category == "immediate":
            if op.width is not None:
                eval_operand = generate_random_immediate_based_in_width(op.width)
            else:
                eval_operand = "unknown"
        elif op.type == "mem":
            # For every memory usage, we will plant a dynamic_init instruction to place that memory address in a temp register
            # this is done to avoid using memories offset due to their formatting requirements and my lack of knowledge.
            # TODO:: need to improve that logic and integrate offset allocation and avoid dynamic_init where possible!
            eval_operand = memory_operand.format_reg_as_label(dynamic_init_memory_address_reg)
        elif op.type == "label":
            eval_operand = Label(postfix=f"generate")
        elif op.type == "condition":
            random_condition = choice(values=["EQ", "LT", "LE", "GT", "GE"])  # NEQ create invalid condition?
            eval_operand = random_condition
        else:
            eval_operand = "unknown"
            # raise ValueError(f"invalid operand type {operand.type} at selected instruction {selected_instruction.mnemonic}")

        # handle extensions
        if op.extensions != "[]":
            extensions = ast.literal_eval(op.extensions)
            if len(extensions) > 1:
                if extensions_index is None:
                    extensions_index = random.randint(0, len(extensions) - 1)
                eval_operand = f"{eval_operand}.{extensions[extensions_index]}"
            elif "SP" in op.extensions:
                if "31" in eval_operand:
                    # when asm_template contains <Xn|SP> , it means the register can be r0..30 or SP, r31 is not allowed
                    # in this logic, I just replace r31 with SP. #TODO:: need to replace with a smarter logic
                    eval_operand = RegisterManager.get(reg_type="gpr", reg_name="SP")
            else:
                eval_operand = f"{eval_operand}{extensions[0]}"

        evaluated_operands.append(eval_operand)
        op_location += 1

    gen_instruction = GeneratedInstruction(mnemonic=selected_instruction.mnemonic, operands=evaluated_operands,
                                           comment=instruction_comment)

    # print(f"    Generated Instruction: {gen_instruction}")

    if memory_usage:
        RegisterManager.free(dynamic_init_memory_address_reg)

    instruction_list.append(gen_instruction)

    return instruction_list


def generate_random_immediate_based_in_width(width: int):
    if width <= 0:
        raise ValueError("Bit width must be greater than 0")
    max_value = (1 << width) - 1  # Compute the maximum value for this bit width
    return random.randint(0, max_value)