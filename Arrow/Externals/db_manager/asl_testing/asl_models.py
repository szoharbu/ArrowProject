import os
from peewee import Model, SqliteDatabase, CharField, IntegerField, ForeignKeyField, TextField, BooleanField

# Initialize SQLite Database
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_dir = os.path.join(base_dir, 'db')
if not os.path.exists(db_dir):
    raise ValueError(f" DB path doesn't exist: {db_dir}")
db_path = os.path.join(db_dir, 'arm_instructions_isalib.db')
db = SqliteDatabase(db_path)

class BaseModel(Model):
    class Meta:
        database = db  # Use the SQLite database

class Instruction(BaseModel):
    unique_id = CharField(unique=True, primary_key=True)  # Unique key: id + syntax
    id = CharField(index=True)  # Instruction ID (not unique)
    syntax = TextField()  # Assembly syntax variation
    description = TextField()  # Full instruction description
    mnemonic = CharField(null=True)  # From ASL
    instr_class = CharField(null=True)
    feature = CharField(null=True)
    iformid = CharField(null=True)
    #operands = TextField(null=True)  # From ASL
    mop_count = IntegerField(null=True)  # From USL
    table_name = CharField(null=True)  # From USL
    #latency_class = CharField(null=True)  # From USL
    max_latency = IntegerField(null=True)  # From USL
    steering_class = TextField(null=True)  # From USL , will store a JSON list of steering classes
    usl_flow = CharField(null=True)
    random_generate = BooleanField(default=False)  # New boolean flag with a default
    asl_info = TextField(null=True)  # Full ASL JSON
    usl_info = TextField(null=True)  # Full USL JSON
    is_valid = BooleanField(default=True)  # New boolean flag with a default
    # redundant fields to reduce the number of joins
    op1_role = CharField(null=True)
    op1_type = CharField(null=True)
    op1_size = IntegerField(null=True)
    op1_ismemory = BooleanField(default=False)
    op2_role = CharField(null=True)
    op2_type = CharField(null=True)
    op2_size = IntegerField(null=True)
    op2_ismemory = BooleanField(default=False)
    op3_role = CharField(null=True)
    op3_type = CharField(null=True)
    op3_size = IntegerField(null=True)
    op3_ismemory = BooleanField(default=False)
    op4_role = CharField(null=True)
    op4_type = CharField(null=True)
    op4_size = IntegerField(null=True)
    op4_ismemory = BooleanField(default=False)


    class Meta:
        database = db


class Operand(BaseModel):
    instruction = ForeignKeyField(Instruction, backref="operands", on_delete="CASCADE")
    text = CharField()
    full_text = CharField()
    syntax = CharField()
    type = CharField()
    type_category = CharField()
    role = CharField()
    size = IntegerField(null=True)
    index = IntegerField(null=True)
    width = IntegerField(null=True)
    element_size = IntegerField(null=True)
    extensions = TextField(null=True)  # a JSON list of extensions like .T, /M, etc
    is_optional = BooleanField(default=False)  # default to False
    is_memory = BooleanField(default=False)  # default to False
    memory_role = CharField()
    is_operand = BooleanField(default=True)  # New boolean flag with a default
    is_valid = BooleanField(default=True)  # New boolean flag with a default
    #anchors = TextField(null=True)  # Stored as JSON string

    class Meta:
        database = db


# Function to initialize the database
def initialize_db():
    db.connect(reuse_if_open=True)
    db.create_tables([Instruction, Operand], safe=True)
    db.close()
