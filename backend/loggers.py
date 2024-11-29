import os
import json
from datetime import datetime, timezone

# Define the log folder and file
LOGIN_FOLDER = "logs"
LOGIN_LOG_FILE = os.path.join(LOGIN_FOLDER, "login.json")

# Ensure the folder exists
os.makedirs(LOGIN_FOLDER, exist_ok=True)

def log_login_to_json(user_id, ip_address, device_type, user_agent, status):
    # Create a log entry
    log_entry = {
        "user_id": user_id,
        "ip_address": ip_address,
        "device_type": device_type,
        "user_agent": user_agent,
        "status": status,
        "timestamp": datetime.now(timezone.utc).isoformat(),  # Updated timestamp method
    }

    # Read existing logs or initialize an empty list if the file doesn't exist
    try:
        if os.path.exists(LOGIN_LOG_FILE):
            with open(LOGIN_LOG_FILE, "r") as f:
                logs = json.load(f)
        else:
            logs = []
    
    except json.JSONDecodeError:  # Handle the case where the file is empty or corrupted
        logs = []

    # Append new log entry
    logs.append(log_entry)

    # Write the updated logs back to the file
    with open(LOGIN_LOG_FILE, "w") as f:
        json.dump(logs, f, indent=4)
