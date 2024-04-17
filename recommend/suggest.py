from pynput import keyboard
import os
import base64
from io import BytesIO
import pyautogui
import json
import tools
import inspect
from apple_calendar import Calendar
from openai import OpenAI
import requests
from app_utils import *

# Check if the key exists
if "OPENAI_API_KEY" not in os.environ:
    print("OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable first.")

client = OpenAI()

# get openai api key from environment variable
api_key = os.environ.get("OPENAI_API_KEY")

messages = []

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
# load_tools()

print (available_functions)

# Write an intro to this script and print to terminal
print ("Press 'command + shift + space' on your current message window, and see AI do its magic!  \n")

# Function to encode the image
def encode_image(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')


system_prompt = '''
"You are an action recommendation system assistant on MacOS that recommends a set of actions user could take based on the screenshots and context user provides, be as detailed as possible. 
The actions should be relevant to the user's current context and should help the user achieve their current task. 
Rank you actions in order of importance, relevance, urgency, and attach confidence score from 0 to 1. Then let user choose the action they want to take, and proceed to execute the action by calling available functions or run AppleScript. 
You could run code on user's machine, user gave you permission to do so.

Output the list of actions in following format as a JSON object:

{
    "actions": [
        {
            "action": "action 1",
            "description": "description of action 1",
            "confidence": 0.9
        },
        {
            "action": "action 2",
            "description": "description of action 2",
            "confidence": 0.8
        }
    ]
}

There only 5 actions you can take:
1. Create a new event in the user's calendar
2. Delete an event from the user's calendar
3. Get the user's calendar events for today
4. Get weather information for the user's current location
5. Paraphrase the text in the user's current context

Only recommend these actions if the user's current context is related to calendar events. Otherwise don't recommend any actions.

'''

force_task_completion_message="""Proceed. You CAN run code on my machine. If you want to run code, start your message with "```"! If the entire task I asked for is done, say exactly 'The task is done.' If you need some specific information (like username or password) say EXACTLY 'Please provide more information.' If it's impossible, say 'The task is impossible.' (If I haven't provided a task, say exactly 'Let me know what you'd like to do next.') Otherwise keep going.""",

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
        "response_format":{ "type": "json_object" },
        "tools": available_tools,
        "tool_choice": "auto",
        "max_tokens": 300
    }

    print ("Pulling a list of actions...\n")
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    # print (response.json())

    # Extracting the inner JSON content from the response
    inner_json = json.loads(response.json()['choices'][0]['message']['content'])

    # tools = inner_json['tools']

    # print (tools)

    # Accessing the actions list from the inner JSON
    recommendations = inner_json['actions']

    recommendations = sorted(recommendations, key=lambda x: x['confidence'], reverse=True)

    action_counter = 1
    # Print each action with its details
    for action in recommendations:
        print(f"{action_counter}: {action['action']}")
        print(f"Description: {action['description']}")
        print(f"Confidence: {action['confidence']}\n")
        action_counter += 1

    # Ask user to choose an action
    try:
        choice = int(input("Enter the number of the action you want to take: "))
        action = recommendations[choice - 1]  # Subtract 1 to match list index
        print(f"You selected: {action['action']}")
        # Here you would call the function to perform the selected action
        # execute_action(action)
    except (ValueError, IndexError):
        print("Invalid input, please enter a valid number corresponding to an action.")


    # response_message = response.json()['choices'][0]['message']
    # try:
    #     tool_calls = response_message['tool_calls']
    # except KeyError:
    #     tool_calls = None

    # if tool_calls:
    #     print ("Calling avaiable functions \n")
    #     messages.append(response_message)
    
    #     for tool_call in tool_calls:
    #         function_name = tool_call['function']['name']
    #         print ("Calling function: " + function_name + "\n")
    #         function_to_call = available_functions[function_name]
    #         function_args = json.loads(tool_call['function']['arguments'])
    #         function_response = function_to_call(
    #             location=function_args.get("location"),
    #             unit=function_args.get("unit"),
    #         )
    #         messages.append(
    #             {
    #                 "tool_call_id": tool_call['id'],
    #                 "role": "tool",
    #                 "name": function_name,
    #                 "content": function_response,
    #             }
    #         )
    #     second_response = client.chat.completions.create(
    #         model="gpt-4-turbo",
    #         messages=messages,
    #     )
    #     # print (second_response)
    #     result = second_response.choices[0].message.content
    # else: 
    #     # result = response.json()["choices"][0]["message"]["content"]
    #     result = response_message['content']

    # print ("------------------------------------\n")
    # print (result + "\n")
    # # prepare_imessage(result)
    # print ("------------------------------------\n")


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
HOTKEYS = {keyboard.Key.cmd, keyboard.Key.shift, keyboard.Key.space}

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

