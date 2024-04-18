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

# get openai api key from environment variable
client = OpenAI()
api_key = os.environ.get("OPENAI_API_KEY")

messages = []

today_date = datetime.date.today()

system_prompt = f'''
Today's date is {today_date}.
You are an action recommendation system assistant on MacOS that recommends a set of actions based on current context and screenshots that the user provides, let user choose the action they want to take, and proceed to execute the action by calling the corresponding function.
You only recommend actions that are available in the tools. 
List all the options from 1~n, and let user choose the action they want to take.
After user finished the action, proactively suggest more actions for user to take based on current context.
If you need more parameters for function calling, you can ask the user for more information.
'''

def load_tools():
    available_functions = {}
    available_tools = {}
    # load tools from tools.json
    with open("tools.json", "r") as file:
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
        messages = get_context(screenshot)
        loop_active = True
        while loop_active:
            user_input = input("> ")
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

