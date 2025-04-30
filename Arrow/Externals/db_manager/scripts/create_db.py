import json
from peewee import SqliteDatabase, OperationalError
from Externals.db_manager.models import get_instruction_db, get_json_path, get_db_path
from Utils.logger_management import get_logger
import os

"""
Script: create_db.py

Description:
This script creates and populates an SQLite database (instructions.db) from JSON data 
in the `data/instructions.json` file. It is intended to be run only when updates 
are made to the JSON data, ensuring the database is up-to-date for application use. 

Functionality:
- Reads instruction data from `data/instructions.json`.
- Connects to the SQLite database located at `db/instructions.db`.
- Defines database tables based on models in `models.py` and creates them if they don’t exist.
- Inserts each instruction from the JSON file as a new record in the database.
- Closes the database connection once data loading is complete.

Usage:
Run this script from the project root to refresh the database with the latest JSON data:
    python Tool/scripts/create_db.py
"""


def create_db(architecture:str):
    '''
    1. Load the JSON File - Read the JSON file and load its content into a Python dictionary.
    2. Connect to SQLite Database - Establish a connection to an SQLite database file. If the file doesn’t exist, SQLite will create it.
    3. Create a Table - Define the database schema based on the structure of your JSON file.
    4. Insert Data - Iterate over the JSON data and insert it into the database.
    5. Close the Database Connection - Ensure the database connection is closed after all operations are completed.
    '''
    print(f"  ========== CREATE DB for '{architecture}' architecture")
    json_path = get_json_path(architecture)

    with open(json_path, 'r') as file:
        data = json.load(file)

    try:
        Instruction = get_instruction_db(architecture)
        db = Instruction._meta.database
        # Connect to the database
        db.connect()

        db.create_tables([Instruction], safe=True)

        # Load each instruction into the database
        for entry in data['instructions']:
            print(entry)
            instruction = Instruction.create(
                mnemonic=entry['mnemonic'],
                operands=json.dumps(entry['operands']),  # Store as JSON string
                #operand_size=entry['operand_size'],
                type_=entry['type'],
                group=entry['group'],
                architecture_modes=json.dumps(entry['architecture_modes']),  # Store as JSON string
                description=entry['description'],
                syntax=entry['syntax'],
            )
            if entry.get('random_generate') == "False":
                instruction.random_generate = False
            else:
                instruction.random_generate = True
            instruction.save()  # Save the change

    except OperationalError as e:
        logger = get_logger()
        # Check if the error message indicates a missing column
        if "no column named" in str(e):
            # Get the missing column name from the error message
            missing_column = str(e).split("no column named ")[-1]
            logger.error(f"Error: The '{missing_column}' field is missing in the database.")
            logger.error("Please delete your existing database file and create a new one to add the latest fields.")
        else:
            # Raise other operational errors that are not related to missing columns
            raise

    print("Data loaded into instructions.db successfully.")
    db.close()
