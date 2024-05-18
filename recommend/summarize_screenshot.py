import os
from openai import OpenAI
import requests
from app_utils import *
import datetime
import pytesseract

messages = []
api_key = os.getenv("OPENAI_API_KEY")


def extract_text_from_image(image):
    try:
        return pytesseract.image_to_string(image)
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

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
                "url": f"data:image/jpeg;base64,{base64_image}"
            }
            }
        ]
    }

    messages.append(user_query)


    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    payload = {
        "model": "gpt-4o",
        "messages": messages,
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
    print ("Assistant> \n", message)

    # construct assistant reply
    reply = {
        "role": "assistant",
        "content": current_time + ": " + message
    }

    # Append log to a log file
    with open('log.txt', 'a') as file:
        file.write(f"{current_time}\n: {message}\n")

    # Remove the last message from the messages list
    messages.pop()

    messages.append(reply)


    return messages


if __name__ == "__main__":
    # create new log file
    with open('log.txt', 'w') as file:
        file.write("")

        # Set system query
    system_query = '''
    You are a helpful assistant responsible for summarizing the user’s interaction on their macOS. You will receive a screenshot of the user’s interaction, along with summaries of previous screenshots as context. Your task is to:

    1.	Summarize the new screenshot and explain what the user is doing.
    2.	Use the summaries of previous screenshots as a guide to help understand the user’s intent and actions.

    Please output your summary in the following format:

    1.	Observation: [Summarize the new screenshot and explain what the user is doing.]
    2.	Thought: [Provide insights or reflections based on the observation and previous summaries.]
    3.	Action: [List actionable recommendations relevant to the user’s current context and activities.]

    '''
    
    message = {
        "role": "system",
        "content": system_query
    }


    messages.append(message)

    print ("Welcome to UtopiaOS Action Recommendation System! What would like me to do for you today? To get started, either tell me the task you try to complete, or simply press command + shift to recommend actions based on vision understanding!\n")

    # Main loop
    while True:
        # user_input = input(">User: ")
        # if user_input.lower() in ["exit", "quit"]:
        #     loop_active = False
        # else:
        #     messages.append({"role": "user", "content": user_input})



        #     messages = run_conversation(messages)
        screenshot, app_name, window_name = get_active_window_screenshot()
        screenshot = screenshot.resize((screenshot.width, screenshot.height))
        summerize_image (screenshot, app_name, window_name)


