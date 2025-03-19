import os
import re
import yaml
from Externals.db_manager.asl_testing.asl_models import Instruction, Operand, db, initialize_db
from collections import OrderedDict

def reset_database():
    """Drops existing tables and recreates them to ensure schema consistency."""
    db.drop_tables([Instruction, Operand])  # Drop old tables
    db.create_tables([Instruction, Operand])  # Recreate tables
    print("Database tables reset to match the latest schema.")

def parse_asmtemplate(asm_template):
    """
    Consume asm_template and return a list of clean operands and extra info. like:
        - asm template : ADD <Vd>.<T>, <Xn|SP>{, <Vm>.<T>}
            - operand1 : Vd      extra info: contain T
            - operand2 : Xn      extra info: contain SP
            - operand3 : Vm      extra info: contain T, optional

    """
    print("===== parse_asmtemplate")
    clean_asm_template = re.sub(r"\s+", " ", asm_template).strip()
    print(f"    - asm template : {clean_asm_template} ")

    # Step 1: Extract the mnemonic (first word before a space)
    parts = clean_asm_template.split(" ", 1)
    mnemonic = parts[0]

    # If there are no operands, return early
    if len(parts) == 1:
        return mnemonic, []

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
        extra_info = ""
        index +=1
        # Check if the operand is fully wrapped in {}
        match = re.fullmatch(r"\{(.*)\}", clean_op)
        if match:
            clean_op = match.group(1)  # Extract the content inside {}
            #optional = True  # Mark as optional
            extra_info = f"optional , {extra_info}"

        clean_op = re.sub(r"[{}<>]", "", clean_op)

        # Check if the operand ends with .<T> .D /P ...
        match = re.fullmatch(r"(.+?)(?:\.(\w+)|\.\<(\w+)\>|/(\w+)|\|(\w+)|\[(.+)\])?", clean_op)
        if match:
            clean_op = match.group(1)
            for i in range(2, 7):
                if match.group(i) is not None:
                    extra_info = f"contain {match.group(i)} , {extra_info}"

        new_operand = {
            "original_name": op,
            "clean_name": clean_op,
            "index": index,
            "extra_info": extra_info.rstrip(' ,'),
        }
        operands_data.append(new_operand)
    #
    # for op in operands_data:
    #     name = op["clean_name"]
    #     extra_info = op["extra_info"]
    #     index = op["index"]
    #     if extra_info == "":
    #         print(f"    - operand{index} : {name}")
    #     else:
    #         print(f"    - operand{index} : {name}      extra info: {extra_info}")

    return operands_data

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
    # TODO:: need to extend it
    else:
        operand["type_category"] = "unknown"
    print(f"        - updating type_category of type {operand["type"]} to {operand["type_category"]} category")

    # Adding "role" while keeping the original "use", with slight naming adjustment dest instead of dst
    if operand["use"] == "dst":
        operand["role"] = "dest"
    elif operand["use"] == "src":
        operand["role"] = "src"
    elif operand["use"] == "src_dst":
        operand["role"] = "src_dest"
    print(f"        - updating role from {operand["use"]} to {operand["role"]}")

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
    #elif "16" in optional_names:
    elif check_substring(optional_names, "16"):
        operand["size"] = 16
    elif check_substring(optional_names, "8"):
        operand["size"] = 8
    elif "simdfp" in operand["type"]:  # default operand size in ProjectA
        operand["size"] = 128
    elif "sve_reg" in operand["type"]:  # default operand size in ProjectA
        operand["size"] = 128
    elif "sve_pred" in operand["type"]:  # default operand size in ProjectA
        operand["size"] = 16
    else:
        operand["size"] = None

    print(f"        - updating size of type {operand["type"]} to {operand["size"]}")
    yaml_entry["size"] = operand["size"]

def assign_operand_syntax_name(operand, yaml_entry):
    """
    Assigns a syntax field to an operand based on its type and size.
    """
    # Possible types are: gpr_32, gpr_64, gpr_var, simdfp_scalar_128, simdfp_scalar_16, simdfp_scalar_32, simdfp_scalar_64, simdfp_scalar_8, simdfp_scalar_var, simdfp_vec, sve_pred, sve_reg

    syntax = "unknown"  # Default value

    if operand["type"].startswith("gpr"): # gpr_32, gpr_64, gpr_var
        match = re.fullmatch(r"R(\w+)", operand["text"])
        if match:
            reg_num = match.group(1)
            if operand["size"] == 64:
                syntax = f"X{reg_num}"  # 64-bit GPR → Xi
            elif operand["size"] == 32:
                syntax = f"W{reg_num}"  # 32-bit GPR → Wi
        else:
            syntax = operand["text"]  # Special registers like SP, LR, etc.

    elif operand["type"].startswith("simdfp"): # simdfp_scalar_128, simdfp_scalar_16, simdfp_scalar_32, simdfp_scalar_64, simdfp_scalar_8, simdfp_scalar_var, simdfp_vec
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

    elif operand["type"].startswith("sve"): # sve_pred, sve_reg
        syntax = operand["text"]  # Not sure SVE needs conversion.
        # match = re.fullmatch(r"R(\w+)", operand["text"])
        # if match:
        #   ...
        # else:
        #     syntax = operand["text"]  # Special registers like SP, LR, etc.

    operand["syntax"] = syntax
    print(f"        - updating syntax from {operand["text"]} to {operand["syntax"]}")
    yaml_entry["syntax"] = operand["syntax"]

def assign_operand_index(operand, asm_template_operands, yaml_entry):

    match = False
    for i, asm_operand in enumerate(asm_template_operands):
        if asm_operand["clean_name"] == operand["syntax"]:
            match = True
            operand["index"] = i + 1
            operand["extra_info"] = asm_operand["extra_info"]

    if match:
        #print(f"        - find match between {asm_operand["clean_name"]} and {operand["syntax"]} (originally {operand["text"]})")
        print(f"        - updating index to {operand["index"]}")
        if operand["extra_info"] != "":
            print(f"        - updating extra info to {operand["extra_info"]}")
    else:
        print(f"        - no match to {operand["syntax"]} (originally {operand["text"]})")
    yaml_entry["index"] = operand["index"]
    yaml_entry["extra_info"] = operand["extra_info"]


# Function to extract Operands information from Yaml
def extract_operands(inst_data):
    """Extracts up to 4 source and 2 destination operands explicitly."""

    operands_data = []
    var_encode = inst_data.get("var_encode", {})
    if var_encode is not None:
        for operand_text, operand_info in var_encode.items():
            operand_entry = {
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
                "index": -1,  # Index of operand (1, 2, 3, 4) , -1 means unknown
                "extra_info": "N/A",  # Extra information about the operand
                # Similar to 'use' both more common name, keeping also the original 'use' name
            }
            operands_data.append(operand_entry)

    asm_template_operands = parse_asmtemplate(inst_data.get("asmtemplate", ""))
    for operand in operands_data:
        print(f"    - operand {operand["text"]}")
        assign_operand_category(operand, operand_info)
        assign_operand_size(operand, operand_info)
        assign_operand_syntax_name(operand, operand_info)
        assign_operand_index(operand, asm_template_operands, operand_info)




    operands_data.sort(key=lambda op: op["index"])

    return operands_data


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

    for operand in operands_data:
        op_type = operand['type']
        op_role = operand['role']
        op_size = operand['size']

        if op_role == "src" or op_role == "src_dest":
            if src_index == 1:
                src1_type, src1_size = op_type, op_size
            elif src_index == 2:
                src2_type, src2_size = op_type, op_size
            elif src_index == 3:
                src3_type, src3_size = op_type, op_size
            elif src_index == 4:
                src4_type, src4_size = op_type, op_size
            src_index += 1

        elif op_role == "dest" or op_role == "src_dest":
            if dest_index == 1:
                dest1_type, dest1_size = op_type, op_size
            elif dest_index == 2:
                dest2_type, dest2_size = op_type, op_size
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
            print(f"- Processing2: {inst_id} ")

            asm_template = inst_data.get("asmtemplate", "")  # Assume one ASM_templates per entry

            # Extract ASL encoding details
            asl_data = inst_data.get("asl", {})
            if asl_data is not None:
                encoding_name = asl_data.get("encoding_name", "N/A")
                #iform = asl_data.get("iform", "N/A")
                iformid = asl_data.get("iformid", "N/A").replace(".xml", "")

            # Extract USL data
            usl_data = inst_data.get("usl", {})
            if usl_data is not None:
                usl_flow = usl_data.get("flow", "N/A")
                steering_classes_list = usl_data.get("steering", [])
            else:
                usl_flow = "N/A"
                steering_classes_list = []

            unique_id = inst_id

            # Extract and insert operands
            operands_data = extract_operands(inst_data)

            instr_extended_operands = extended_operands(operands_data)
            print(f"  syntax: {asm_template}")
            for op in operands_data:
                print(f"    operand {op}")


            # Insert instruction
            instruction = Instruction.create(
                unique_id=unique_id,
                id=inst_id,
                syntax=asm_template,
                description=inst_data.get("description", "no description"),
                mnemonic=inst_data.get("mnemonic", "").lower(),
                instr_class=inst_data.get("instr_class", "no description"),
                feature=inst_data.get("feature", "None"),
                iformid = iformid,
                usl_flow = usl_flow,
                # mop_count=usl_data.get("mop_count"),
                # table_name=usl_data.get("table_name"),
                # max_latency=max_latency,
                steering_class=str(steering_classes_list),
                **instr_extended_operands
            )

            # Handle random_generate flag
            instruction.random_generate = inst_data.get("random_generate", "True") == "True"
            instruction.save()

            for operand in operands_data:
                Operand.create(
                    instruction=instruction,  # Foreign key reference
                    text=operand["text"],  # Rd, Rm, Rn
                    type=operand["type"],  # gpr_64, gpr_32
                    type_category=operand["type_category"], # register, immediate, unknown # TODO:: need to extend it
                    role=operand["role"],  # dest, src, src_dest
                    size=operand["size"],  # 8,16,32,64,128
                    index=operand["index"],  # 1,2..
                    width=operand["width"],
                    is_optional=0  # Default to 0, can be adjusted if needed
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
    #   /some_path/isa_lib.yml

    # Load ASL and USL JSON data, and convert JSON lists to dictionaries for quick lookup
    #isa_lib_path = "/home/scratch.zbuchris_cpu/run_arrow/ArrowProject/Externals/db_manager/instruction_jsons/arm_isa_lib.yml"

    # TODO:: set this False after testing
    # TODO:: set this False after testing
    # TODO:: set this False after testing
    # TODO:: set this False after testing
    debug_mode = False

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    isa_lib_path = os.path.join(base_dir, 'instruction_jsons', 'arm_isa_lib.yml')
    if debug_mode:
        isa_lib_path = os.path.join(base_dir, 'instruction_jsons', 'arm_isa_lib_mini.yml')

    if not os.path.exists(isa_lib_path):
        raise ValueError(f" Yaml path doesn't exist: {isa_lib_path}")
    # Load YAML file
    with open(isa_lib_path, "r") as f:
        yml_data = yaml.safe_load(f)

    # if debug_mode:
    #     populate_database_mini(yml_data)
    # else:

    # Initialize database
    initialize_db()
    updated_yaml = populate_database(yml_data, force_reset=True)

    """Writes a dictionary to a YAML file."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    new_yaml = os.path.join(base_dir, 'instruction_jsons', 'arm_isalib_extended.yml')
    with open(new_yaml, "w") as f:
        yaml.dump(updated_yaml, f, default_flow_style=False, sort_keys=False)
