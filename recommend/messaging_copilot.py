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
from tools import get_current_weather, paraphrase_text


# Check if the key exists
if "OPENAI_API_KEY" in os.environ:
    print("OpenAI API key is set.")
else:
    print("OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable.")

# load tools from tools.json
with open("recommend/tools.json", "r") as file:
    tools = json.load(file)['tools']

system_prompt = "You are an advanced AI assistant designed to aid in messaging tasks. Your main roles include analyzing the content of message sender, determining the appropriate actions based on the query context, and executing those actions by calling predefined functions accurately. You need to handle different types of inputs such as text and images. When you receive text input, evaluate the content to determine if it should be paraphrased or if weather information is needed based on mentioned locations. For images, analyze and provide relevant responses or actions based on image content. Use the following functions accordingly: 'paraphrase_text' for text paraphrasing and 'get_current_weather' for fetching weather data. Always confirm the exact requirements such as necessary parameters and ensure you adapt your responses to be in English or Chinese based on the contextual clues provided in the conversation. Just give the response and nothing else."

client = OpenAI()

# get openai api key from environment variable
api_key = os.environ.get("OPENAI_API_KEY")
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")

# Map names to function object for tool calls
tool_functions = {
    "get_current_weather": get_current_weather,
    "paraphrase_text": paraphrase_text
}

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
            "text": system_prompt,
            },
        ]

    }

    user_query =  {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": "Give me a response, use function calling if necessary."
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
    print (response.json())
    response_message = response.json()['choices'][0]['message']
    if 'tool_calls' in response_message:
        print("Calling available functions \n")
        available_functions = tool_functions
        messages.append(response_message)
        tool_calls = response_message['tool_calls']
        for tool_call in tool_calls:
            function_name = tool_call['function']['name']
            print ("Calling function: " + function_name + "\n")
            function_args = json.loads(tool_call['function']['arguments'])  # Ensure arguments are correctly formatted as a dictionary
            if function_name in available_functions and isinstance(function_args, dict):
                function_response = available_functions[function_name](**function_args)
                messages.append({
                    "tool_call_id": tool_call['id'],
                    "role": "tool",
                    "name": function_name,
                    "content": json.dumps(function_response)  # Assume response needs to be JSON string
                })
        # Perform follow-up request if needed
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages
        )
        print (response)
        result = response.choices[0].message.content
        # print (result)
    else:
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
    screenshot, app_name, window_name = get_active_window_screenshot()

    # compress the screenshot
    screenshot = screenshot.resize((screenshot.width // 2, screenshot.height // 2))

    # show image in preview
    # screenshot.show()

    # send the screenshot to gpt4v
    send_to_gpt4v(screenshot)

def for_canonical(f):
    # Convert the key to a canonical version
    return lambda k: f(keyboard.Key.from_canonical(k))

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

