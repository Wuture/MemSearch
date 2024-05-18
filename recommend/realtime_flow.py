from pynput import keyboard
import os
import json
import tools.functions as functions
import inspect
from openai import OpenAI
import requests
from app_utils import *
import datetime
from tools.MySocalApp import create_google_calendar_event
from tools.contacts import Contacts
from tools.mail import Mail
from tools.sms import SMS
from tools.location import search_location_in_maps
from tools.executecommand import execute_command
from tools.executecommand import generate_and_execute_applescript
from tools.Calendar import Calendar
import pytesseract
import threading
import time
from time import sleep  

conversation_messages = []
summary_messages = []

# Check if the key exists
if "OPENAI_API_KEY" not in os.environ:
    print("OpenAI API key is not set. Please set the OPENAI_API_KEY environment variable first.")

# get openai api key from environment variable
client = OpenAI()
api_key = os.environ.get("OPENAI_API_KEY")

today_date = datetime.date.today()

system_prompt = f'''
Today's date is {today_date}.
You are an action recommendation system assistant on MacOS that recommends a set of actions based on current context and screenshots that the user provides, let user choose the action they want to take, and proceed to execute the action by calling the corresponding function.
You only recommend actions that are available in the tools provided. To get more tools, always call function get_shortcuts to find out what shortcuts are available, and add them to available tools to recommend based on the context.
List all the options from 1~n ranked by relevance (don't show any irrelevant options), and let user choose the action they want to take. 
You can recommend similar options that are available. For example if there is a meeting request you can recommend both Apple Calendar and Google Calendar.
After user finished the action, proactively suggest more actions for user to take based on current context.
If you need more parameters to complete function calling, you can ask the user for more information. Don't call functions if you are unsure about the correctness of parameters.

In your available tools, there is a function called run_shortcut, which runs a certain shortcut designated by the user. You can use this function to run any shortcut on the user's machine.
e.g. run_shortcut("Send iMessage") would summon the Messages app and send an iMessage to the recipient.

On MacOS, if you can't find a function to do something, you can use generate_and_execute_applescript to generate an applescript and execute it.
If a tool is not available then generate the code necessary to execute the action and then call the execute_command function to execute the code.

ALWAYS RECOMMEND MORE RElEVANT ACTIONS TO TAKE AFTER COMPLETING AN ACTION.
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
    with open("recommend/tools/tools.json", "r") as file:
        available_tools = json.load(file)['tools']

    # Get all members of the tools module
    members = inspect.getmembers(functions)
    # load all functions from tools module
    for name, member in members:
        # Check if the member is a function
        if inspect.isfunction(member):
            # Add the function to the available_functions dictionary
            available_functions[name] = member

    # add schedule_google_calendar_event from MySocalApp to available functions
    available_functions['create_google_calendar_event'] = create_google_calendar_event

    # Add Contacts to available functions
    add_functions_to_available_functions (Contacts)
    add_functions_to_available_functions (Mail)
    add_functions_to_available_functions (SMS)
    add_functions_to_available_functions (Calendar)
    available_functions['search_location_in_maps'] = search_location_in_maps
    available_functions['execute_command'] = execute_command
    available_functions['generate_and_execute_applescript'] = generate_and_execute_applescript

    return available_tools, available_functions

available_tools, available_functions = load_tools()


# Send context to GPT-4 and ask for a list of actions
def summerize_image (image, app_name, window_name):
    # get current time 
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

   # print ("Preparing an response!\n")
    base64_image = encode_image(image)
    # text_from_image = extract_text_from_image(image)

    user_query =  {
        "role": "user",
        "content": [
            {
            "type": "text",
            "text": f"This is a screenshot of my MacOS. I am currently on {app_name} and its {window_name}."
            },
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}",
                "detail":"low"
            }
            }
        ]
    }

    summary_messages.append(user_query)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4o",
        "messages": summary_messages,
        "max_tokens": 300,
        "temperature": 0
    }

    # print ("Pulling a list of actions...\n")
    # Time the request
    # start_time = time.time()

    # try to get a response from the model, if not working, retry   
    try:
        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    
    # end_time = time.time()
    # print(f"Request took {end_time - start_time} seconds")

    # print (response.json())
    # message =  response.json()['choices'][0]['message']['content']
    response_json = response.json()
    # print (response_json)
    summary_message = response_json['choices'][0]['message']['content']
    # append the message to the messages list
    # print ("Assistant> \n", summary_message)

    # construct assistant reply
    reply = {
        "role": "assistant",
        "content": "Here is the summary for the screenshot taken at " + current_time + ": " + summary_message
    }

    # Append log to a log file
    with open('log.txt', 'a') as file:
        file.write(f"{current_time}: {summary_message}\n")

    # # Remove the last message from the messages list, because it is an image
    summary_messages.pop()

    summary_messages.append(reply)

    return summary_messages

# Send context to GPT-4 and ask for a list of actions
def get_context (conversation_messages):
    print ("Preparing an response!\n")

    # print (summary_messages)
    recent_summaries = []

    # if the role in summary messages is not system or user, then append to conversation_messages
    for i in range(len(summary_messages)):
        if summary_messages[i]['role'] != 'system' and summary_messages[i]['role'] != 'user':
            recent_summaries.append(summary_messages[i])

    # if the length of recent_summaries is more than 5, then only take the last 5 summaries
    if len(recent_summaries) > 3:
        recent_summaries = recent_summaries[-3:]

    # if recent_summaries is not empty, then append to conversation_messages
    if len(recent_summaries) > 0:
        for i in range(len(recent_summaries)):
            conversation_messages.append(recent_summaries[i])

    return conversation_messages


def run_conversation(conversation_messages):
    # print (messages)
    # Step 1: send the conversation and available functions to the model
    # Time the request
    start_time = time.time()
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=conversation_messages,
        tools=available_tools,
        tool_choice="auto",  # auto is default, but we'll be explicit
        temperature=0,
    )
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    
    # Step 2: check if the model wanted to call a function
    # messages.append(response_message)  # extsend conversation with assistant's reply
    if tool_calls:
        conversation_messages.append(response_message)
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        # Step 4: send the info for each function call and function response to the model
        for tool_call in tool_calls:
            # print (tool_call)
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)

            # print("Calling function: ", function_name)

            # catch error and just append the error to the messages
            try:
                function_response = function_to_call(**function_args)
            except Exception as e:
                function_response = str(e)
                print(f"An error occurred: {e}")
                # add the error as assistant response, and append to the conversation_messages
                assistant_message = {
                    "role": "assistant",
                    "content": f"An error occurred: {e}"
                }
                conversation_messages.append(assistant_message)
                return conversation_messages

            # If the response is a json, convert it to a string
            if isinstance(function_response, dict):
                function_response = json.dumps(function_response)

            # if function response is a list, then combine them into a single string
            if isinstance(function_response, list):
                function_response = ",".join(function_response)

            conversation_messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )  # extend conversation with function response
        second_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=conversation_messages,
        )  # get a new response from the model where it can see the function response
        second_message = second_response.choices[0]
        if second_message.message.content:
            # print("Response from the model after function call:")
            print(">Assistant: ", second_message.message.content)
        # print(second_message)
        # append the new message to the conversation
            # Prepare assistant message to append to the conversation
            assistant_message = {
                "role": "assistant",
                "content": second_message.message.content,
            }
            conversation_messages.append(assistant_message)
    else:
        if response_message.content is not None:
            # print("Response from the model: \n") 
            print(">Assistant: ", response_message.content)
            
            # Add assistant's response to the conversation
            assistant_message = {
                "role": "assistant",
                "content": response_message.content,
            }
            conversation_messages.append(assistant_message)
    
    end_time = time.time()
    print(f"Request took {end_time - start_time} seconds")
    
    # print (conversation_messages)

    return conversation_messages


def on_activate():
    print ("\nScanning the current window...\n")
    global conversation_messages

    # if the conversation messages only have system, then just ret

    if len (conversation_messages) == 1:
        screenshot, app_name, window_name = get_active_window_screenshot()
        screenshot = screenshot.resize((screenshot.width, screenshot.height))
        base64_image = encode_image(screenshot)
        user_query =  {
            "role": "user",
            "content": [
                {
                "type": "text",
                "text": f"Give me a description of the screenshot, I am current using {app_name} and on its {window_name}. Give me a list of actions i could do based on the screenshot and context that i provided, and number them. Allow me to choose 1 of the actions to execute."
                },
                {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
                }
            ]
        }

        conversation_messages.append(user_query)
        run_conversation(conversation_messages)
    else:
        conversation_messages = get_context(conversation_messages)
        # print (conversation_messages)
        conversation_messages = run_conversation(conversation_messages)
    print(">User: ", end="", flush=True)
    # loop_active = True

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

def summerization_loop():
    global summary_messages
        # Set system query
    summary_prompt = '''
    You are a helpful assistant responsible for summarizing the user’s interaction on their macOS. You will receive a screenshot of the user’s interaction, along with summaries of previous screenshots as context. Your task is to:

    1.  Summarize the new screenshot and explain what the user is doing.
    2.	Use the summaries of previous screenshots as a guide to help understand the user’s intent and actions.
    3.  If the screenshot contains messages (from emails or other messagers), just add the original messages to the summary. But make sure the messages are arranged in order of the people who sent them.


    '''
    
    summary_system_prompt = {
        "role": "system",
        "content": summary_prompt
    }


    summary_messages.append(summary_system_prompt)

    while True:
        # try get screenshot, if error, just skip
        try:
            screenshot, app_name, window_name = get_active_window_screenshot()
        except Exception as e:
            # print(f"Cannot get screenshot: {e}")
            continue

        if app_name == "Terminal":
            continue

        screenshot = screenshot.resize((screenshot.width, screenshot.height))
        summary_messages = summerize_image (screenshot, app_name, window_name)

        sleep (3)
        # print (summary_messages)



if __name__ == "__main__":
    # create new log file
    with open('log.txt', 'w') as file:
        file.write("")

    conversation_messages = [system]
    # Set loop_active to True to keep the main loop running
    loop_active = True

    # Start the keyboard listener in a separate thread
    keyboard_thread = threading.Thread(target=keyboard_listener)
    keyboard_thread.daemon = True
    keyboard_thread.start()


    # Create and start a new thread for the main loop
    loop_thread = threading.Thread(target=summerization_loop)
    loop_thread.start()

    print ("Welcome to UtopiaOS Action Recommendation System! What would like me to do for you today? To get started, either tell me the task you try to complete, or simply press command + shift to recommend actions based on vision understanding!\n")

    # Main loop
    while loop_active:
        user_input = input(">User: ")
        if user_input.lower() in ["exit", "quit"]:
            loop_active = False
        else:
            conversation_messages.append({"role": "user", "content": user_input})
            conversation_messages = run_conversation(conversation_messages)


    # Ensure the threads are properly terminated
    loop_thread.join()
    keyboard_thread.join()