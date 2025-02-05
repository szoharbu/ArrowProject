import requests


## Airtable API endpoint
# BASE_ID = 'appOJKrcvb4gxH65d'
# TABLE_NAME = 'run_statistics'
# URL = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"

# Function to upload run statistics
def upload_run_statistics(template, command_line, duration, architecture, cloud_mode, system_metadata, user_id, run_status:str="Pass"):

    """Send data to the backend for asynchronous Airtable upload."""

    UPLOAD_URL = "https://szoharbu.pythonanywhere.com/upload"

    '''
    To view Airtable statistics:
    - enter: https://airtable.com/appOJKrcvb4gxH65d/tblWab8HLi2azhcxJ
    
    To debug PythoneAnywhare issues:
    - enter https://www.pythonanywhere.com/user/szoharbu/
    - click on the Web tab
    - see Error log 
    '''

    upload_data = {
            "Template": str(template),
            "Command Line": command_line,
            "Duration": duration,
            "Status": run_status,
            "Architecture": architecture,
            "Cloud Mode": str(cloud_mode),
            "User Identifier": user_id,
            "System Metadata": system_metadata
    }

    try:
        headers = {"Content-Type": "application/json"}
        requests.post(UPLOAD_URL, json=upload_data, headers=headers)
        print("Data sent to backend successfully.")
    except requests.exceptions.RequestException as e:
        print("Failed to send data to backend:", e)

