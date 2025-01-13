import json
from peewee import SqliteDatabase, OperationalError
from Tool.db_manager.models import get_instruction_db
import os

"""
Script: create_db_riscv.py

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
    python Tool/scripts/create_db_riscv.py
"""


# Initialize the database
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(BASE_DIR, 'db_manager', 'db', 'x86_instructions.db')
# Check and deleter if the file exists
if os.path.exists(db_path):
    os.remove(db_path)  # Delete the file
db = SqliteDatabase(db_path)



def load_json_to_db():
    # Open and read the JSON data

    json_path = os.path.join(BASE_DIR, 'instruction_jsons', 'x86_instructions.json')

    # Check if the template file exists
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"The template file does not exist: {json_path}")

    print(json_path)
    with open(json_path, 'r') as file:
        data = json.load(file)


    try:
        Instruction = get_instruction_db("x86")
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
                syntax=entry['syntax']
            )
            if entry.get('random_generate') == "False":
                instruction.random_generate = False
            else:
                instruction.random_generate = True
            instruction.save()  # Save the change

    except OperationalError as e:
        # Check if the error message indicates a missing column
        if "no column named" in str(e):
            # Get the missing column name from the error message
            missing_column = str(e).split("no column named ")[-1]
            print(f"Error: The '{missing_column}' field is missing in the database.")
            print("Please delete your existing database file and create a new one to add the latest fields.")
        else:
            # Raise other operational errors that are not related to missing columns
            raise

    print("Data loaded into instructions.db successfully.")
    db.close()


if __name__ == "__main__":
    load_json_to_db()
