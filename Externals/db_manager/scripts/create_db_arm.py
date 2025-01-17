from Externals.db_manager.scripts.create_db import create_db

"""
Script: create_db_arm.py

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
    python Tool/scripts/create_db_arm.py
"""


if __name__ == "__main__":
    #load_json_to_db()
    create_db("arm")
