import requests
import json
import os
# import contacts
# import inspect

# contacts = contacts.Contacts()

# Get functions from contacts module
# members = inspect.getmembers(contacts)

# Get ACCESS_TOKEN from environment variable
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
import datetime
import platform
import subprocess
from app_utils import run_applescript, run_applescript_capture
import pyautogui

calendar_app = "Calendar"

# function_schema = {
#     "name": "execute",
#     "description": "Executes code on the user's machine **in the users local environment** and returns the output",
#     "parameters": {
#         "type": "object",
#         "properties": {
#             "language": {
#                 "type": "string",
#                 "description": "The programming language (required parameter to the `execute` function)",
#                 "enum": [
#                     # This will be filled dynamically with the languages OI has access to.
#                 ],
#             },
#             "code": {"type": "string", "description": "The code to execute (required)"},
#         },
#         "required": ["language", "code"],
#     },
# }

# Example dummy function hard coded to return the same weather
# In production, this could be your backend API or an external API
def get_current_weather(location, unit="fahrenheit"):
    """Get the current weather in a given location"""
    if "tokyo" in location.lower():
        return json.dumps({"location": "Tokyo", "temperature": "10", "unit": unit})
    elif "san francisco" in location.lower():
        return json.dumps({"location": "San Francisco", "temperature": "72", "unit": unit})
    elif "paris" in location.lower():
        return json.dumps({"location": "Paris", "temperature": "22", "unit": unit})
    else:
        return json.dumps({"location": location, "temperature": "unknown"})

# Function to call the external API for paraphrasing
def paraphrase_text(text, plan="paid", prefer_gpt="gpt3", custom_style="", language="EN_US"):
    url = "https://api-yomu-writer-470e5c0e3608.herokuapp.com/paraphrase"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "ACCESS_TOKEN": f"{ACCESS_TOKEN}"
    }
    payload = json.dumps({
        "text": text,
        "plan": plan,
        "prefer_gpt": prefer_gpt,
        "custom_style": custom_style,
        "language": language
    })

    response = requests.post(url, headers=headers, data=payload)
    if response.status_code == 200:
        print (response.json())
        return response.json()  # Return the JSON response from the API
    else:
        return {"error": "Failed to fetch data", "status_code": response.status_code}

def reply_message(message):
    # Type and send the message
    pyautogui.write(message)
    # pyautogui.press('return')
