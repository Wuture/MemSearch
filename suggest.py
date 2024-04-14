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

client = OpenAI()

# get openai api key from environment variable
api_key = os.environ.get("OPENAI_API_KEY")

# screenshot based on the active window
def screenshot (window):
    # Get the coordinates and dimensions of the active window
    x = window['kCGWindowBounds']['X']
    y = window['kCGWindowBounds']['Y']
    width = window['kCGWindowBounds']['Width'] + 20
    height = window['kCGWindowBounds']['Height'] + 20

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
    
# Set up the access token as an environment variable or directly in your script
ACCESS_TOKEN = "YRe8osUdaAXDHq2auQpp3ifWukiy"

    
tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the current weather in a given location",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "The city and state, e.g. San Francisco, CA",
                        },
                        "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                    },
                    "required": ["location"],
                },
            },
        }
    ]

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
            "text": "You are an messaging co-pilot helping user respond based on current conversation and context, you will be providing a response in chinese or english depending on the context."
            },
        ]

    }

    user_query =  {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": "Give me a response, nothing else."
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

    # print (response)
    # print (response.json())
    # print (response.json()['choices'][0]['message']['tool_calls'])

    response_message = response.json()['choices'][0]['message']
    # print (response_message)
    # print (response_message['tool_calls'])
    # # catch KeyError: 'tool_calls'
    try:
        tool_calls = response_message['tool_calls']
    except KeyError:
        tool_calls = None
    
    # # print (tool_calls)
    # # # print (tool_calls)

    if tool_calls:
        print ("Calling avaiable functions \n")
        available_functions = {
            "get_current_weather": get_current_weather,
        }
        messages.append(response_message)
        for tool_call in tool_calls:
            function_name = tool_call['function']['name']
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
    prepare_imessage(result)
    print ("------------------------------------\n")


def prepare_imessage(message):
    # Type and send the message
    pyautogui.write(message)
    # pyautogui.press('return')

def on_activate():
    # # Function to take a screenshot
    # screenshot = ImageGrab.grab()
    # screenshot.save(os.path.expanduser("~/Desktop/screenshot.png"))  # Save to desktop
    # print("Screenshot taken and saved on desktop.")
    screenshot, app_name, window_name = get_active_window_screenshot()

    # compress the screenshot
    screenshot = screenshot.resize((screenshot.width // 2, screenshot.height // 2))

    # show image in preview
    # screenshot.show()
    # save the screenshot in current directory
    # screenshot.save(f"{app_name}_{window_name}.png")
    # print(f"Screenshot taken and saved as {app_name}_{window_name}.png")
    # send the screenshot to gpt4v
    send_to_gpt4v(screenshot)

def for_canonical(f):
    # Convert the key to a canonical version
    return lambda k: f(l.canonical(k))

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

