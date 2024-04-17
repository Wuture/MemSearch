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
# load_tools()

# print (available_functions)

# Write an intro to this script and print to terminal
print ("Press 'command + shift + space' on your current message window, and see AI do its magic!  \n")

# Function to encode the image
def encode_image(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')


# system_prompt = '''
# "You are an action recommendation system assistant on MacOS that recommends a set of actions user could take based on the screenshots and context user provides, be as detailed as possible. 
# The actions shxould be relevant to the user's current context and should help the user achieve their current task. 
# Rank you actions in order of relevancy. Then let user choose the action they want to take, and proceed to execute the action by calling the corresponding function.
# Only recommend actions that are available in the tools.json files, return a list of functions for users to choose.
# '''

today_date = datetime.date.today()


system_prompt = '''
Today's date is {today_date}.
You are an action recommendation system assistant on MacOS that recommends a set of actions, let user choose the action they want to take, and proceed to execute the action by calling the corresponding function.
You only recommend actions that are available in the tools. 
List all the options from 1~n, and let user choose the action they want to take.

e.g. 
1. Get weather
2. Get calendar events
3. Create a new event
4. Delete an event
5. Paraphrase a sentence

'''

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

    print (messages)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4-turbo",
        "messages": messages,
        "tools": available_tools,
        "tool_choice": "auto",
        "max_tokens": 100,
        "temperature": 0
    }

    print ("Pulling a list of actions...\n")
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    # message =  response.json()['choices'][0]['message']['content']
    response_json = response.json()
    print (response_json)

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

