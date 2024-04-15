from pynput import keyboard
import os
# from active_window import get_active_window_screenshot
import base64
import requests
from io import BytesIO
import pyautogui
import json
from openai import OpenAI
import Quartz
from AppKit import NSWorkspace
from tools import get_current_weather


# Check if the key exists
if "OPENAI_API_KEY" in os.environ:
    print("OpenAI API key is set.")
else:
    print("OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable.")


# Write an intro to this script and print to terminal
print ("Press 'command + shift' on your current message window, and see AI do its magic!  \n")

# get tools from tools.json
with open("recommend/tools.json", "r") as file:
    tools = json.load(file)['tools']

available_functions = {
    "get_current_weather": get_current_weather,
}

client = OpenAI()

# get openai api key from environment variable
api_key = os.environ.get("OPENAI_API_KEY")

# screenshot based on the active window
def screenshot (window):
    # Get the coordinates and dimensions of the active window
    x = window['kCGWindowBounds']['X']
    y = window['kCGWindowBounds']['Y']
    width = window['kCGWindowBounds']['Width']
    height = window['kCGWindowBounds']['Height']

    app_name = window['kCGWindowOwnerName']
    window_name = window['kCGWindowName']

    # make them integers
    x, y, width, height = int(x), int(y), int(width), int(height)

    # Capture the active window
    screenshot = pyautogui.screenshot(region=(x, y, width, height))
    
    # return the screenshot, app name, and window name
    return screenshot, app_name, window_name


# Get the active window and take a screenshot
def get_active_window_screenshot ():
    # Get the active window
    options = Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements
    active_window_list = Quartz.CGWindowListCopyWindowInfo(options, Quartz.kCGNullWindowID)

    # Get the list of running applications
    workspace = NSWorkspace.sharedWorkspace()
    active_app_info = workspace.activeApplication()

    # Get the active application name
    active_app_name = active_app_info.get('NSApplicationName')

    # Iterate through all windows to find the active window
    for window in active_window_list:
        if window['kCGWindowOwnerName'] == active_app_name and window['kCGWindowName'] != '':
            # screenshot based on the active window
            results  = screenshot(window)
            # print (window['kCGWindowOwnerName'])
            return results 
        

# Function to encode the image
def encode_image(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def send_to_gpt4v (image):
    print ("Preparing an response!\n")
    base64_image = encode_image(image)

    # Prepare system message for gpt4v
    system = {
        "role": "system",
        "content": [
            {
            "type": "text",
            "text": "You are an action recommendation system that recommends a set of actions user could take based on the screenshot user provides, be as detailed as possible. The actions should be relevant to the user's current context and should help the user achieve their goals."
            },
        ]

    }

    user_query =  {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": "Give me a list of actions that i could do, and number them."
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
        "tools": tools,
        "tool_choice": "auto",
        "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    # print (response.json())

    response_message = response.json()['choices'][0]['message']
    try:
        tool_calls = response_message['tool_calls']
    except KeyError:
        tool_calls = None

    if tool_calls:
        print ("Calling avaiable functions \n")
        messages.append(response_message)
    
        for tool_call in tool_calls:
            function_name = tool_call['function']['name']
            print ("Calling function: " + function_name + "\n")
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call['function']['arguments'])
            function_response = function_to_call(
                location=function_args.get("location"),
                unit=function_args.get("unit"),
            )
            messages.append(
                {
                    "tool_call_id": tool_call['id'],
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )
        second_response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages,
        )
        # print (second_response)
        result = second_response.choices[0].message.content
    else: 
        # result = response.json()["choices"][0]["message"]["content"]
        result = response_message['content']

    print ("------------------------------------\n")
    print (result + "\n")
    # prepare_imessage(result)
    print ("------------------------------------\n")


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

    send_to_gpt4v(screenshot)

def for_canonical(f):
    # Convert the key to a canonical version
    return lambda k: f(keyboard.Key.canonical(k))

# The key combination to check
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

