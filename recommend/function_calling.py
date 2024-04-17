from openai import OpenAI
import json
import inspect
import tools
import datetime

client = OpenAI()

def load_tools():
    available_functions = {}
    available_tools = {}
    # load tools from tools.json
    with open("recommend/tools.json", "r") as file:
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

# print (available_functions)
# print (available_tools)

today_date = datetime.datetime.now().strftime("%Y-%m-%d")

# system_prompt = '''
# Today's date is {today_date}.
# You are an action recommendation system assistant on MacOS that recommends a set of actions user could take based on the screenshots and context user provides, be as detailed as possible.
# Let user choose the action they want to take, and proceed to execute the action by calling the corresponding function.

# Return a list of actions available as json objects, with the following format:

# {
#     "actions": [
#         {
#             "action": "Get weather",
#             "description": "Get the current weather based at San Francisco",
#             "confidence": 0.9
#             "function_name": get_current_weather,
#             "function_args": ["location": "San Francisco", "unit": "F"]
#         },
#         {
#             "action": "Get calendar events",
#             "description": "Get the calendar events for a specific date",
#             "confidence": 0.8
#             "function_name": get_events, 
#             "function_args": { "start_date": "2022-01-01", "end_date": "2022-01-31" }
#         }
#     ]
# }
# '''

system_prompt = '''
You are an action recommendation system assistant on MacOS that recommends a set of actions, let user choose the action they want to take, and proceed to execute the action by calling the corresponding function.
You only recommend actions that are available in the tools. 
List all the options from 1~n, and let user choose the action they want to take.

e.g. 
1. Get weather
2. Get calendar events
3. Get current location
4. Get current time
5. Get current date
6. Get current weather

'''

system_message = {
        "role": "system",
        "content": [
            {
            "type": "text",
            "text": system_prompt,
            },
        ]
}

email_msg = '''
Marisa Lu
Title: Coffee?

Hey Jason,
Was wondering if you'd be interested in meeting my team at Philz Coffee at 11 AM today. No pressure if you can't make it, although I think you guys would really get along!
'''

def run_conversation(messages):
    # Step 1: send the conversation and available functions to the model
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        tools=available_tools,
        tool_choice="auto",  # auto is default, but we'll be explicit
    )
    response_message = response.choices[0].message
    print(response_message)
    tool_calls = response_message.tool_calls
    # Step 2: check if the model wanted to call a function
    messages.append(response_message)  # extend conversation with assistant's reply
    if tool_calls:
        # Step 3: call the function
        # Note: the JSON response may not always be valid; be sure to handle errors
        # Step 4: send the info for each function call and function response to the model
        for tool_call in tool_calls:
            # print (tool_call)
            function_name = tool_call.function.name
            function_to_call = available_functions[function_name]
            function_args = json.loads(tool_call.function.arguments)
            print (function_name)
            print (function_args)

            function_response = function_to_call(**function_args)
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response,
                }
            )  # extend conversation with function response
        second_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )  # get a new response from the model where it can see the function response
        second_message = second_response.choices[0].message
        print(second_message)
        # append the new message to the conversation
        messages.append(second_message)
    
    return messages
        
if __name__ == "__main__":
    context = email_msg
    messages = [system_message, {"role": "user", "content": context}]
    messages = run_conversation( messages)
    # let user 

    # Let user enter the message, and run the conversation until the user wants to exit
    while True:
        user_input = input("Enter your message: ")
        messages.append({"role": "user", "content": user_input})
        messages = run_conversation(messages)