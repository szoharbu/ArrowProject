import os
import json
from peewee import Model, CharField, TextField, SqliteDatabase, BooleanField
from Arrow.Utils.configuration_management import Configuration
from Arrow.Utils.logger_management import get_logger
from Arrow.Utils.singleton_management import SingletonManager

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
    from Arrow.Tool.db_manager.models import Instruction

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


class SimpleOperand:
    """
    Lightweight operand class that mimics ARM Operand object interface.
    Used for RISC-V/x86 to provide consistent operand interface across architectures.
    """
    def __init__(self, index, role=None, type=None, size=None, is_memory=False):
        self.index = index
        self.role = role
        self.type = type
        self.size = size
        self.is_memory = is_memory
        self.is_operand = True  # Always true for actual operands
        self.memory_role = 'base' if is_memory and 'basereg' in (type or '') else None
        # Additional attributes for compatibility
        self.is_valid = True
        self.is_optional = False
        self.text = f"op{index}"
        self.full_text = f"operand_{index}"
        self.type_category = "register" if not is_memory else "memory"
        self.width = None
        self.extensions = None


# Instruction Model
class Instruction(Model):
    mnemonic = CharField()
    operands = TextField()  # JSON string for operands (nested)
    #operand_size = CharField()
    type_ = CharField()
    group = CharField()
    description = TextField()
    extension = TextField() # JSON string for extension
    architecture_modes = TextField()  # JSON string for architecture modes
    syntax = TextField()
    random_generate = BooleanField(default=False)  # New boolean flag with a default
    is_valid = BooleanField(default=True)  # Whether instruction is valid/parsed correctly
    
    # Denormalized operand fields for faster queries (avoiding joins)
    # These duplicate info from the operands JSON for performance
    op1_role = CharField(null=True)
    op1_type = CharField(null=True)
    op1_size = CharField(null=True)  # Keep as CharField to handle various size formats
    op1_ismemory = BooleanField(default=False)
    op2_role = CharField(null=True)
    op2_type = CharField(null=True)
    op2_size = CharField(null=True)
    op2_ismemory = BooleanField(default=False)
    op3_role = CharField(null=True)
    op3_type = CharField(null=True)
    op3_size = CharField(null=True)
    op3_ismemory = BooleanField(default=False)
    op4_role = CharField(null=True)
    op4_type = CharField(null=True)
    op4_size = CharField(null=True)
    op4_ismemory = BooleanField(default=False)

    class Meta:
        database = None  # Placeholder; set dynamically using `bind_to_database`

    @classmethod
    def bind_to_database(cls, database):
        """Bind the Instruction model to a specific database."""
        cls._meta.database = database
    
    def get_operands_as_objects(self):
        """
        Get operands as objects for consistent interface across architectures.
        For RISC-V/x86, creates SimpleOperand objects from denormalized fields.
        For ARM, this would return the actual Operand objects.
        """
        operands_list = []
        
        # Build operands from denormalized fields (up to 4 operands)
        for i in range(1, 5):
            role = getattr(self, f'op{i}_role', None)
            if role is None:
                # No more operands
                break
            
            op_type = getattr(self, f'op{i}_type', None)
            op_size = getattr(self, f'op{i}_size', None)
            op_is_memory = getattr(self, f'op{i}_ismemory', False)
            
            operand = SimpleOperand(
                index=i,
                role=role,
                type=op_type,
                size=op_size,
                is_memory=op_is_memory
            )
            operands_list.append(operand)
        
        return operands_list


# Factory function to retrieve the InstructionDB instance
def get_instruction_db(architecture:str=None):
    """Get a cached Instruction model or create a new one bound to the correct database.
    
    Args:
        architecture: Target architecture (defaults to current config)
    
    Returns:
        For ARM with Asl_extract=True: dict with 'Instruction' and 'Operand' models
        For other cases: Instruction model only
    """
    
    # Access or initialize the singleton variable
    model_cache_instance = SingletonManager.get("model_cache_instance", default=None)

    if architecture is None:
        architecture = Configuration.Architecture.arch_str

    if model_cache_instance is None:
        model_cache_instance = {}


    if architecture not in model_cache_instance:
        if architecture == 'arm':
            # ARM ASL case with optimized pragmas
            from Arrow.Externals.db_manager.asl_testing import asl_models
            
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            db_path = os.path.join(base_dir, 'db_manager', 'db', 'arm_instructions_isalib.db')
            
            if not os.path.exists(db_path):
                raise ValueError(f"SQL DB file not found: {db_path}")
            
            # Create optimized SQLite connection for read-only, single-process usage
            sql_db = SqliteDatabase(db_path, pragmas={
                # Memory and caching
                'cache_size': -64000,       # 64MB cache (negative = KB)
                'temp_store': 'memory',     # Store temp tables/indices in memory
                'mmap_size': 268435456,     # 256MB memory-mapped I/O
                
                # Performance optimizations (safe for read-only, single-process)
                'journal_mode': 'off',      # No journaling needed for read-only (fastest)
                'synchronous': 'off',       # No sync needed for read-only (fastest)
                'locking_mode': 'exclusive', # Exclusive lock for single-process (faster)
                
                # Read-only optimizations
                'query_only': 'true',       # Read-only mode (safe since you never write)
                'read_uncommitted': 'true', # Allow dirty reads (safe for single-process read-only)
                
                # Query and connection optimizations
                'optimize': None,           # Run PRAGMA optimize on connection
            })
            
            asl_models.Instruction._meta.database = sql_db
            asl_models.Operand._meta.database = sql_db
            sql_db.connect()
            
            # Cache both Instruction and Operand models
            model_cache_instance[architecture] = {
                'Instruction': asl_models.Instruction,
                'Operand': asl_models.Operand
            }
        else:
            # Standard case for other architectures or ARM without ASL
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
