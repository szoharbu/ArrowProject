import os
import re
import yaml
from Externals.db_manager.asl_testing.asl_models import Instruction, Operand, db, initialize_db


def reset_database():
    """Drops existing tables and recreates them to ensure schema consistency."""
    db.drop_tables([Instruction, Operand])  # Drop old tables
    db.create_tables([Instruction, Operand])  # Recreate tables
    print("Database tables reset to match the latest schema.")


# Function to extract Operands information from Yaml
def extract_operands(inst_data):
    """Extracts up to 4 source and 2 destination operands explicitly."""

    operands_data = []
    var_encode = inst_data.get("var_encode", {})
    if var_encode is not None:
        for operand_text, operand_info in var_encode.items():
            operand_entry = {
                "text": operand_text,  # Operand identifier (Rd, Rm, Rn)
                "hibit": operand_info.get("hibit", None),  # High bit position
                "width": operand_info.get("width", None),  # Bit width
                "encode": operand_info.get("encode", ""),  # Encoding pattern
                "cnt": operand_info.get("reginfo", {}).get("cnt", 1),  # Register count
                "r31": operand_info.get("reginfo", {}).get("r31", "N/A"),  # Special register condition
                "type": operand_info.get("reginfo", {}).get("type", "N/A"),  # Register type (e.g., gpr_64)
                "use": operand_info.get("reginfo", {}).get("use", "N/A"),  # Operand role (dst, src)
                "role": "N/A",  # Similar to "use" field, with slight adjustments and more common name
                "index": 0,  # Index of operand (1, 2, 3, 4)
                # Similar to 'use' both more common name, keeping also the original 'use' name
            }
            operands_data.append(operand_entry)

    # Sort operands by `hibit` (bit position) to determine order
    operands_data.sort(key=lambda op: op["hibit"])

    def check_substring(strings, substring):
        return any(substring in s for s in strings)

    index = 1
    # Add operand size and Index op1, op2, ...
    for operand in operands_data:
        operand["index"] = index
        index += 1
        optional_names = [operand["type"], operand["text"]]
        # Possible types are: gpr_32, gpr_64, gpr_var, simdfp_scalar_128, simdfp_scalar_16, simdfp_scalar_32, simdfp_scalar_64, simdfp_scalar_8, simdfp_scalar_var, simdfp_vec, sve_pred, sve_reg
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
        elif "simdfp" in operand["type"]:  # default operand size in Olympus
            operand["size"] = 128
        elif "sve" in operand["type"]:  # default operand size in Olympus
            operand["size"] = 128
        else:
            operand["size"] = None

    # Adding "role" while keeping the original "use", with slight naming adjustment dest instead of dst
    for operand in operands_data:
        if operand["use"] == "dst":
            operand["role"] == "dest"
        elif operand["use"] == "src":
            operand["role"] == "src"
        elif operand["use"] == "src_dst":
            operand["role"] == "src_dest"


    # Adding operand category based on the operand type
    for operand in operands_data:
        '''
        Operand types:
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

        elif op_role == "dst" or op_role == "src_dest":
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

            # Generate unique ID
            unique_id = inst_id
            # clean_syntax = re.sub(r"[<>#.{}]", "", asm_template)  # Remove <, >, #, ., {, }
            # clean_syntax = re.sub(r"(,\s+|\s+)", "_", clean_syntax)  # Replace spaces and ", " with _
            # unique_id = f"{inst_id}__{clean_syntax}"
            # counter = 1

            # # Ensure uniqueness
            # while Instruction.select().where(Instruction.unique_id == unique_id).exists():
            #     unique_id = f"{unique_id}__{counter}"
            #     counter += 1

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
                    role=operand["role"],  # dst, src, src_dest
                    size=operand["size"],  # 8,16,32,64,128
                    index=operand["index"],  # 1,2..
                    width=operand["width"],
                    is_optional=0  # Default to 0, can be adjusted if needed
                )


    print(f"Total instructions: {Instruction.select().count()}")
    print("Database populated successfully!")

    print(f"Database is stored at: {db.database}")

    # query = (Instruction.select().join(Operand).where((Operand.role == "dest")&(Operand.type == "gpr_64")))
    # print(f"Total instructions under dest:  { len(query)}")
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
    #isa_lib_path = "/home/scratch.zbuchris_cpu/run_arrow/ArrowProject/Externals/db_manager/instruction_jsons/arm_isa_lib.yml"

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    isa_lib_path = os.path.join(base_dir, 'instruction_jsons', 'arm_isa_lib.yml')
    if not os.path.exists(isa_lib_path):
        raise ValueError(f" Yaml path doesn't exist: {isa_lib_path}")
    # Load YAML file
    with open(isa_lib_path, "r") as f:
        yml_data = yaml.safe_load(f)

    # Initialize database
    initialize_db()

    populate_database(yml_data, force_reset=True)


