from pynput import keyboard
import os
import json
import tools.functions as functions
import inspect
from openai import OpenAI
import requests
from app_utils import *
import datetime
from tools.MySocalApp import auto_event_scheduler
from tools.contacts import Contacts
from tools.mail import Mail
from tools.sms import SMS
from tools.Calendar import Calendar
import pytesseract


# Check if the key exists
if "OPENAI_API_KEY" not in os.environ:
    print("OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable first.")

# get openai api key from environment variable
client = OpenAI()
api_key = os.environ.get("OPENAI_API_KEY")

messages = []

today_date = datetime.date.today()

system_prompt = f'''
Today's date is {today_date}.
You are an action recommendation system assistant on MacOS that recommends a set of actions based on current context and screenshots that the user provides, let user choose the action they want to take, and proceed to execute the action by calling the corresponding function.
You only recommend actions that are available in the tools provided. 
List all the options from 1~n, and let user choose the action they want to take.
After user finished the action, proactively suggest more actions for user to take based on current context.
If you need more parameters to complete function calling, you can ask the user for more information.
'''

available_functions = {}
available_tools = {}

def add_functions_to_available_functions(Class):
    class_name = Class.__name__
    # Get all members of the functions module
    members = inspect.getmembers(Class)
    # load all functions from the Contacts class
    for name, member in members:
        # print (name)
        # Check if the member is a method
        if inspect.isfunction(member):
            # Add the method to the available_functions dictionary
            available_functions[name] = member

def load_tools():
    # load tools from tools.json
    with open("recommend/tools/tools_backup.json", "r") as file:
        available_tools = json.load(file)['tools']

    # Get all members of the tools module
    members = inspect.getmembers(functions)
    # load all functions from tools module
    for name, member in members:
        # Check if the member is a function
        if inspect.isfunction(member):
            # Add the function to the available_functions dictionary
            available_functions[name] = member

    # add auto_event_scheduler from MySocalApp to available functions
    available_functions['auto_event_scheduler'] = auto_event_scheduler

    # Add Contacts to available functions
    add_functions_to_available_functions (Contacts)
    add_functions_to_available_functions (Mail)
    add_functions_to_available_functions (SMS)
    add_functions_to_available_functions (Calendar)

    return available_tools, available_functions

available_tools, available_functions = load_tools()

# for tool in available_tools:
    # function_name  = tool['function']['name']
#     # print (function_name)
#     function = available_functions[function_name]
    # print (function)
# print (available_functions)

# for function in available_functions:
    # print (function)

# for tool in available_tools:
#     print (tool)


# Write an intro to this script and print to terminal
print ("Press 'command + shift' on your current window, see AI recommend a list of things that you could do!  \n")

def extract_text_from_image(image):
    try:
        return pytesseract.image_to_string(image)
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


# Send context to GPT-4 and ask for a list of actions
def get_context (image, app_name, window_name):
    print ("Preparing an response!\n")
    base64_image = encode_image(image)
    text_from_image = extract_text_from_image(image)

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
            "text": f"First take the OCR details: '{text_from_image}' and also give me a description of the screenshot, I am current using {app_name} and on its {window_name}. Give me a list of actions i could do based on the screenshot and context that i provided, and number them. Allow me to choose 1 of the actions to execute."
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

    # print (messages)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4-turbo",
        "messages": messages,
        "tools": available_tools,
        "tool_choice": "auto",
        "max_tokens": 300,
        "temperature": 0
    }

    print ("Pulling a list of actions...\n")
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    # print (response.json())
    # message =  response.json()['choices'][0]['message']['content']
    response_json = response.json()
    message = response_json['choices'][0]['message']['content']
    # append the message to the messages list
    print ("Assistant> ", message)

    # construct assistant reply
    reply = {
        "role": "assistant",
        "content": message
    }

    messages.append(reply)

    return messages
    
def run_conversation(messages):
    # print (messages)
    # Step 1: send the conversation and available functions to the model
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=messages,
        tools=available_tools,
        tool_choice="auto",  # auto is default, but we'll be explicit
        temperature=0,
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    
    # Step 2: check if the model wanted to call a function
    # messages.append(response_message)  # extsend conversation with assistant's reply
    if tool_calls:
        messages.append(response_message)
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        # Step 4: send the info for each function call and function response to the model
        for tool_call in tool_calls:
            # print (tool_call)
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)

            # print("Calling function: ", function_name)

            function_response = function_to_call(**function_args)

            # If the response is a json, convert it to a string
            if isinstance(function_response, dict):
                function_response = json.dumps(function_response)
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )  # extend conversation with function response
        second_response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages,
        )  # get a new response from the model where it can see the function response
        second_message = second_response.choices[0]
        if second_message.message.content:
            # print("Response from the model after function call:")
            print(second_message.message.content)
        # print(second_message)
        # append the new message to the conversation
            # Prepare assistant message to append to the conversation
            assistant_message = {
                "role": "assistant",
                "content": second_message.message.content,
            }
            messages.append(assistant_message)
    else:
        if response_message.content is not None:
            # print("Response from the model: \n") 
            print(response_message.content)
            
            # Add assistant's response to the conversation
            assistant_message = {
                "role": "assistant",
                "content": response_message.content,
            }
            messages.append(assistant_message)
    
    return messages

loop_active = False 

def on_activate():
    global loop_active
    
    if not loop_active:
        screenshot, app_name, window_name = get_active_window_screenshot()
        screenshot = screenshot.resize((screenshot.width, screenshot.height))
        messages = get_context(screenshot, app_name, window_name)
        loop_active = True
        while loop_active:
            user_input = input("> ")
            # Listener for keyboard events
            # with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            #     listener.join()
            messages.append({"role": "user", "content": user_input})
            messages = run_conversation(messages)
    else:
        loop_active = False


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
        if all(k in current for k in HOTKEYS) and not loop_active:
            on_activate()

def on_release(key):
    try:
        current.remove(key)
    except KeyError:
        pass

# Listener for keyboard events
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()

