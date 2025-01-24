import os
import requests
from datetime import datetime

# Airtable configuration
PERSONAL_ACCESS_TOKEN = os.getenv("AIRTABLE_PAT") # Retrieve the Airtable token from the environment variable set as GutHub secret
if not PERSONAL_ACCESS_TOKEN:
    raise ValueError("The Airtable token (AIRTABLE_PAT) is missing from the environment.")

BASE_ID = 'appOJKrcvb4gxH65d'
TABLE_NAME = 'run_statistics'

# Airtable API endpoint
URL = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"

# Function to upload run statistics
def upload_run_statistics(template, command_line, duration, architecture, cloud_mode, run_status:str="Pass"):

    headers = {
        "Authorization": f"Bearer {PERSONAL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    # Prepare the data to send
    data = {
        "fields": {
            "Template": str(template),
            "Command Line": command_line,
            "Duration": duration,
            "Status": run_status,
            "Architecture": architecture,
            "Cloud Mode": str(cloud_mode),
        }
    }

    # Send the POST request to Airtable
    response = requests.post(URL, headers=headers, json=data)

    # Check the response
    if response.status_code == 200:
        print("Run statistics uploaded successfully!")
    else:
        print(f"Failed to upload statistics: {response.status_code}")
        print(response.json())

