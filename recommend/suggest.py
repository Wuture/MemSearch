from pynput import keyboard
import os
import base64
from io import BytesIO
import pyautogui
import json
import tools
import inspect
from openai import OpenAI
import requests
from app_utils import *
import datetime


# Check if the key exists
if "OPENAI_API_KEY" not in os.environ:
    print("OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable first.")

client = OpenAI()

# get openai api key from environment variable
api_key = os.environ.get("OPENAI_API_KEY")

messages = []

def load_tools():
    available_functions = {}
    available_tools = {}
    # load tools from tools.json
    with open("recommend/tools.json", "r") as file:
        available_tools = json.load(file)['tools']
    # Get all members of the tools module
    members = inspect.getmembers(tools)

    # load all functions from tools module
    for name, member in members:
        # Check if the member is a function
        if inspect.isfunction(member):
            # Add the function to the available_functions dictionary
            available_functions[name] = member

    return available_tools, available_functions

available_tools, available_functions = load_tools()

# Write an intro to this script and print to terminal
print ("Press 'command + shift' on your current message window, and see AI do its magic!  \n")

today_date = datetime.date.today()

system_prompt = f'''
Today's date is {today_date}.
You are an action recommendation system assistant on MacOS that recommends a set of actions, let user choose the action they want to take, and proceed to execute the action by calling the corresponding function.
You only recommend actions that are available in the tools. 
List all the options from 1~n, and let user choose the action they want to take.
After user finished the action, proactively suggest more actions for user to take based on current context.
If you don't know what time and date it is, call the function get_current_time_and_date() to get the current time and date.

'''

# system_prompt = '''
# Today's date is {today_date}.
# You are an action recommendation system assistant on MacOS that recommends a set of actions user could take based on the screenshots and context user provides, be as detailed as possible.
# Let user choose the action they want to take, and proceed to execute the action by calling the corresponding function.

# Return a list of actions available as json objects, with the following format:

# {
#     "actions": [
#         {
#             "action": "Get weather",
#             "description": "Get the current weather based at San Francisco",
#             "confidence": 0.9
#             "function_name": get_current_weather,
#             "function_args": ["location": "San Francisco", "unit": "F"]
#         },
#         {
#             "action": "Get calendar events",
#             "description": "Get the calendar events for a specific date",
#             "confidence": 0.8
#             "function_name": get_events, 
#             "function_args": { "start_date": "2022-01-01", "end_date": "2022-01-31" }
#         }
#     ]
# }
# '''

# Send context to GPT-4 and ask for a list of actions
def get_context (image):
    print ("Preparing an response!\n")
    base64_image = encode_image(image)

    # Prepare system message for gpt4v
    system = {
        "role": "system",
        "content": [
            {
            "type": "text",
            "text": system_prompt,
            },
        ]

    }

    user_query =  {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": "Give me a list of actions i could do based on the screenshot and context that i provided, and number them. Allow me to choose 1 of the actions to execute."
            },
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
            }
        ]
    }

    messages = [system, user_query]

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4-turbo",
        "messages": messages,
        "tools": available_tools,
        "tool_choice": "auto",
        # "response_format": { "type": "json_object" },
        "max_tokens": 300,
        "temperature": 0
    }

    print ("Pulling a list of actions...\n")
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    # message =  response.json()['choices'][0]['message']['content']
    response_json = response.json()

    print (response_json)

    # print (message + "\n")

    # choice = int(input("> Enter the number of the action you want to take: "))
    
        # Extract action choices from the response
    actions = json.loads(response_json['choices'][0]['message']['content'])['actions']
    
    # Print each action with its details
    for idx, action in enumerate(actions, start=1):
        print(f"{idx}: {action['action']}")
        print(f"Description: {action['description']}")
        print(f"Confidence: {action['confidence']}\n")
    
    # Ask user to choose an action
    try:
        choice = int(input("Enter the number of the action you want to take: "))
        selected_action = actions[choice - 1]  # Subtract 1 to match list index
        print(f"You selected: {selected_action['action']}")

        print (selected_action)
        
        # Check if the selected action has a function to call
        if 'function_name' in selected_action and selected_action['function_name'] is not None:
            # Get the function name and arguments
            function_name = selected_action['function_name'].split(".")[1]
            function_args = selected_action['function_args']

            print (function_name)
            print (function_args)

            # Call the selected function with arguments
            if function_name in available_functions:
                print(f"Calling function: {function_name}")
                function_to_call = available_functions[function_name]
                function_response = function_to_call(**function_args)
                print(f"Function response: {function_response}")
            else:
                print(f"Function '{function_name}' is not available.")
        else:
            print("No function call available for the selected action.")
    
    except (ValueError, IndexError):
        print("Invalid choice. Please enter a valid number.")


def prepare_imessage(message):
    # Type and send the message
    pyautogui.write(message)
    # pyautogui.press('return')

def on_activate():
    screenshot, app_name, window_name = get_active_window_screenshot()

    # compress the screenshot
    screenshot = screenshot.resize((screenshot.width, screenshot.height))

    # show image in preview
    # screenshot.show()

    # send_to_gpt4v(screenshot)
    get_context(screenshot)

def for_canonical(f):
    # Convert the key to a canonical version
    return lambda k: f(keyboard.Key.canonical(k))

# The key combination to check
# HOTKEYS = {keyboard.Key.cmd, keyboard.Key.shift, keyboard.Key.space}
HOTKEYS = {keyboard.Key.cmd, keyboard.Key.shift}

# The currently active modifiers
current = set()

def on_press(key):
    if any([key in HOTKEYS, key in current]):
        current.add(key)
        if all(k in current for k in HOTKEYS):
            on_activate()  # Call screenshot function if all modifiers are pressed

def on_release(key):
    try:
        current.remove(key)
    except KeyError:
        pass

# Listener for keyboard events
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

