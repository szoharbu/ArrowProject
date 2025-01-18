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

def get_json_path(architecture:str=None):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if architecture:
        json_file = f"{architecture}_instructions.json"
    else:
        json_file = f"{Configuration.Architecture.arch_str}_instructions.json"
    json_path = os.path.join(base_dir, 'db_manager', 'instruction_jsons', json_file)
    if not os.path.exists(json_path):
        raise ValueError(f"Couldn't find json_path : {json_path}")
    return json_path


def get_db_path(architecture: str = None, check_exist=False):
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_dir = os.path.join(base_dir, 'db_manager', 'db')
    os.makedirs(db_dir, exist_ok=True) # Create the directory if it doesn't exist

    if architecture:
        db_file = f"{architecture}_instructions.db"
    else:
        db_file = f"{Configuration.Architecture.arch_str}_instructions.db"
    db_path = os.path.join(db_dir , db_file)


    if check_exist and not os.path.exists(db_path):
        raise ValueError(f"Couldn't find db_path : {db_path}")

    return db_path


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


# Factory function to retrieve the InstructionDB instance
def get_instruction_db(architecture:str=None):
    """Get a cached Instruction model or create a new one bound to the correct database."""
    # Access or initialize the singleton variable
    model_cache_instance = SingletonManager.get("model_cache_instance", default=None)

    if architecture is None:
        architecture = Configuration.Architecture.arch_str

    if model_cache_instance is None:
        model_cache_instance = {}

    if architecture not in model_cache_instance:
        db_path = get_db_path(architecture)
        sql_db = SqliteDatabase(db_path)
        # Properly rebind the model to the new database
        Instruction.bind_to_database(sql_db)
        # Reset the database connection state (if lingering)
        if not sql_db.is_closed():
            sql_db.close()
        model_cache_instance[architecture] = Instruction

        SingletonManager.set("model_cache_instance", model_cache_instance)

    return model_cache_instance[architecture]
