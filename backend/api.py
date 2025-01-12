import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins; replace "*" with specific domains in production
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all HTTP headers
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Backend directory
RULES_FILE = os.path.join(BASE_DIR, "logs", "rules.json")  # Logs directory

@app.get("/")
def get_root():
    return {"message":"Hello World!"}

@app.get("/rules")
def get_rules():
    try:
        # Check if the file exists
        if not os.path.exists(RULES_FILE):
            with open(RULES_FILE, "w") as file:
                json.dump([], file)  # Create an empty JSON array if it doesn't exist

        with open(RULES_FILE, "r") as file:
            try:
                data = json.load(file)  # Load the JSON data
                if isinstance(data, list):
                    return data  # Return the list of rules if valid
                else:
                    return []  # Return an empty list if data is not a list
            except json.JSONDecodeError:
                return []  # Handle empty or invalid JSON by returning an empty list
    except Exception as e:
        return {"error": str(e)}

@app.post("/rules")
def add_rule(rule: dict):
    try:
        if not os.path.exists(RULES_FILE):
            with open(RULES_FILE, "w") as file:
                json.dump([], file)  # Create an empty JSON array if it doesn't exist

        with open(RULES_FILE, "r+") as file:
            try:
                rules = json.load(file)  # Load existing rules
                if not isinstance(rules, list):
                    rules = []  # Reset to an empty list if the file content is invalid
            except json.JSONDecodeError:
                rules = []  # Handle invalid JSON by resetting to an empty list

            rules.append(rule)  # Add the new rule
            file.seek(0)
            json.dump(rules, file, indent=4)  # Write back updated rules
        return {"message": "Rule added", "rule": rule}
    except Exception as e:
        return {"error": str(e)}