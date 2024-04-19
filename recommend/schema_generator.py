import inspect
import json
from tools.sms import SMS
from tools.contacts import Contacts
from tools.mail import Mail
from tools.calendar import Calendar
from openai import OpenAI

client = OpenAI()
def generate_json_schema(code, class_name=None):
    prompt = '''Generate a JSON for the function in''' + f'{code}' + '''according to this format:  
    
    {
        "type": "function",
        "function": {
            "name": function_name_1
            "description": this is a function "",
            "parameters": {
                "type": "object",
                "properties": {
                    "param_1": {
                        "type": "string",
                        "description": "description 1"
                    },
                    "param_2": {
                        "type": "string",
                        "description": "description 2"
                    }
                },
                "required": ["param_1"]
            }
        }
    }

    # if class_name in front of function_name_1 if there is class_name is None

    
    '''

    # print (prompt)
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": f"give me a JSON. Make sure the required field in the json is correct!"}
        ],
        response_format = { "type": "json_object" }
    )
    json_schema = response.choices[0].message.content
    print (json_schema)
    return json_schema

# Example usage
# code = inspect.getsource(Mail)

def generate_json_for_class (Class):
    class_name = Class.__name__
    function_defs = inspect.getmembers(Class, predicate=inspect.isfunction)

    json_schemas = []

    for name, func in function_defs:
        # Get the source code of the function
        func_code = inspect.getsource(func)
        print("Generating json for:", name)
        # print (func_code)
        json_schema = generate_json_schema(func_code, class_name)
        # print(json_schema)
        json_schemas.append (json_schema)
        # break

    return json_schemas

def add_jsons_to_tools (tools_jsons):
    formatted_jsons = [] 
    # Load the existing JSON content from the tools.json file
    with open('recommend/tools/tools.json', 'r') as file:
        tools_data = json.load(file)

    # Get the "tools" array from the loaded JSON data
    tools_array = tools_data['tools']

    for json_string in tools_jsons:
        tool_json = json.loads (json_string)
        formatted_jsons.append (tool_json)

    # Check for duplicate tool names and append only new tools
    new_tools = []
    for new_tool in formatted_jsons:
        tool_exists = False
        for existing_tool in tools_array:
            if existing_tool['function']['name'] == new_tool['function']['name']:
                tool_exists = True
                break
        if not tool_exists:
            print ("Append new tool:", new_tool['function']['name'])
            new_tools.append(new_tool)

    # Extend the "tools" array with the new JSON objects
    tools_array.extend(new_tools)

    # Write the updated JSON data back to the tools.json file
    with open('recommend/tools/tools.json', 'w') as file:
        json.dump(tools_data, file, indent=4)


# if __name__ == '__main__':
#     # sms
#     sms_list = generate_json_for_class (SMS)
#     add_jsons_to_tools (sms_list)

#     # contacts
#     contacts_list = generate_json_for_class (Contacts)
#     add_jsons_to_tools (contacts_list)

#     # calendar
#     calendar_list = generate_json_for_class (Calendar)
#     add_jsons_to_tools (calendar_list)

#     # mail
#     mail_list = generate_json_for_class (Mail)
#     add_jsons_to_tools (mail_list)
