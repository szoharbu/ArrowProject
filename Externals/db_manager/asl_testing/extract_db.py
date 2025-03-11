import os
import datetime
import re
from asl_models import Instruction, Operand
from peewee import SqliteDatabase, fn

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(base_dir, 'db', 'arm_instructions_isalib.db')
# Check if the file exists
if not os.path.exists(db_path):
    raise ValueError(f"SQL DB file not found: {db_path}")
#db_path = "C:/Users/zbuchris/PycharmProjects/ArrowProject/Externals/db_manager/asl_testing/instructions.db"


def return_last_modified_date():
    # Get the last modified time of the file
    if os.path.exists(db_path):
        last_modified_timestamp = os.path.getmtime(db_path)
        last_modified_datetime = datetime.datetime.fromtimestamp(last_modified_timestamp)

        # Format the date nicely
        formatted_date = last_modified_datetime.strftime("%Y-%m-%d %H:%M:%S")

        return f"📅 **Last update:** {formatted_date}"
    else:
        return "⚠️ Database file not found."

def load_db():
    sql_db = SqliteDatabase(db_path)
    Instruction._meta.database = sql_db
    Operand._meta.database = sql_db

    sql_db.connect()

    # db_path = "C:/Users/zbuchris/PycharmProjects/ArrowProject/Externals/db_manager/asl_testing/instructions.db"
    # sql_db = SqliteDatabase(db_path)
    # asl_models.Instruction._meta.database = sql_db
    # asl_models.Operand._meta.database = sql_db
    #
    # sql_db.connect()
    # Instruction = asl_models.Instruction
    # Operand = asl_models.Operand

    return Instruction, Operand


def get_unique_values(field_name):
    """Fetch unique values from a given field in the Instruction table."""
    Instruction, Operand  = load_db()

    try:
        query = Instruction.select(getattr(Instruction, field_name)).distinct()
        unique_values = set()  # Use a set to ensure uniqueness
        for row in query:
            field_value = getattr(row, field_name)
            if field_value:  # Ensure value is not None or empty
                if isinstance(field_value, str):
                    cleaned_value = re.sub(r'[\[\]"]', '', field_value)
                    # If it's a string, split on commas and strip spaces
                    unique_values.update(value.strip() for value in cleaned_value.split(","))
                else:
                    unique_values.add(field_value)  # Handle non-string values safely
        return sorted(unique_values)  # Return a sorted list for UI consistency

    except AttributeError:
        print(f"Error: Field '{field_name}' does not exist in the Instruction table.")
        return []


def extract(selected_project,
            instr_query=None,
            mnemonic=None,
            src_size=None,
            src_type=None,
            dest_size=None,
            dest_type=None,
            steering_classes=None,
            max_latency=None,
            ):
    """Extracts instructions matching the given filters while reducing joins."""

    if selected_project != "Olympus":
        raise ValueError(f"Project {selected_project} is not yet supported")

    Instruction, Operand  = load_db()

    query = Instruction.select()

    if instr_query:
        query = query.where(eval(instr_query))

    if mnemonic:
        if not mnemonic.startswith('"') or not mnemonic.endswith('"'):
            mnemonic = f'"{mnemonic}"'
        query = query.where(Instruction.mnemonic.contains(eval(mnemonic)))

    if src_size:
        query = query.where(
            (Instruction.src1_size == src_size) |
            (Instruction.src2_size == src_size) |
            (Instruction.src3_size == src_size) |
            (Instruction.src4_size == src_size)
        )
    if src_type:
        query = query.where(
            (Instruction.src1_type == src_type) |
            (Instruction.src2_type == src_type) |
            (Instruction.src3_type == src_type) |
            (Instruction.src4_type == src_type)
        )
    if dest_size:
        query = query.where(
            (Instruction.dest1_size == dest_size) |
            (Instruction.dest2_size == dest_size)
        )
    if dest_type:
        query = query.where(
            (Instruction.dest1_type == dest_type) |
            (Instruction.dest2_type == dest_type)
        )
    if steering_classes:
        conditions = None  # Initialize conditions
        # Loop through selected steering classes and build the condition
        for value in steering_classes:
            condition = Instruction.steering_class.contains(value)
            #conditions = condition if conditions is None else conditions | condition  # Use bitwise OR |
            conditions = condition if conditions is None else conditions & condition  # Use bitwise AND &
        # Apply conditions to the query
        query = query.where(conditions)
        # query = query.where(Instruction.steering_class.contains(steering_classes))
    if max_latency:
        query = query.where(Instruction.max_latency==max_latency)


    return query

if __name__ == "__main__":

    print("zzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzzz")
    #
    print(f"Total instructions: {Instruction.select().count()}")

    #
    # query = Instruction.select().where(Instruction.mnemonic == "add" and Instruction.operands['role'] == "src")
    # print(f"Total instructions: {Instruction.select().count()}")

    query = (Instruction.select().join(Operand).where(
        (Operand.role == "DEST") & (Operand.type == "PREDICATE") &
        (Operand.instruction_id << Operand.select(Operand.instruction_id)
         .where((Operand.role == "SRC") & (Operand.type == "SVE"))))
        .distinct())

    print(f"Total instructions under dest_pred_src_sve:  { len(query)}")

    query = extract(src_type="SVE", dest_type="PREDICATE")
    print(f"Total instructions under dest_pred_src_sve:  { len(query)}")

    query = extract(instr_query=Instruction.mnemonic == "add", src_type="SIMD_FPR")
    print(f"Instructions with `add` and SIMD: {len(query)}")

    query = extract(instr_query=Instruction.max_latency == 4)
    print(f"Instructions with latency==4 : {len(query)}")

    query = extract(instr_query=Instruction.max_latency == 2)
    print(f"Instructions with latency==2 : {len(query)}")

    query = extract(instr_query=Instruction.max_latency == 2, dest_type="SIMD_FPR")
    print(f"Instructions with latency==2 : {len(query)}")


    query = extract(instr_query=Instruction.steering_class.contains("mx_pred"))
    print(f"Instructions with steering_class=mx_pred : {len(query)}")
    query = Instruction.select().where(Instruction.steering_class.contains("mx_pred"))
    print(f"Instructions with steering_class=mx_pred : {len(query)}")

    query = extract(instr_query=Instruction.steering_class.contains("mx_pred") & Instruction.max_latency == 1)
    print(f"Instructions with steering_class=mx_pred and max_latency=1 : {len(query)}")
    query = extract(instr_query=Instruction.steering_class.contains("mx_pred") & Instruction.max_latency == 2)
    print(f"Instructions with steering_class=mx_pred and max_latency=2 : {len(query)}")


    query = extract(instr_query=Instruction.steering_class.contains("mx"))
    print(f"Instructions with steering_class=mx: {len(query)}")
    query = extract(instr_query=Instruction.max_latency == 2)
    print(f"Instructions with max_latency=2 : {len(query)}")

    query = extract(instr_query=(Instruction.steering_class.contains("mx")) & (Instruction.max_latency == 1))
    print(f"Instructions with steering_class=mx & max_latency=1 : {len(query)}")

    query = extract(instr_query=(Instruction.steering_class.contains("mx")) & (Instruction.max_latency == 2))
    print(f"Instructions with steering_class=mx & max_latency=2 : {len(query)}")

    query = extract(instr_query=(Instruction.steering_class.contains("mx")) & (Instruction.max_latency == 3))
    print(f"Instructions with steering_class=mx & max_latency=3 : {len(query)}")

    query = extract(instr_query=(Instruction.steering_class.contains("mx")) & (Instruction.max_latency == 4))
    print(f"Instructions with steering_class=mx & max_latency=4 : {len(query)}")

    query = extract(instr_query=(Instruction.steering_class.contains("mx")) & (Instruction.max_latency == 5))
    print(f"Instructions with steering_class=mx & max_latency=5 : {len(query)}")

    query = extract(instr_query=(Instruction.steering_class.contains("vx_v2g")))
    print(f"Instructions with steering_class=vx_v2g : {len(query)}")

    query = extract(instr_query=(Instruction.steering_class.contains("vx_v2g")), dest_type="SIMD_FPR")
    print(f"Instructions with steering_class=vx_v2g and dest_type=SIMD : {len(query)}")

    query = extract(instr_query=(Instruction.steering_class.contains("vx_v2g")), src_type="SVE")
    print(f"Instructions with steering_class=vx_v2g and src_type=SVE : {len(query)}")

    for inst in query:
        print(f"----- {inst.id}")
        print(f"  syntax {inst.syntax}")
        #print(f"  mnemonic {inst.mnemonic}")
        #print(f"  operands {inst.operands}")
        #print(f"  mop_count {inst.mop_count}")
        #print(f"  table_name {inst.table_name}")
        for op in inst.operands:
            print(f"      Operand: {op.text} {op.type} {op.role}")

