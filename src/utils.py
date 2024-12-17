import json
import os

DATA_FILE = "data.json"

def load_data():
    # Check if the file exists
    if not os.path.exists(DATA_FILE):
        print(f"{DATA_FILE} does not exist.")
        # Create a default data structure and save it to a new file
        default_data = {
            "users": {}, 
            "expenses": []
            }
        save_data(default_data)
        return default_data
    
    print(f"{DATA_FILE} exists.")
    try:
        with open(DATA_FILE, 'r') as file:
            data = json.load(file)

        if "users" not in data:
            data["users"] = {}
        
        if "expenses" not in data:
            data["expenses"] = []

        save_data(data)
        return data
    
    except json.JSONDecodeError:
        # Handle corrupted JSON files gracefully
        print("Error: data.json is corrupted. Reinitializing.")
        default_data = {"users": {}, "groups": {}}
        save_data(default_data)
        return default_data

def save_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)
