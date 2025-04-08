import os
import re
import yaml
from typing import List
from Externals.db_manager.asl_testing.asl_models import Instruction, Operand, db, initialize_db


def reset_database():
    """Drops existing tables and recreates them to ensure schema consistency."""
    db.drop_tables([Instruction, Operand])  # Drop old tables
    db.create_tables([Instruction, Operand])  # Recreate tables
    print("Database tables reset to match the latest schema.")


####################################################################################################################### Operand Class

class Operand_class:
    def __init__(self, ast_data=None, var_encode_data=None):
        """
        Initialize an Operand object.

        :param ast_text: Operand identifier as appeared in the asm_template (e.g., Xd, Vm, Wn)
        :param var_encode_text: operand text as appeared in the Var_encoding (e.g., Rd, Rm, Rn)
        :param index: Operand index (1, 2, 3, 4) or -1 for non Operands entries (e.g., Q, size)
        :param syntax: Syntax representation (e.g., X0, V1)
        :param size: Operand size (e.g., 32, 64)
        :param hibit: High bit position
        :param width: Bit width
        :param encode: Encoding pattern
        :param cnt: Register count
        :param r31: Special register condition
        :param type: Register type (e.g., gpr_64)
        :param type_category: Register type (e.g., register, immediate)
        :param role: Similar to "use" field, with slight adjustments and more common name
        """
        self.ast_text = "unknown"
        self.var_encode_text = "unknown"
        self.index = -1
        self.syntax = "unknown"
        self.size = None
        self.hibit = None
        self.width = None
        self.encode = ""
        self.cnt = 1
        self.r31 = "N/A"
        self.type = "unknown"
        self.type_category = "unknown"
        self.role = "unknown"
        self.extensions = []  # List of extensions
        self.is_operand = True  # Flag to indicate if Operand came from ast_operands or just a data field from var_encoding
        self.is_valid = True  # Flag to indicate if the Operand is valid or still contain unknown values

        if var_encode_data:
            for key, val in var_encode_data.items():
                if key == "text":
                    key = "var_encode_text"  # Rename field
                if hasattr(self, key):  # only set if the attribute is defined
                    setattr(self, key, val)

        if ast_data:
            for key, val in ast_data.items():
                if hasattr(self, key):  # only set if the attribute is defined
                    setattr(self, key, val)

        if ast_data is None:
            self.is_operand = False

        if var_encode_data is None or ast_data is None:
            self.is_valid = False

        # print(f"       - Operand init: {self}")

    def set(self, key, value):
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            raise AttributeError(f"Unknown attribute: {key}")

    def __str__(self):
        attrs = vars(self)  # returns the object's __dict__
        return f"{self.__class__.__name__}({', '.join(f'{k}={v}' for k, v in attrs.items())})"

    # def to_dict(self):
    #     """
    #     Convert the Operand object to a dictionary.
    #
    #     :return: Dictionary representation of the Operand
    #     """
    #     return {
    #         "ast_text": self.ast_text,
    #         "var_encode_text": self.var_encode_text,
    #         "index": self.index,
    #         "syntax": self.syntax,
    #         "size": self.size,
    #         "hibit": self.hibit,
    #         "width": self.width,
    #         "encode": self.encode,
    #         "cnt": self.cnt,
    #         "r31": self.r31,
    #         "type": self.type,
    #         "type_category": self.type_category,
    #         "role": self.role,
    #     }


#
######################################################################################################################## asm_template parsing


def parse_asmtemplate(asm_template):
    """
    Consume asm_template and return a list of clean operands and extra info. like:
        - asm template : ADD <Vd>.<T>, <Xn|SP>{, <Vm>.<T>}
            - operand1 : Vd      extra info: contain T
            - operand2 : Xn      extra info: contain SP
            - operand3 : Vm      extra info: contain T, optional

    """
    clean_asm_template = re.sub(r"\s+", " ", asm_template).strip()
    print(f"    - asm template : {clean_asm_template} ")

    # Step 1: Extract the mnemonic (first word before a space)
    parts = clean_asm_template.split(" ", 1)
    mnemonic = parts[0]

    # If there are no operands, return early
    if len(parts) == 1:
        return []

    operands_str = parts[1]  # Everything after the mnemonic

    # Step 2: Handle the special case of [], like `ZA.<T>[<Wv>, <offs>{, VGx2}]`
    # Convert "[...]" into "[unknown]" # TODO:: need to handle later
    operands_str = re.sub(r"\[.*?\]", "[unknown]", operands_str)

    # Step 3: Handle the special case `{, op3}` -> `, {op3}`
    # Convert "{, " into ",{"
    operands_str = re.sub(r"{,\s*", ",{", operands_str)

    # Step 4: Split operands while keeping all symbols (except commas)
    # This ensures {op3} is treated as one operand
    operands = re.split(r",\s*", operands_str)

    operands_data = []
    index = 0
    for op in operands:
        clean_op = op
        extensions = []
        index += 1
        # Check if the operand is fully wrapped in {}
        match = re.fullmatch(r"\{(.*)\}", clean_op)
        if match:
            clean_op = match.group(1)  # Extract the content inside {}
            # optional = True  # Mark as optional
            extensions.append("optional")

        clean_op = re.sub(r"[{}<>]", "", clean_op)

        # Check if the operand ends with .<T> .D /P ...
        # match = re.fullmatch(r"(.+?)(?:\.(\w+)|\.\<(\w+)\>|/(\w+)|\|(\w+)|\[(.+)\])?", clean_op)
        match = re.fullmatch(r"(.+?)(?:(\.\w+)|(\.\<\w+\>)|(/\w+)|(\|\w+)|(\[.+\]))?", clean_op)
        if match:
            clean_op = match.group(1)
            for i in range(2, 7):
                if match.group(i) is not None:
                    extensions.append(match.group(i))

        new_operand = {
            "ast_text": op,
            "clean_name": clean_op,
            "index": index,
            "extensions": extensions,
        }
        operands_data.append(new_operand)

    return operands_data


####################################################################################################################### var_encode parsing

def assign_operand_category(operand, yaml_entry):
    '''
    Classify operands into "register", "immediate", or "unknown"
    Possible operand types:
    'imm19', 'imm5', 'sz', 'scale', 'immlo', 'Rt2', 'Xn', 'V', 'b5', 'imm7', 'shift', 'Rs', 'Pm',
    'immr', 'Zn', 'i3h', 'uimm6', 'Rv', 'imm6', 'Zm', 'Rd', 'tszh', 'imm4', 'imm12', 'i4', 'off3',
    'i3', 'Q', 'tsize', 'S', 'hw', 'o0', 'L', 'Zdn', 'sh', 'Rt', 'imm13', 'off2', 'immh', 'xs',
    'N', 'Rm', 'op2', 'a', 'Pn', 'imm9h', 'Rn', 'Pd', 'Xm', 'CRm', 'simm7', 'size', 'i1', 'i2h',
    'imm2', 'i2', 'imm16', 'imm8', 'Pg', 'i4h', 'op1', 'imm26', 'imm9', 'imm8h'
    '''

    if operand["type"] != "N/A":
        # this mean reg_info is available
        operand["type_category"] = "register"
    elif "imm" in operand["text"]:
        operand["type_category"] = "immediate"
    else:
        operand["type_category"] = "unknown"

    # Adding "role" while keeping the original "use", with slight naming adjustment dest instead of dst
    if operand["use"] == "dst":
        operand["role"] = "dest"
    elif operand["use"] == "src":
        operand["role"] = "src"
    elif operand["use"] == "src_dst":
        operand["role"] = "src_dest"

    print(
        f"          - updating type_category of type {operand["type"]} to '{operand["type_category"]}' category, and role to '{operand["role"]}'")

    yaml_entry["type_category"] = operand["type_category"]
    yaml_entry["role"] = operand["role"]


def assign_operand_size(operand, yaml_entry):
    """
    Assigns a size field to an operand based on its type and size.
    """

    # Possible types are: gpr_32, gpr_64, gpr_var, simdfp_scalar_128, simdfp_scalar_16, simdfp_scalar_32, simdfp_scalar_64, simdfp_scalar_8, simdfp_scalar_var, simdfp_vec, sve_pred, sve_reg

    def check_substring(strings, substring):
        return any(substring in s for s in strings)

    optional_names = [operand["type"], operand["text"]]
    if check_substring(optional_names, "128"):
        operand["size"] = 128
    if check_substring(optional_names, "64"):
        operand["size"] = 64
    elif check_substring(optional_names, "32"):
        operand["size"] = 32
    # elif "16" in optional_names:
    elif check_substring(optional_names, "16"):
        operand["size"] = 16
    elif check_substring(optional_names, "8"):
        operand["size"] = 8
    elif "simdfp" in operand["type"]:  # default operand size in Olympus
        operand["size"] = 128
    elif "sve_reg" in operand["type"]:  # default operand size in Olympus
        operand["size"] = 128
    elif "sve_pred" in operand["type"]:  # default operand size in Olympus
        operand["size"] = 16
    elif "imm" in operand["text"]:
        operand["size"] = operand["width"]
    else:
        operand["size"] = None

    print(f"          - updating size of type {operand["type"]} to '{operand["size"]}'")
    yaml_entry["size"] = operand["size"]


def assign_operand_syntax_name(operand, yaml_entry):
    """
    Assigns a syntax field to an operand based on its type and size.
    """
    # Possible types are: gpr_32, gpr_64, gpr_var, simdfp_scalar_128, simdfp_scalar_16, simdfp_scalar_32, simdfp_scalar_64, simdfp_scalar_8, simdfp_scalar_var, simdfp_vec, sve_pred, sve_reg

    syntax = "unknown"  # Default value

    if operand["type"].startswith("gpr"):  # gpr_32, gpr_64, gpr_var
        match = re.fullmatch(r"R(\w+)", operand["text"])
        if match:
            reg_num = match.group(1)
            if operand["size"] == 64:
                syntax = f"X{reg_num}"  # 64-bit GPR → Xi
            elif operand["size"] == 32:
                syntax = f"W{reg_num}"  # 32-bit GPR → Wi
            elif operand["type"] == "gpr_var":
                syntax = f"X{reg_num}_or_W{reg_num}"  # Variable-sized GPR -> Xi or Wi
        else:
            syntax = operand["text"]  # Special registers like SP, LR, etc.

    elif operand["type"].startswith(
            "simdfp"):  # simdfp_scalar_128, simdfp_scalar_16, simdfp_scalar_32, simdfp_scalar_64, simdfp_scalar_8, simdfp_scalar_var, simdfp_vec
        match = re.fullmatch(r"R(\w+)", operand["text"])
        if match:
            reg_num = match.group(1)
            if operand["size"] == 128:
                syntax = f"V{reg_num}"  # 128-bit SIMD → Vi
            elif operand["size"] == 64:
                syntax = f"D{reg_num}"  # 64-bit SIMD → Di
            elif operand["size"] == 32:
                syntax = f"S{reg_num}"  # 32-bit SIMD → Si
            elif operand["size"] == 16:
                syntax = f"H{reg_num}"  # 16-bit SIMD → Hi
            elif operand["size"] == 8:
                syntax = f"B{reg_num}"  # 8-bit SIMD → Bi
        else:
            syntax = operand["text"]  # Special registers like SP, LR, etc.

    elif operand["type"].startswith("sve"):  # sve_pred, sve_reg
        syntax = operand["text"]  # Not sure SVE needs conversion.
        # match = re.fullmatch(r"R(\w+)", operand["text"])
        # if match:
        #   ...
        # else:
        #     syntax = operand["text"]  # Special registers like SP, LR, etc.
    elif operand["text"].startswith("imm"):
        syntax = operand["text"]

    operand["syntax"] = syntax
    print(f"          - updating syntax from '{operand["text"]}' to '{operand["syntax"]}'")
    yaml_entry["syntax"] = operand["syntax"]


def extract_var_encode(inst_data):
    var_encode_data = []
    var_encode = inst_data.get("var_encode", {})
    if var_encode is not None:
        for operand_text, operand_info in var_encode.items():
            var_encode_entry = {
                "text": operand_text,  # Operand identifier (Rd, Rm, Rn)
                "syntax": "",  # Syntax representation (e.g., X0, V1)
                "hibit": operand_info.get("hibit", None),  # High bit position
                "width": operand_info.get("width", None),  # Bit width
                "encode": operand_info.get("encode", ""),  # Encoding pattern
                "cnt": operand_info.get("reginfo", {}).get("cnt", 1),  # Register count
                "r31": operand_info.get("reginfo", {}).get("r31", "N/A"),  # Special register condition
                "type": operand_info.get("reginfo", {}).get("type", "N/A"),  # Register type (e.g., gpr_64)
                "use": operand_info.get("reginfo", {}).get("use", "N/A"),  # Operand role (dst, src)
                "role": "N/A",  # Similar to "use" field, with slight adjustments and more common name
                # Similar to 'use' both more common name, keeping also the original 'use' name
            }
            var_encode_data.append(var_encode_entry)

            print(f"       - var_encode_entry: {var_encode_entry["text"]}")
            assign_operand_category(var_encode_entry, operand_info)
            assign_operand_size(var_encode_entry, operand_info)
            assign_operand_syntax_name(var_encode_entry, operand_info)

    return var_encode_data


####################################################################################################################### Constraints parsing
def extract_aligned_options(constraint_block):
    """
    Extracts aligned label options from a YAML-style constraint block.

    This function parses multiple constraint groups, each containing a list of entries
    with a 'label' and exactly one integer-like field (e.g., 'size', 'sz', 'Q', 'option', etc).
    The goal is to identify corresponding label values across groups based on their shared key values.

    The function supports two cases:
    1. Aligned constraints: All groups use the same key name (e.g., 'size') and share key values.
       In this case, label lists are returned in a shared, aligned order based on the key.
    2. Non-alignable or cross-key constraints (e.g., one uses 'size' and the other 'Q') are skipped,
       and the function raises a ValueError.

    Returns:
        A dictionary mapping group names (with "_options" suffix) to lists of labels, ordered
        by shared key values across all groups.

    Raises:
        ValueError: If a group contains more than one int-like key, uses inconsistent keys internally,
                    or groups can't be aligned due to mismatched or missing key values.

    TODO:: need to add support for more cases.
    """
    import collections

    label_map = {}  # group_name -> {key_name, ordered list of (key_value, label)}

    for group_name, group_data in constraint_block.items():
        constraints = group_data.get("constraints", [])
        key_to_label = {}

        key_name = None
        for entry in constraints:
            label = entry.get("label")
            if not label:
                continue

            # Find int-valued keys (excluding 'boolean', etc.)
            int_keys = [k for k, v in entry.items()
                        if k not in ("label", "boolean") and isinstance(v, int)]

            print(f"zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz  int_keys: {int_keys}")
            if len(int_keys) != 1:
                raise ValueError(f"Group '{group_name}' must have exactly one int-valued key, got: {int_keys}")

            current_key = int_keys[0]
            value = entry[current_key]

            if key_name is None:
                key_name = current_key
            elif key_name != current_key:
                raise ValueError(f"Group '{group_name}' uses inconsistent keys: {key_name} vs {current_key}")

            key_to_label[value] = label

        label_map[group_name] = {"key_name": key_name, "entries": key_to_label}
        print(f"zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz  label_map: {label_map}")

    # Determine alignment strategy
    all_keys = [v["key_name"] for v in label_map.values()]
    shared_key = all_keys[0]

    if not all(k == shared_key for k in all_keys):
        raise ValueError(f"Inconsistent keys across groups: {all_keys}")

    # Collect all unique key values
    all_key_values = set()
    for v in label_map.values():
        all_key_values.update(v["entries"].keys())

    # Create aligned lists
    result = {}
    for group_name, info in label_map.items():
        entries = info["entries"]
        aligned = []
        for k in sorted(all_key_values):
            if k not in entries:
                raise ValueError(f"Missing value {k} in group '{group_name}'")
            aligned.append(entries[k])
        result[f"{group_name}_options"] = aligned

    return result


def extract_constraints(inst_data):
    '''
    Constraints group: T : B → { size: 0 }, H → { size: 1 }, S → { size: 10 }, D → { size: 11 }
    Constraints group: shift : LSL → { shift: 0 }, LSR → { shift: 1 }, ASR → { shift: 10 }
    '''
    aligned_options = {}
    constraint_groups = inst_data.get("constraint", {})

    if constraint_groups:
        try:
            # Code that might raise an exception
            aligned_options = extract_aligned_options(constraint_groups)
        except Exception as e:
            # Code to handle the exception
            print(f"extract_constraints:: error: {e}")
            return False, {}

        print(f"aligned_options: {aligned_options}")

    return True, aligned_options


####################################################################################################################### full operand parsing


# Function to extract Operands information from Yaml
def extract_operands(inst_data):
    success = True
    # extract operands from the asm_templates
    asm_template_operands_data = parse_asmtemplate(inst_data.get("asmtemplate", ""))
    var_encode_data = extract_var_encode(inst_data)
    success_constraints, constraints_data = extract_constraints(inst_data)

    success = success and success_constraints  # accumulate successes or failure as you go

    operands_data: List[Operand_class] = []
    if asm_template_operands_data:  # if asm_template_operands_data is not empty
        asm_template_operands_data.sort(key=lambda op: op["index"])
        for asmt_op in asm_template_operands_data:
            # print(operand)
            match = False
            for var in var_encode_data:
                if asmt_op["clean_name"] == var["syntax"]:
                    operand_entry = Operand_class(ast_data=asmt_op, var_encode_data=var)
                    operands_data.append(operand_entry)
                    match = True
                    break
                elif "imm" in asmt_op["clean_name"] and "imm" in var["syntax"]:
                    # In ARM AArch64, most instruction with immediate will have immX, some will have immr, imms, or both.
                    # These imm require special calculation logic, which I skip implementing at this early stage. # TODO:: need to eventually model it
                    # FYI, there are some cases (~5) when immr and imms are used together in an instruction, which require "logical immediate"
                    operand_entry = Operand_class(ast_data=asmt_op, var_encode_data=var)
                    if var["text"] == "imms" or var["text"] == "immr":
                        operand_entry.set("is_valid", False)
                    match = True
                    operands_data.append(operand_entry)
                    break

            if not match:
                operand_entry = Operand_class(ast_data=asmt_op)
                operand_entry.set("is_valid", False)
                operands_data.append(operand_entry)
                #    raise ValueError(f"Operand {asmt_op['clean_name']} not found in var_encode_data")

    # Identify unmatched items from the var_encode_data
    # Extract existing syntaxes from operands_list
    existing_syntaxes = {operand.syntax for operand in operands_data}
    # Extract vars that do not exist in the operands_list based on the 'syntax' field
    non_matching_vars = [var for var in var_encode_data if var['syntax'] not in existing_syntaxes]

    for var in non_matching_vars:
        operand_entry = Operand_class(var_encode_data=var)
        operand_entry.set("index", -1)
        operand_entry.set("is_valid", False)
        operand_entry.set("is_operand", False)

        operands_data.append(operand_entry)

    # handle extensions field
    for op in operands_data:

        if op.extensions and constraints_data:  # if both extensions and constraints_data are not None
            processed_list = [item.lstrip('.') + '_options' for item in op.extensions]
            for item in processed_list:  # Process the list to match dictionary keys
                if item in constraints_data:
                    print(
                        f"          - updating extensions of {op.syntax} from '{op.extensions}' to '{constraints_data[item]}'")
                    op.set("extensions", constraints_data[item])
                    break  # Stops after finding the first match

        # if ".Tb" in op.extensions or ".Ta" in op.extensions:
        #     # In Arm, there is a special case when T and Tb/Ta are used, and it require special referencing to the size filed
        #     # I will skip implementing that logic at this early stage. # TODO:: need to eventually model it
        #     op.set("is_valid", False)
        # if op.type == "simdfp_scalar_var":
        #     # Here's a summary of the register mapping:
        #     #   32 x 128-bit SIMD registers (v0 to v31)
        #     #      - Can be used for SIMD operations (NEON and Advanced SIMD instructions)
        #     #      - Can be used for double-precision floating-point operations (d0 to d15)
        #     #      - Can be used for single-precision floating-point operations (s0 to s15)
        #     # TODO:: this require additional logic which not yet implemented, so I will skip it for now .
        #     op.set("is_valid", False)

    operands_data.sort(key=lambda op: op.index)

    return success, operands_data


# Function to extend operands and upload basic fields into Instruction object, like src1, src2, dest1. They will be added to Instruction entry to reduce usage of join queries.
def extended_operands(operands_data):
    """Extracts up to 4 source and 2 destination operands explicitly."""

    # Initialize variables with default values
    src1_type, src2_type, src3_type, src4_type = None, None, None, None
    src1_size, src2_size, src3_size, src4_size = None, None, None, None
    dest1_type, dest2_type = None, None
    dest1_size, dest2_size = None, None

    src_index = 1
    dest_index = 1

    for op in operands_data:
        # op_type = operand['type']
        # op_role = operand['role']
        # op_size = operand['size']

        if op.role == "src" or op.role == "src_dest":
            if src_index == 1:
                src1_type, src1_size = op.type, op.role
            elif src_index == 2:
                src2_type, src2_size = op.type, op.role
            elif src_index == 3:
                src3_type, src3_size = op.type, op.role
            elif src_index == 4:
                src4_type, src4_size = op.type, op.role
            src_index += 1

        elif op.role == "dest" or op.role == "src_dest":
            if dest_index == 1:
                dest1_type, dest1_size = op.type, op.size
            elif dest_index == 2:
                dest2_type, dest2_size = op.type, op.size
            dest_index += 1

    return {
        "src1_type": src1_type, "src1_size": src1_size,
        "src2_type": src2_type, "src2_size": src2_size,
        "src3_type": src3_type, "src3_size": src3_size,
        "src4_type": src4_type, "src4_size": src4_size,
        "dest1_type": dest1_type, "dest1_size": dest1_size,
        "dest2_type": dest2_type, "dest2_size": dest2_size,
    }


def populate_database(yaml_dict, force_reset=False):
    """
    Populates the database with instruction data.
    """
    if force_reset:
        reset_database()

    # Insert data into SQLite using a transaction
    with db.atomic():

        for inst_id, inst_data in yaml_dict.items():
            print(f"--------------------------------------------- Processing: {inst_id} ")

            asm_template = inst_data.get("asmtemplate", "")  # Assume one ASM_templates per entry

            is_instruction_valid = True  # this flag will be passed on to inner function, and will be used to determine if the instruction is valid, instead of raising an exception. # TODO:: need to improve that logic

            # Extract ASL encoding details
            asl_data = inst_data.get("asl", {})
            if asl_data is not None:
                encoding_name = asl_data.get("encoding_name", "N/A")
                # iform = asl_data.get("iform", "N/A")
                iformid = asl_data.get("iformid", "N/A").replace(".xml", "")

            # Extract USL data
            usl_data = inst_data.get("usl", {})
            if usl_data is not None:
                usl_flow = usl_data.get("flow", "N/A")
                steering_classes_list = usl_data.get("steering", [])
            else:
                # The current behavior is that if usl_data is not found, that instruction is NOT part of Olympus, and so we skip the instruction
                print(f"     - Skipping instruction: {inst_id} due to missing usl data")

                continue

                usl_flow = "N/A"
                steering_classes_list = []

            unique_id = inst_id

            # Extract and insert operands
            success, operands_data = extract_operands(inst_data)

            if not success:
                is_instruction_valid = False
                print(f"zzzzzzzzzzzz  Invalid instruction: {inst_id}")
            for op in operands_data:
                if op.is_operand and not op.is_valid:
                    is_instruction_valid = False
                    print(f"zzzzzzzzzzzz  Invalid instruction: {inst_id}")

            instr_extended_operands = extended_operands(operands_data)

            print(f"    - syntax: {asm_template}")
            for op in operands_data:
                if op.is_operand:
                    if op.is_valid:
                        print(f"        - valid operand {op.index} : {op}")
                    else:
                        print(f"        - invalid operand {op.index} : {op}")
                else:
                    print(f"        - attribute : {op}")

            # Insert instruction
            instruction = Instruction.create(
                unique_id=unique_id,
                id=inst_id,
                syntax=asm_template,
                description=inst_data.get("description", "no description"),
                mnemonic=inst_data.get("mnemonic", "").lower(),
                instr_class=inst_data.get("instr_class", "no description"),
                feature=inst_data.get("feature", "None"),
                iformid=iformid,
                usl_flow=usl_flow,
                # mop_count=usl_data.get("mop_count"),
                # table_name=usl_data.get("table_name"),
                # max_latency=max_latency,
                steering_class=str(steering_classes_list),
                is_valid=is_instruction_valid,
                **instr_extended_operands
            )

            # Handle random_generate flag
            instruction.random_generate = inst_data.get("random_generate", "True") == "True"
            instruction.save()

            for operand in operands_data:
                Operand.create(
                    instruction=instruction,  # Foreign key reference
                    text=operand.ast_text,  # Wd, Xn, Vn (and not Rd, Rm, Rn)
                    syntax=operand.syntax,  # X0, V1
                    type=operand.type,  # gpr_64, gpr_32
                    type_category=operand.type_category,  # register, immediate, unknown # TODO:: need to extend it
                    role=operand.role,  # dest, src, src_dest
                    size=operand.size,  # 8,16,32,64,128
                    index=operand.index,  # 1,2..
                    width=operand.width,
                    extensions=operand.extensions,
                    is_optional=0,  # Default to 0, can be adjusted if needed
                    is_operand=operand.is_operand,
                    is_valid=operand.is_valid
                )

    print(f"Total instructions: {Instruction.select().count()}")
    print("Database populated successfully!")

    print(f"Database is stored at: {db.database}")

    return yaml_dict

    # query = (Instruction.select().join(Operand).where((Operand.role == "dest")&(Operand.type == "gpr_64")))
    # print(f"Total instructions under dest and grp64:  { len(query)}")
    #
    # query = (Instruction.select().join(Operand).where(
    #     (Operand.role == "dest") & (Operand.type == "gpr_64") &
    #     (Operand.instruction_id << Operand.select(Operand.instruction_id)
    #      .where(Operand.role == "src") ))
    #     .distinct())
    # print(f"Total instructions under dest_gpr64_src:  { len(query)}")
    # query = Instruction.select()
    # src_type = dest_type = "gpr_64"
    # query = query.where(
    #     (Instruction.src1_type == src_type ) |
    #     (Instruction.src2_type == src_type) |
    #     (Instruction.src3_type == src_type) |
    #     (Instruction.src4_type == src_type)
    # )
    # query = query.where(
    #     (Instruction.dest1_type == dest_type ) |
    #     (Instruction.dest2_type == dest_type)
    # )
    # for instr in query:
    #     print(f"    Instruction: {instr.unique_id} | {instr.mnemonic} | {instr.syntax} ")
    #     extracted_operands = Operand.select().where(Operand.instruction == instr)
    #     for op in extracted_operands:
    #         print(f"       Text: {op.text}")
    #         print(f"       Type: {op.type}")
    #         print(f"       Role: {op.role}")
    #         print(f"       Size: {op.size}")
    #         print(f"       Element Size: {op.element_size}")
    #         print(f"       Is Optional: {op.is_optional}")
    # print(f"Total instructions under dest_size64:  { len(query)}")


# Automatically run if script is executed directly
if __name__ == "__main__":
    # periodically update the isa_lib yaml from the ec/util/isa_lib path
    #   .source_cache/hw/nvcpu_arm_olym/ip/cpuip/core/1.0/dvlib/ec/util/isa_lib/spec_gen/spec/isa_lib.yml
    # Load ASL and USL JSON data, and convert JSON lists to dictionaries for quick lookup
    # isa_lib_path = "/home/scratch.zbuchris_cpu/run_arrow/ArrowProject/Externals/db_manager/instruction_jsons/arm_isa_lib.yml"

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    isa_lib_path = os.path.join(base_dir, 'instruction_jsons', 'arm_isa_lib.yml')
    # isa_lib_path = os.path.join(base_dir, 'instruction_jsons', 'arm_isa_lib_mini.yml')

    if not os.path.exists(isa_lib_path):
        raise ValueError(f" Yaml path doesn't exist: {isa_lib_path}")
    # Load YAML file
    with open(isa_lib_path, "r") as f:
        yml_data = yaml.safe_load(f)

    # Initialize database
    initialize_db()
    updated_yaml = populate_database(yml_data, force_reset=True)

    """Writes a dictionary to a YAML file."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    new_yaml = os.path.join(base_dir, 'instruction_jsons', 'arm_isalib_extended.yml')
    with open(new_yaml, "w") as f:
        yaml.dump(updated_yaml, f, default_flow_style=False, sort_keys=False)
