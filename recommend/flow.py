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

today_date = datetime.datetime.now().strftime("%Y-%m-%d")

system_prompt = f'''
Today's date is {today_date}.
You are an action recommendation system assistant on MacOS that recommends a set of actions, let user choose the action they want to take, and proceed to execute the action by calling the corresponding function.
You only recommend actions that are available in the tools. 
List all the options from 1~n, and let user choose the action they want to take.
After user finished the action, proactively suggest more actions for user to take based on current context.
If you don't know what time and date it is, call the function get_current_time_and_date() to get the current time and date.

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

def run_conversation(messages):
    print (messages)
    # Step 1: send the conversation and available functions to the model
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
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
            model="gpt-3.5-turbo",
            messages=messages,
        )  # get a new response from the model where it can see the function response
        second_message = second_response.choices[0]
        if second_message.message.content:
            print("Response from the model after function call:")
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
            print("Response from the model: \n") 
            print(response_message.content)
            
            # Add assistant's response to the conversation
            assistant_message = {
                "role": "assistant",
                "content": response_message.content,
            }
            messages.append(assistant_message)

    
    return messages
        
if __name__ == "__main__":
    # context = email_msg
    # messages = [system_message, {"role": "user", "content": context}]
    messages = [system_message]
    # messages = run_conversation( messages)
    # let user 
    print ("\n\nPlease tell us what you need, we will recommend the best tools to help you accomplish your task.")
    # Let user enter the message, and run the conversation until the user wants to exit
    while True:
        user_input = input("> ")
        messages.append({"role": "user", "content": user_input})
        messages = run_conversation(messages)