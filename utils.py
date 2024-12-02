import json
import os

DATA_FILE = "data.json"

def load_data():
    # Check if the file exists
    if not os.path.exists(DATA_FILE):
        # Create a default data structure and save it to a new file
        default_data = {"users": {}, "groups": {}}
        save_data(default_data)
        return default_data

    # If the file exists, load and return the data
    try:
        with open(DATA_FILE, 'r') as file:
            return json.load(file)
    except json.JSONDecodeError:
        # Handle corrupted JSON files gracefully
        print("Error: data.json is corrupted. Reinitializing.")
        default_data = {"users": {}, "groups": {}}
        save_data(default_data)
        return default_data

def save_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)
