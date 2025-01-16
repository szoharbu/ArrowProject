from pyairtable import Table
from datetime import datetime

# Set your API key and base ID
API_KEY = "your_airtable_api_key"
BASE_ID = "your_base_id"
TABLE_NAME = "Tool Runs"

# Connect to the table
table = Table(API_KEY, BASE_ID, TABLE_NAME)

# Prepare data
tool_run_data = {
    "User": "user_123",
    "Timestamp": datetime.now().isoformat(),
    "Command": "--example-command",
    "Environment": "Python 3.9, Ubuntu 20.04",
    "Generated Content": "Random output content",
}

# Insert data
table.create(tool_run_data)
