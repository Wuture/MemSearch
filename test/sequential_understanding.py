
import requests
import base64
from io import BytesIO
from PIL import Image
import pytesseract
import os
from openai import OpenAI
import datetime
import threading
from pynput import keyboard


# date is today's date

date = datetime.date.today().strftime("%Y-%m-%d")
messages = []

client = OpenAI()
api_key = os.environ.get("OPENAI_API_KEY")

# get latest screenshots and get their metadata
def get_latest_screenshots(number_of_screenshots=3, screenshot_type="active"):
    print ("Getting the latest screenshots\n")
    screenshot_directory_name = screenshot_type + "_screenshot"
    screenshot_metadata_directory_name = screenshot_type + "_screenshot_metadata"
    screenshot_directory = f"screenshot_data/{screenshot_directory_name}/"
    screenshot_metadata_directory = f"screenshot_data/{screenshot_metadata_directory_name}/"

    screenshot_directory_today = os.path.join(screenshot_directory, date)
    screenshot_metadata__directory_today = os.path.join(screenshot_metadata_directory, date)

    # print (screenshot_directory_today)

    # sort the files in the directory by creation time
    files = os.listdir(screenshot_directory_today)

    # sort the files by creation time, from newest to oldest
    files.sort(key=lambda x: os.path.getctime(os.path.join(screenshot_directory_today, x)), reverse=False)

    # # get the latest screenshots
    counter = 1 
    screenshot_raw_text = ""
    screenshot_raw_ocr_text = ""
    screenshot_images = []
    # get last filename in the directory
    for filename in files[-number_of_screenshots:]:
        # make sure the filename is not .DS_Store
        if filename == ".DS_Store":
            continue

        # print (filename)
        screenshot_path = os.path.join(screenshot_directory_today, filename)
        image = Image.open(screenshot_path)
        # append the image to the screenshot_images list
        screenshot_images.append(image)

        # get app name from file name, it is the characters before "_"
        app_name = filename.split("_")[0]
        # # # # Get raw text from the image
        # text = pytesseract.image_to_string(image)

        # # # with each file, append the raw text to the screenshot_raw_text, 
        # title = f"**** Screenshot {counter}, the current app is {app_name}, the raw text content is:\n {text}"
        # screenshot_raw_text += title + "\n"


        # get metadata
        metadata_path = os.path.join(screenshot_metadata__directory_today, filename.replace(".jpg", ".txt"))
        with open(metadata_path, "r") as file:
            metadata = file.read()
            title = f"Screenshot {counter}, the current app is {app_name}, the OCR content is:\n {metadata}"
            screenshot_raw_ocr_text += title + "\n"

        metadata_path = os.path.join(screenshot_metadata__directory_today, filename.replace(".jpg", "_text.txt"))
        with open(metadata_path, "r") as file:
            metadata = file.read()
            title = f"Screenshot {counter}, the current app is {app_name}, the text content is:\n {metadata}"
            screenshot_raw_text += title + "\n"

        counter += 1
    # # write both the raw text and metadata to a file
    # with open("screenshot_raw_text.txt", "w") as file:
    #     file.write(screenshot_raw_text)
    
    # with open("screenshot_raw_oct_text.txt", "w") as file:
    #     file.write(screenshot_raw_oct_text)
    # print (screenshot_images)
    return screenshot_raw_text, screenshot_raw_ocr_text, screenshot_images

def extract_text_from_image(image):
    try:
        return pytesseract.image_to_string(image)
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Function to encode the image
def encode_image(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')


def get_context_from_text (text):

    print ("Getting context from X previous screenshots text\n")

    user_text = f"Given sequential number of screenshots text data, summerize and describe what the I am doing on MacOS. Then give me a list of actions ranked by relevancy and importance from 1~5 that I can take based on the context."

    # print (text)
    user_query =  {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": user_text
            },
            {
                "type": "text",
                "text": text
            }
        ]
    }

       # print (user_query)
    messages.append(user_query)

    # print (messages)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-3.5-turbo",
        "messages": messages,
        "max_tokens":300,
        "temperature": 0
    }

    # print ("Pulling a list of actions...\n")

    # try to get a response from the model, if not working, retry   
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
    # print (response.json())
    # message =  response.json()['choices'][0]['message']['content']
    response_json = response.json()
    # print (response_json)
    message = response_json['choices'][0]['message']['content']
    # append the message to the messages list
    # print ("Assistant> ", message)

    print (message)



# Send context to GPT-4 and ask for a list of actions
def get_context_from_image (images=None):
    # print ("Preparing an response!\n")
    print ("Getting context from X previous screenshots\n")

    base64_images = []
    # turn images into base64
    for image in images:
        base64_image = encode_image(image)
        base64_images.append(base64_image)

    base64_images_query = []
    # populate the json payload with base64 images
    for base64_image in base64_images:
        base64_images_query.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
        })

    # print (base64_images_query)

    content = []
    user_text = f"Given sequential screenshots, summerize and describe what I am currently doing on MacOS. Then give me a list of actions from 1~5 that I can take."

    # append the user text to the content
    content.append({
        "type": "text",
        "text": user_text
    })

    # append the base64 images to the content
    for base64_image in base64_images_query:
        content.append(base64_image)
    

    user_query =  {
        "role": "user",
        "content": content
    }

    # print (user_query)
    messages.append(user_query)

    # print (messages)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4-turbo",
        "messages": messages,
        # "tools": available_tools,
        # "tool_choice": "auto",
        # "max_tokens": 300,
        "temperature": 0
    }

    # print ("Pulling a list of actions...\n")

    # try to get a response from the model, if not working, retry   
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
    # print (response.json())
    # message =  response.json()['choices'][0]['message']['content']
    response_json = response.json()
    # print (response_json)
    message = response_json['choices'][0]['message']['content']
    # append the message to the messages list
    # print ("Assistant> ", message)

    print (message)

    # construct assistant reply
    # reply = {
    #     "role": "assistant",
    #     "content": message
    # }

    # messages.append(reply)

    # return messages 
    return message



today_date = datetime.date.today()

system_prompt = f'''
Today's date is {today_date}.
You are an action recommendation system assistant on MacOS that recommends a set of actions based on current context and screenshots that the user provides, let user choose the action they want to take, and proceed to execute the action by calling the corresponding function.
The screenshots provided by the user are sequential in time, so first summerize what the user is dping on MacOS, then give a list of actions from 1~5 that the user can take.
List all the possible actions from 1~n, and let user choose the action they want to take.

Return the list of action in the following format:
1. Action 1: 
2. Action 2: 
3. Action 3: 
4. Action 4: 
5. Action 5: 
'''


def on_activate():
    # print ("\nGetting context from X previous screenshots\n")
    global messages
    screenshot_text, screenshot_ocr, screenshot_images = get_latest_screenshots(3)

    # get the context from the images
    # get_context_from_image(images=screenshot_images)

    # get the context from the OCR
    # get_context_from_text(screenshot_ocr)

    # print (screenshot_text)
    # get the context from the raw text
    get_context_from_text(screenshot_text)

def for_canonical(f):
    # Convert the key to a canonical version
    return lambda k: f(keyboard.Key.canonical(k))

# The key combination to check
# HOTKEYS = {keyboard.Key.cmd, keyboard.Key.shift, keyboard.Key.space}
HOTKEYS = {keyboard.Key.cmd, keyboard.Key.shift}

# The currently active modifiers
current = set()

def on_press(key):
    # print ("Key pressed\n")
    if any([key in HOTKEYS, key in current]):
        current.add(key)
        if all(k in current for k in HOTKEYS):
            on_activate()

def on_release(key):
    try:
        current.remove(key)
    except KeyError:
        pass

# # Listener for keyboard events
def keyboard_listener():
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

if __name__ == "__main__":
    # get the latest screenshots

    messages.append({
        "role": "system",
        "content": system_prompt
    })

    keyboard_thread = threading.Thread(target=keyboard_listener)
    keyboard_thread.daemon = True
    keyboard_thread.start()
    # get_context_from_text(screenshot_raw_oct_text)

    loop_active = True    
    while loop_active:
        user_input = input(">User: ")
        if user_input.lower() in ["exit", "quit"]:
            loop_active = False
        else:
            print ("Getting context from X previous screenshots\n")
