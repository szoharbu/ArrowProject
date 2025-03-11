import json
import re
from asl_models import Instruction, Operand, db, initialize_db


def reset_database():
    """Drops existing tables and recreates them to ensure schema consistency."""
    db.drop_tables([Instruction, Operand])   # Drop old tables
    db.create_tables([Instruction, Operand]) # Recreate tables
    print("Database tables reset to match the latest schema.")

def extract_operands(template):
    """Extracts up to 4 source and 2 destination operands explicitly."""
    operands = template.get("operands", [])

    # ✅ Initialize variables with default values
    src1_type, src2_type, src3_type, src4_type = None, None, None, None
    src1_size, src2_size, src3_size, src4_size = None, None, None, None
    dest1_type, dest2_type = None, None
    dest1_size, dest2_size = None, None

    src_index = 1
    dest_index = 1

    for operand in operands:
        op_type = operand.get("type", "")
        op_role = operand.get("role", "")
        op_size = operand.get("size", 0)  # Default to 0

        if op_role == "SRC":
            if src_index == 1:
                src1_type, src1_size = op_type, op_size
            elif src_index == 2:
                src2_type, src2_size = op_type, op_size
            elif src_index == 3:
                src3_type, src3_size = op_type, op_size
            elif src_index == 4:
                src4_type, src4_size = op_type, op_size
            src_index += 1

        elif op_role == "DEST":
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


def extract_mop_data(usl_inst):
    """Extract max_latency and steering_classes from a list of mops."""
    latencies = []
    steering_classes = set()  # Use a set to avoid duplicates

    for mop_table in usl_inst.get("mops_tables", []):
        for mop_entry in mop_table.get("mop_entries", []):
            mop = mop_entry.get("mop", {})
            # Extract latency and steering class
            latencies.append(mop.get("latency_value", 0))
            steering_classes.add(mop.get("steering_class", ""))  # Avoid duplicates

    # Determine max latency
    max_latency = max(latencies) if latencies else 0
    # Convert steering_classes set to a JSON string
    steering_classes_json = json.dumps(list(steering_classes))

    return max_latency, steering_classes_json


def populate_database(asl_dict, usl_dict, force_reset=False):
    """
    Populates the database with instruction data.
    """
    if force_reset:
        reset_database()

    # Insert data into SQLite using a transaction
    with db.atomic():

        for inst_id, asl_inst in asl_dict.items():
            print(f"------------------------------------------------------ {inst_id} ")

            # Get USL data if exists
            usl_inst = usl_dict.get(inst_id, {})

            description = asl_inst.get("description", {}).get("full", "")
            if description is None:
                description = "no description"

            asm_templates = asl_inst.get("asm_templates", [])  # Get all variations

            print(f"  populate_db.py: Processing instruction '{inst_id}' with {len(asm_templates)} variations")

            for template in asm_templates:
                if template is None:
                    continue
                syntax = template.get("syntax", "unknown")

                # setting the unique_id
                clean_syntax = re.sub(r"[<>#.{}]", "", syntax)  # # Remove <, >, #, ., {, and }
                clean_syntax = re.sub(r"(,\s+|\s+)", "_", clean_syntax)  # Replace spaces and ", " with _
                unique_id = f"{inst_id}__{clean_syntax}"  # Unique identifier
                counter = 1
                # Check if the unique_id already exists
                while Instruction.select().where(Instruction.unique_id == unique_id).exists():
                    unique_id = f"{unique_id}__{counter}"  # Append a counter
                    counter += 1

                print(f"    populate_db.py: Processing unique id '{unique_id}'")

                ################################################################
                ###################### Instruction #############################

                # Extract max_latency and steering_classes from mops
                max_latency, steering_classes_json = extract_mop_data(usl_inst)
                print(f"    populate_db.py: Max Latency: {max_latency}, Steering Classes: {steering_classes_json}")


                # Extract operands
                operand_data = extract_operands(template)

                # Insert into DB
                instruction = Instruction.create(
                    unique_id=unique_id,
                    id=inst_id,
                    syntax=syntax,
                    description=description,
                    mnemonic=template.get("mnemonic").lower(),
                    #operands=json.dumps(operands),
                    mop_count=usl_inst.get("mop_count"),
                    table_name=usl_inst.get("table_name"),
                    max_latency=max_latency,
                    steering_class=steering_classes_json,

                    **operand_data

                    #asl_info=json.dumps(asl_inst),
                    #usl_info=json.dumps(usl_inst)
                )
                if template.get("random_generate") == "False":
                    instruction.random_generate = False
                else:
                    instruction.random_generate = True
                instruction.save()  # Save the changes

                ################################################################
                ###################### Operands ################################

                # Insert individual operand entries for lookup/reference
                for operand in template.get("operands", []):
                    Operand.create(
                        instruction=instruction,
                        text=operand.get("text"),
                        type=operand.get("type"),
                        role=operand.get("role"),
                        size=operand.get("size"),
                        element_size=operand.get("element_size"),
                        is_optional=1 if operand.get("is_optional", False) else 0,
                        #anchors=json.dumps(operand.get("anchors", []))  # Store anchors as JSON string
                    )

                # inserted_inst = Instruction.get(Instruction.unique_id == unique_id)
                # print(f"    Inserted: ID={inst_id}, Syntax={syntax}, Mnemonic={asl_inst.get('mnemonic')}, MOP Count={usl_inst.get('mop_count')}")
                # print(f"    Inserted: {inserted_inst.unique_id} | {inserted_inst.mnemonic} | {inserted_inst.syntax} | {inserted_inst.mop_count} | {inserted_inst.table_name}")
                # extracted_operands = Operand.select().where(Operand.instruction == inserted_inst)
                # for op in extracted_operands:
                #     print(f"       Text: {op.text}")
                #     print(f"       Type: {op.type}")
                #     print(f"       Role: {op.role}")
                #     print(f"       Size: {op.size}")
                #     print(f"       Element Size: {op.element_size}")
                #     print(f"       Is Optional: {op.is_optional}")

    print(f"Total instructions: {Instruction.select().count()}")
    print("Database populated successfully!")

# ✅ Automatically run if script is executed directly
if __name__ == "__main__":

    # Load ASL and USL JSON data, and convert JSON lists to dictionaries for quick lookup
    asl_json_path = "C:/Users/zbuchris/PycharmProjects/ArrowProject/Externals/db_manager/instruction_jsons/arm_asl_instructions.json"
    with open(asl_json_path, "r", encoding="utf-8") as f:
        asl_data = json.load(f)
    asl_dict = {inst["id"]: inst for inst in asl_data["instructions"]}

    usl_json_path = "C:/Users/zbuchris/PycharmProjects/ArrowProject/Externals/db_manager/instruction_jsons/arm_usl_instructions.json"
    with open(usl_json_path, "r", encoding="utf-8") as f:
        usl_data = json.load(f)
    usl_dict = {inst["id"]: inst for inst in usl_data["instructions"]}

    # Initialize database
    initialize_db()

    populate_database(asl_dict, usl_dict, force_reset=True)