from pynput import keyboard
from PIL import ImageGrab
import os
import sys
# Append the parent directory to sys.path
# sys.path.append(os.path.abspath('..'))
from active_window import get_active_window_screenshot
# from interpreter import interpreter
import base64
import requests
from io import BytesIO
import pyautogui

# get openai api key from environment variable
api_key = os.environ.get("OPENAI_API_KEY")

# # Function to encode the image
# def encode_image(image_path):
#   with open(image_path, "rb") as image_file:
#     return base64.b64encode(image_file.read()).decode('utf-8')

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
        "max_tokens": 300
    }

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    result = response.json()["choices"][0]["message"]["content"]
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

