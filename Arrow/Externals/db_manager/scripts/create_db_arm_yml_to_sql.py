import os
import re
import yaml
from typing import List
from Externals.db_manager.asl_testing.asl_models import Instruction, Operand, db, initialize_db

import logging

#from Externals.db_manager.scripts.arm_islib_parser.asmtemplate_parser import parse_asm_template


logger = logging.getLogger(__name__)

valid_instruction_counter = 0  # global variable

def reset_database():
    """Drops existing tables and recreates them to ensure schema consistency."""
    db.drop_tables([Instruction, Operand])  # Drop old tables
    db.create_tables([Instruction, Operand])  # Recreate tables
    print("Database tables reset to match the latest schema.")


####################################################################################################################### Operand Class

class Operand_class:
    def __init__(self,
                 operand_name: str,
                 ast_data: dict = None,
                 var_encode_data: dict = None,
                 extensions: list = None):
        # 1) set defaults in one block
        defaults = {
            "operand_name":   operand_name,
            "ast_text":       "unknown",
            "ast_full_text":  "unknown",
            "var_encode_text":"unknown",
            "index":          -1,
            "syntax":         "unknown",
            "size":           None,
            "hibit":          None,
            "width":          None,
            "encode":         "",
            "cnt":            1,
            "r31":            "N/A",
            "type":           "unknown",
            "type_category":  "unknown",
            "role":           "unknown",
            "extensions":     extensions or [],
            "tokens":         [],
            "is_operand":     True,
            "is_valid":       True,
            "is_optional":    False,
            "is_memory":      False,
            "memory_role":    "None",
        }
        # 1) set defaults in one block
        for k, v in defaults.items():
            setattr(self, k, v)

        # 2) apply ast_data
        if ast_data:
            self._assign_fields(ast_data)
        else:
            self.is_valid = False
            logger.warning("Operand `%s` missing ast_data", operand_name)

        # 3) apply var_encode_data, with renaming of "text" → "var_encode_text"
        if var_encode_data:
            rename_map = {"text": "var_encode_text"}
            self._assign_fields(var_encode_data, rename_map)
        elif  re.fullmatch(r"\{#\d+\}", self.ast_text):
            # this is a special case, where an operand is hardcoded immediate and it doesnt have Var_encode_data
            logger.warning("Operand `%s` missing var_encode_data", operand_name)
        else:
            self.is_valid = False
            logger.warning("Operand `%s` missing var_encode_data", operand_name)

        logger.debug("Initialized %r", self)

    def _assign_fields(self,
                       data: dict,
                       rename_keys: dict = None):
        """
        For each key,val in data:
          - if rename_keys maps it, use the new name
          - if the attribute exists, setattr
          - else log.debug and skip
        """
        for raw_key, val in data.items():
            key = rename_keys.get(raw_key, raw_key) if rename_keys else raw_key
            if hasattr(self, key):
                setattr(self, key, val)
                logger.debug("  %s ← %r", key, val)
            else:
                logger.debug("  Ignored unknown field `%s` for operand `%s`", key, self.operand_name)

    def __repr__(self):
        # concise repr showing only a few core fields, drop the rest if you like
        return (f"<Operand_class "
                f"name={self.operand_name!r} "
                f"idx={self.index} "
                f"syntax={self.syntax!r} "
                f"type={self.type!r} "
                f"is_memory={self.is_memory!r} "
                f"is_optional={self.is_optional!r} "
                f"valid={self.is_valid}>")

    def set(self, key, value):
        """Set an attribute dynamically, used by extract_operands to flag or update fields."""
        if hasattr(self, key):
            setattr(self, key, value)
            logger.debug("Set `%s` to %r on operand `%s`", key, value, self.operand_name)
        else:
            raise AttributeError(f"Unknown attribute: {key}")

# class Operand_class:
#     def __init__(self, operand_name: str, ast_data=None, var_encode_data=None, extensions=None):
#         """
#         Initialize an Operand object.

#         :param ast_text: Operand identifier as appeared in the asm_template (e.g., Xd, Vm, Wn)
#         :param var_encode_text: operand text as appeared in the Var_encoding (e.g., Rd, Rm, Rn)
#         :param index: Operand index (1, 2, 3, 4) or -1 for non Operands entries (e.g., Q, size)
#         :param syntax: Syntax representation (e.g., X0, V1)
#         :param size: Operand size (e.g., 32, 64)
#         :param hibit: High bit position
#         :param width: Bit width
#         :param encode: Encoding pattern
#         :param cnt: Register count
#         :param r31: Special register condition
#         :param type: Register type (e.g., gpr_64)
#         :param type_category: Register type (e.g., register, immediate)
#         :param role: Similar to "use" field, with slight adjustments and more common name
#         """
#         self.operand_name = operand_name
#         self.ast_text = "unknown"
#         self.ast_full_text = "unknown" # Full text from asm_template, include characters the ast_test might remove like [ , ] , ]! ...
#         self.var_encode_text = "unknown"
#         self.index = -1
#         self.syntax = "unknown"
#         self.size = None
#         self.hibit = None
#         self.width = None
#         self.encode = ""
#         self.cnt = 1
#         self.r31 = "N/A"
#         self.type = "unknown"
#         self.type_category = "unknown"
#         self.role = "unknown"
#         self.extensions = extensions
#         self.tokens = []  # List of variable tokens <*>
#         self.is_operand = True  # Flag to indicate if Operand came from ast_operands or just a data field from var_encoding
#         self.is_valid = True  # Flag to indicate if the Operand is valid or still contain unknown values
#         self.is_optional = False
#         self.is_memory = False
#         self.memory_role = "None"

#         if var_encode_data:
#             for key, val in var_encode_data.items():
#                 if key == "text":
#                     key = "var_encode_text"  # Rename field
#                 if hasattr(self, key):  # only set if the attribute is defined
#                     setattr(self, key, val)

#         if ast_data:
#             for key, val in ast_data.items():
#                 if hasattr(self, key):  # only set if the attribute is defined
#                     setattr(self, key, val)

#         if ast_data is None:
#             self.is_operand = False

#         if var_encode_data is None or ast_data is None:
#             print(f"             - Invalid operand `{self.operand_name}`, var_encode or ast_data is None ")
#             self.is_valid = False

#         print(f"          - Operand init : {self}")

#     def set(self, key, value):
#         if hasattr(self, key):
#             setattr(self, key, value)
#         else:
#             raise AttributeError(f"Unknown attribute: {key}")

#     def __str__(self):
#         attrs = vars(self)  # returns the object's __dict__
#         return f"{self.__class__.__name__}({', '.join(f'{k}={v}' for k, v in attrs.items())})"



######################################################################################################################## asm_template parsing

def parse_asmtemplate_memory_struct(asm_template):

    memory_struct_dict = { "base" : None, "offset_immediate" : None, "post_offset_immediate" : None, "offset_register" : None, "extended_register": None }

    # Regular expression to match the memory operand
    mem_struct_regex = r',\s*\[(.*?)\](?:$|, #([^\s,]+)|, )?'
    ##    ,\s*: This matches make sure there is at least one whitespace characters, which separates previous operands from the memory operand.
    ##    \[(.*?)\]: This captures the contents inside the [], which is the memory operand.
    ##    (?:$|, #([^\s,]+)|, )?: This matches an optional comma, a space, a # character, and an optional sign followed all characters that are not spaces or commas. This captures the immediate value.

    match = re.search(mem_struct_regex, asm_template)
    if match:
        memory_struct = match.group(1)  # contents inside the []
        post_index = match.group(2)  # immediate value (if present)
        post_index_str = " #"+post_index if post_index is not None else ""
        #print(f"zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz found memory struct: '[{memory_struct}]{post_index_str}'")

        if post_index is not None:
            # if a post_index exist, it means the inner memory struct is just a single base operand, and the
            memory_struct_dict["base"] = memory_struct
            memory_struct_dict["post_offset_immediate"] = "#"+post_index
        else:
            # the inner memory struct can be a list of operands, like [<Xn>, <imm>], need to split them
            inner_operands = re.sub(r"{,\s*", ",{", memory_struct) # Convert "{, " into ",{"
            inner_operands = re.split(r",\s*", inner_operands)
            memory_struct_dict["base"] = inner_operands[0]  # First operand is the base

            if len(inner_operands) > 1:
                # if a 2nd operand exist, if its start with # its an immediate offset, else its a register offset
                if inner_operands[1].startswith("#"):
                    memory_struct_dict["offset_immediate"] = inner_operands[1]
                else:
                    memory_struct_dict["offset_register"] = inner_operands[1]

                if len(inner_operands) > 2:
                    # if a 3rd operand exist, if its start with # its an immediate offset, else it's an extended register
                    if inner_operands[1].startswith("#"):
                        memory_struct_dict["offset_immediate"] = inner_operands[2]
                    else:
                        memory_struct_dict["extended_register"] = inner_operands[2]

        print(f"       - Memory struct found: {memory_struct_dict}")

    return memory_struct_dict


def parse_asmtemplate(asm_template):
    """
    Consume asm_template and return a list of clean operands and extra info. like:
        - asm template : ADD <Vd>.<T>, <Xn|SP>{, <Vm>.<T>}
            - operand1 : Vd      extra info: contain T
            - operand2 : Xn      extra info: contain SP
            - operand3 : Vm      extra info: contain T, optional

    """

    # ####################### TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
    # ####################### TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
    # ####################### TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
    # ####################### TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
    # ####################### TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
    # print('TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO')
    # print('TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO')
    # print(f"   = asm template : {asm_template} ")
    # testing_ast = parse_asm_template(asm_template)
    # print(testing_ast)
    # print('TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO')
    # print('TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO')
    

    # ####################### TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
    # ####################### TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
    # ####################### TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
    # ####################### TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO
    # ####################### TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO TODO

    # Parse the asm template into a structured AST
    clean_asm_template = re.sub(r"\s+", " ", asm_template).strip()
    print(f"   = asm template : {clean_asm_template} ")
    print(f"     = extract asmtemplate")

    # Step 1: Extract the mnemonic (first word before a space)
    parts = clean_asm_template.split(" ", 1)
    mnemonic = parts[0]

    # If there are no operands, return early
    if len(parts) == 1:
        return []

    operands_str = parts[1]  # Everything after the mnemonic

    # Step 2: Handle the special case `{, op3}` -> `, {op3}`
    # Convert "{, " into ",{"
    operands_str = re.sub(r"{,\s*", ",{", operands_str)

    # Step 3: Mapping the memory struct, as multiple operands can be included in the same memory struct. like [<Xn>, <imm>]
    is_memory = False
    memory_struct_dict = parse_asmtemplate_memory_struct(clean_asm_template)

    # Step 4: Split operands while keeping all symbols (except commas)
    # This ensures {op3} is treated as one operand
    operands = re.split(r",\s*", operands_str)

    operands_data = []
    index = 0

    for op in operands:
        orig_syntax = op
        clean_syntax = op
        index += 1
        is_optional = False
        memory_role = "None"

        # Check if the operand is fully wrapped in {}
        # (?:]|]!)?: Optionally allow either ] or ]! after the closing curly brace
        match = re.fullmatch(r"\{(.*)\}(?:]|]!)?", orig_syntax)
        
        if match:
            is_optional = True  # Mark as optional


        if orig_syntax.startswith("["):
            clean_syntax = orig_syntax[1:]   # remove [ from the start
            is_memory = True    # Mark as Memory that can include multiple operands like [<Xn>, <imm8>}]

        # Extract tokens inside <...>
        tokens = re.findall(r"<(.*?)>", orig_syntax)

        #print(f'zzzzzz asm_template orig_syntax= {orig_syntax}, index= {index}, tokens= {tokens}, optional= {optional}')

        clear_is_memory = False
        if orig_syntax.endswith("]"):
            clean_syntax = clean_syntax.removesuffix("]")
            clear_is_memory = True
        if orig_syntax.endswith("]!"):
            clean_syntax = clean_syntax.removesuffix("]!")
            clear_is_memory = True

        if clean_syntax in memory_struct_dict.values():
            # Find and print the key(s) that match this value
            match = False
            for key, value in memory_struct_dict.items():
                if value == clean_syntax:
                    match = True
                    memory_role = key
                    if key == "post_offset_immediate":
                        is_memory = True # to handle cases of post_index memory like [<Xn|SP>], #<simm>
                        clear_is_memory = True
                    break
            if not match and is_memory:
                raise ValueError(f"Operand '{clean_syntax}' is marked as memory but does not match any known memory structure.")

        new_operand = {
            "ast_full_text": orig_syntax,
            "ast_text": clean_syntax,
            "index": index,
            "tokens": tokens,
            "is_optional": is_optional,
            "is_memory": is_memory,
            "memory_role": memory_role,
        }

        if clear_is_memory:
            is_memory = False

        print(f"       - asm_template parsed '{clean_syntax}' : {new_operand}")
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

    #print(f"          - updating type_category of type {operand["type"]} to '{operand["type_category"]}' category, and role to '{operand["role"]}'")

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

    #print(f"          - updating size of type {operand["type"]} to '{operand["size"]}'")
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
    #print(f"          - updating syntax from '{operand["text"]}' to '{operand["syntax"]}'")
    yaml_entry["syntax"] = operand["syntax"]


def extract_var_encode(inst_data):
    print(f"     = extract var_encoding")
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

            #print(f"       - var_encode_entry: {var_encode_entry["text"]}")
            assign_operand_category(var_encode_entry, operand_info)
            assign_operand_size(var_encode_entry, operand_info)
            assign_operand_syntax_name(var_encode_entry, operand_info)
            print(f"       - var_encode_entry '{var_encode_entry["text"]}' : {var_encode_entry}")


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

            print(f"          - int_keys: {int_keys}")
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
        print(f"          - label_map: {label_map}")

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
    print(f"     = extract constraints")
    aligned_options = {}
    constraint_groups = inst_data.get("constraint", {})

    if constraint_groups:
        try:
            # Code that might raise an exception
            aligned_options = extract_aligned_options(constraint_groups)
        except Exception as e:
            # Code to handle the exception
            print(f"zzzzzzzzzzz extract_constraints:: error: {e}")
            return False, {}

        print(f"          - aligned_options: {aligned_options}")

    return True, aligned_options


####################################################################################################################### full operand parsing


# Function to extract Operands information from Yaml
def extract_operands(inst_data):
    print(f"  === extract operands flow")
    success = True
    # extract operands from the asm_templates
    asm_template_operands_data = parse_asmtemplate(inst_data.get("asmtemplate", ""))
    var_encode_data = extract_var_encode(inst_data)
    success_constraints, constraints_data = extract_constraints(inst_data)

    success = success and success_constraints  # accumulate successes or failure as you go

    '''
    There are multiple variation of how an operand can look like,
    yet, if there are tokens <*> then the var_encoding is always first and the rest can be Type specifier/modifiers/...   in the operand structure. This is consistent across all instruction types. For example:
    for examples: 
        <Xd> - Xd is the var_encoding
        <Zdn>.<T> - Zdn is the var_encoding, T is a type specifier 
        <Pg>/M - Pg is the var_encoding, M is a modifier
        <Xn|SP> - Xn is the var_encoding, SP is an optional stack 
    '''

    print(f"     = extract operands")

    operands_data: List[Operand_class] = []
    if asm_template_operands_data:  # if asm_template_operands_data is not empty

        asm_template_operands_data.sort(key=lambda op: op["index"])
        for asmt_op in asm_template_operands_data:
            print(f"       - operand_entry: {asmt_op['ast_text']}")
            tokens = asmt_op["tokens"]

            if not tokens:
                operand_entry = Operand_class(operand_name=asmt_op["ast_text"], ast_data=asmt_op)
                operands_data.append(operand_entry)
                break

            # handle the first token - if there are several tokens in the operand, the var_encode is always the first.
            asmt_first_token = tokens.pop(0)    # pop the first element

            asmt_token_to_var_encode = None
            #print(f"zzzzzzzzzzzzzzz  asmt_first_token: {asmt_first_token}")
            if (match := re.match(r'([^|]+)\|W?SP', asmt_first_token)): # check if asmt_op_var looks like Xn|SP or WSP|WSP
                asmt_first_token = match.group(1)  # Remove the "|SP" part

            for var in var_encode_data:
                # check for exact match
                if asmt_first_token == var["syntax"]:
                    asmt_token_to_var_encode = var
                    break
                # check for partial immediate match
                elif "imm" in asmt_first_token and "imm" in var["syntax"]:
                    asmt_token_to_var_encode = var
                    break
                # handle cases when counter is involved, like Wt1, Wt2
                elif (match := re.match(r'^(\w+?)(\d)$', asmt_first_token)):
                    if (match.group(1) == var["syntax"]) and (match.group(2)=="1"):
                        asmt_token_to_var_encode = var
                        break
                # handle cases of <V><d|n|m>
                elif (match := re.match(r'<V><([dnm])>\s*$', asmt_op['ast_text'])):
                    if ("V"+match.group(1) == var["syntax"]):
                        asmt_token_to_var_encode = var
                        break


            if asmt_token_to_var_encode is None:
                #raise ValueError(f"Operand {asmt_op['ast_text']} is without a matching var_encode")
                print(f"zzzzzzzzzzzz  Invalid operand: {asmt_token_to_var_encode} - without a matching var_encode")
                operand_entry = Operand_class(operand_name=asmt_op["ast_text"] , ast_data=asmt_op)
                operand_entry.set("is_valid", False)
                operands_data.append(operand_entry)
                break
                #    raise ValueError(f"Operand {asmt_op['clean_name']} not found in var_encode_data")
            else:
                print(f"          - asmt_token `{asmt_first_token}` matched with: {asmt_token_to_var_encode}")

            # handle extensions field
            extensions = []
            if tokens: # the first was used for var_encode. if there is a second its a constraint TODO:: need to check that assumption
                second_token = tokens.pop(0)
                if constraints_data:
                    print(f"          - constraint: {constraints_data}")
                    field_name = second_token + "_options"
                    if field_name in constraints_data:
                        print(f"          - updating extensions of {asmt_op["ast_text"]} to '{constraints_data[field_name]}'")
                        extensions = constraints_data[field_name]
                    # elif asmt_op['ast_text'] == "<V><d>":
                    #     # handle special case of <V><d> where the constraint name is V_option and not d_option
                    #     field_name = "V_options"
                    #     print(f"          - updating extensions of {asmt_op["ast_text"]} to '{constraints_data[field_name]}'")
                    #     extensions = constraints_data[field_name]
                    else:
                        print(f"          - operand {asmt_op["ast_text"]} has no matching extension in constraints data")

            # In most cases, there are maximum of 2 tokens. there are some rare cases like "<Vn>.<Ts>[<index>]" or even (<systemreg>|S<op0>_<op1>_<Cn>_<Cm>_<op2>)
            # This cases will be skipped for now. TODO:: need to address it later on
            if tokens: # two tokens were already removed from the list. checking if there are more
                print(f"             - Invalid operand `{asmt_op["ast_text"]}`, Tokens left without a match: {tokens}")
                # raise ValueError(f"Tokens left in operand {asmt_op['ast_text']}: {tokens}")

            operand_entry = Operand_class(operand_name=asmt_op["ast_text"],
                                          ast_data=asmt_op,
                                          var_encode_data=asmt_token_to_var_encode,
                                          extensions=extensions)

            if tokens:
                operand_entry.set("is_valid", False)

            operands_data.append(operand_entry)


    # Identify unmatched items from the var_encode_data
    existing_syntaxes = {operand.syntax for operand in operands_data} # Extract existing syntaxes from operands_list
    non_matching_vars = [var for var in var_encode_data if var['syntax'] not in existing_syntaxes] # Extract vars that do not exist in the operands_list based on the 'syntax' field
    for var in non_matching_vars:
        print(f"       - operand_entry: {var["text"]}")
        operand_entry = Operand_class(operand_name=var["text"], var_encode_data=var)
        operand_entry.set("index", -1)
        operand_entry.set("is_valid", False)
        operand_entry.set("is_operand", False)
        operands_data.append(operand_entry)




    operands_data.sort(key=lambda op: op.index)

    return success, operands_data


# Function to extend operands and upload basic fields into Instruction object, like src1, src2, dest1. They will be added to Instruction entry to reduce usage of join queries.
def extended_fake_knobs(operands_data):
    """Extracts up to 4 operands explicitly."""

    op1_role, op2_role, op3_role, op4_role = None, None, None, None
    op1_type, op2_type, op3_type, op4_type = None, None, None, None
    op1_size, op2_size, op3_size, op4_size = None, None, None, None
    op1_ismemory, op2_ismemory, op3_ismemory, op4_ismemory = False, False, False, False

    index = 1
    for op in operands_data:
        if op.is_operand:
            # print(f"zzzzzzzzzzzzzz name = {op.operand_name}, index = {op.index}, role = {op.role}, type = {op.type}, size = {op.size}, is_memory = {op.is_memory}")
            if op.index == 1:
                op1_role, op1_type, op1_size, op1_ismemory = op.role, op.type, op.size, op.is_memory
            elif op.index == 2:
                op2_role, op2_type, op2_size, op2_ismemory = op.role, op.type, op.size, op.is_memory
            elif op.index == 3:
                op3_role, op3_type, op3_size, op3_ismemory = op.role, op.type, op.size, op.is_memory
            elif op.index == 4:
                op4_role, op4_type, op4_size, op4_ismemory = op.role, op.type, op.size, op.is_memory

    return {
        "op1_role": op1_role, "op1_type": op1_type, "op1_size": op1_size, "op1_ismemory": op1_ismemory,
        "op2_role": op2_role, "op2_type": op2_type, "op2_size": op2_size, "op2_ismemory": op2_ismemory,
        "op3_role": op3_role, "op3_type": op3_type, "op3_size": op3_size, "op3_ismemory": op3_ismemory,
        "op4_role": op4_role, "op4_type": op4_type, "op4_size": op4_size, "op4_ismemory": op4_ismemory,
    }


def populate_database(yaml_dict, force_reset=False):
    """
    Populates the database with instruction data.
    """

    global valid_instruction_counter
    valid_instruction_counter = 0

    if force_reset:
        reset_database()

    # Insert data into SQLite using a transaction
    with db.atomic():

        for inst_id, inst_data in yaml_dict.items():
            print("=========================================================================================================================")
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
                print(f"       - Invalid instruction: {inst_id}")
            else:
                for op in operands_data:
                    if op.is_operand and not op.is_valid:
                        is_instruction_valid = False
                        print(f"       - Invalid instruction: {inst_id} due to invalid operand {op.syntax}")
                        break

            if is_instruction_valid:
                valid_instruction_counter += 1

            instr_extended_fake_knobs = extended_fake_knobs(operands_data)

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
                **instr_extended_fake_knobs
            )

            # Handle random_generate flag
            instruction.random_generate = inst_data.get("random_generate", "True") == "True"

            # TODO:: need to add that information to the DB, not to the script. 
            # for now I'm setting some unfriendly instructions as random_generate = False
            branch_instructions = ["br", "bra", "braaz", "brab", "brabz", "blr", "blraa", "blraaz", "blrab", "blra",  # branch instructions
                                    "ret", "retaa", "retab", "eret", "eretaa", "eretab", # return instructions
                                    "cbnz", "cbz", "tbz", "tbnz", # conditional branch instructions
                                    "dcps1", "dcps2", "dcps3", "drps", # debug state change,  These instructions trigger transitions to debug modes
                                    "mrs", "msr", # system register access
                                    "eret", "smc", "hvc", "svc", "brk"] # exception handling


            if instruction.mnemonic in branch_instructions:
                instruction.random_generate = False

            instruction.save()

            for operand in operands_data:
                Operand.create(
                    instruction=instruction,  # Foreign key reference
                    text=operand.ast_text,  # <Wd>, <Xn>, <Vn> (and not Rd, Rm, Rn)
                    full_text=operand.ast_full_text, # include all tokens and characters like []!
                    syntax=operand.syntax,  # X0, V1
                    type=operand.type,  # gpr_64, gpr_32
                    type_category=operand.type_category,  # register, immediate, unknown # TODO:: need to extend it
                    role=operand.role,  # dest, src, src_dest
                    size=operand.size,  # 8,16,32,64,128
                    index=operand.index,  # 1,2..
                    width=operand.width,
                    extensions=operand.extensions,
                    is_optional=operand.is_optional,
                    is_memory=operand.is_memory,
                    memory_role=operand.memory_role,
                    is_operand=operand.is_operand,
                    is_valid=operand.is_valid
                )

    print(f"Total instructions: {Instruction.select().count()}")

    # dont show the full percentage, just the last 2 digits
    valid_precentage = valid_instruction_counter/Instruction.select().count()
    valid_precentage = str(valid_precentage).split(".")[1][:2]
    print(f"Total valid instructions: {valid_instruction_counter} ({valid_precentage}%)")
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
    #isa_lib_path = os.path.join(base_dir, 'instruction_jsons', 'arm_isa_lib_mini.yml')

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
