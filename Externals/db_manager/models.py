import os
from peewee import Model, CharField, TextField, SqliteDatabase, BooleanField
from Utils.configuration_management import Configuration
from Utils.logger_management import get_logger

"""
File: models.py

Description:
This file defines the data models for the SQLite database using the `Peewee` ORM.
The models represent the structure of the tables in the `instructions.db` database, 
allowing the application to interact with the database using Python objects rather than raw SQL.

Models:
- `Instruction`: Represents a single instruction in the database, with fields for 
  mnemonic, operands, operand_size, type, group, description, architecture_modes, and syntax.
  
  architecture_modes differentiate between "RV32" and "RV64" 

Usage:
Import these models into other scripts to interact with the database:
    from Tool.db_manager.models import Instruction

Example:
    # Query all arithmetic instructions
    arithmetic_instructions = Instruction.select().where(Instruction.group == 'arithmetic')
"""


# Function to dynamically select and initialize the database
def get_database(architecture:str=None):
    """Initialize and return the database for the given architecture."""

    if architecture:
        # Map architecture to database file
        db_files = {
            "x86": "x86_instructions.db",
            "riscv": "riscv_instructions.db",
            "arm": "arm_instructions.db",
        }

        if architecture not in db_files:
            raise ValueError(f"Unknown Architecture requested: {architecture}")

        db_file = db_files[architecture]
    else:
        if Configuration.Architecture.x86:
            db_file = 'x86_instructions.db'
        elif Configuration.Architecture.riscv:
            db_file = 'riscv_instructions.db'
        elif Configuration.Architecture.arm:
            db_file = 'arm_instructions.db'
        else:
            raise ValueError(f"Unknown Architecture requested")

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(BASE_DIR, 'db_manager', 'db', db_file)

    if not os.path.exists(db_path) and not architecture:
        raise ValueError(f'Unknown SqliteDatabase path {db_path}')

    logger = get_logger()
    logger.debug(f'======================== using SqliteDatabase with {db_path}')
    return SqliteDatabase(db_path)

# Instruction Model
class Instruction(Model):
    mnemonic = CharField()
    operands = TextField()  # JSON string for operands (nested)
    #operand_size = CharField()
    type_ = CharField()
    group = CharField()
    description = TextField()
    architecture_modes = TextField()  # JSON string for operands
    syntax = TextField()
    random_generate = BooleanField(default=False)  # New boolean flag with a default

    class Meta:
        database = None  # Placeholder; set dynamically using `bind_to_database`

    @classmethod
    def bind_to_database(cls, database):
        """Bind the Instruction model to a specific database."""
        cls._meta.database = database


# Add a caching mechanism for bound models
_model_cache = {}

def get_instruction_db(architecture:str=None):
    """Get a cached Instruction model or create a new one bound to the correct database."""
    global _model_cache
    if architecture not in _model_cache:
        db = get_database(architecture)

        # Properly rebind the model to the new database
        Instruction.bind_to_database(db)

        # Reset the database connection state (if lingering)
        if not db.is_closed():
            db.close()

        _model_cache[architecture] = Instruction

    return _model_cache[architecture]
