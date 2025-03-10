from peewee import Model, SqliteDatabase, CharField, IntegerField, ForeignKeyField, TextField, BooleanField

# Initialize SQLite Database
db = SqliteDatabase("instructions.db")

class BaseModel(Model):
    class Meta:
        database = db  # Use the SQLite database

class Instruction(BaseModel):
    unique_id = CharField(unique=True, primary_key=True)  # Unique key: id + syntax
    id = CharField(index=True)  # Instruction ID (not unique)
    syntax = TextField()  # Assembly syntax variation
    description = TextField()  # Full instruction description
    mnemonic = CharField(null=True)  # From ASL
    #operands = TextField(null=True)  # From ASL
    mop_count = IntegerField(null=True)  # From USL
    table_name = CharField(null=True)  # From USL
    #latency_class = CharField(null=True)  # From USL
    max_latency = IntegerField(null=True)  # From USL
    steering_class = TextField(null=True)  # From USL , will store a JSON list of steering classes
    random_generate = BooleanField(default=False)  # New boolean flag with a default
    asl_info = TextField(null=True)  # Full ASL JSON
    usl_info = TextField(null=True)  # Full USL JSON

    # redundant fields to reduce the number of joins
    src1_size = IntegerField(null=True)
    src1_type = CharField(null=True)
    src2_size = IntegerField(null=True)
    src2_type = CharField(null=True)
    src3_size = IntegerField(null=True)
    src3_type = CharField(null=True)
    src4_size = IntegerField(null=True)
    src4_type = CharField(null=True)
    dest1_size = IntegerField(null=True)
    dest1_type = CharField(null=True)
    dest2_size = IntegerField(null=True)
    dest2_type = CharField(null=True)

    class Meta:
        database = db


class Operand(BaseModel):
    instruction = ForeignKeyField(Instruction, backref="operands", on_delete="CASCADE")
    text = CharField()
    type = CharField()
    role = CharField()
    size = IntegerField(null=True)
    element_size = IntegerField(null=True)
    is_optional = IntegerField(default=0)  # 0 = False, 1 = True
    #anchors = TextField(null=True)  # Stored as JSON string

    class Meta:
        database = db


# Function to initialize the database
def initialize_db():
    db.connect(reuse_if_open=True)
    db.create_tables([Instruction, Operand], safe=True)
    db.close()

# def execute_query(expression):
#     """
#     Execute a Peewee query using overloaded operators.
#     """
#     try:
#         query = (Instruction
#                  .select()
#                  .join(ForeignKeyField("Operand", backref="operands"), on=(Instruction.id == ForeignKeyField("Operand", backref="operands").instruction))
#                  .where(expression.condition))
#
#         # Convert results to JSON
#         result = [
#             {
#                 "id": instr.id,
#                 "unique_id": instr.unique_id,
#                 "mnemonic": instr.mnemonic,
#                 "syntax": instr.syntax,
#                 "mop_count": instr.mop_count,
#                 "latency": instr.latency,
#                 "table_name": instr.table_name
#             }
#             for instr in query
#         ]
#
#         return json.dumps(result, indent=4)
#
#     except Exception as e:
#         return json.dumps({"error": str(e)})