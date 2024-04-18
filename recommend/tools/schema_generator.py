# Give a curl request generate a tool description and python schema for the request using LLM

from openai import OpenAI
client = OpenAI()

# Read APIs from a APIs.txt file, the APIs are separated by a newline
with open('APIs.txt', 'r') as file:
    apis = file.read()

# print (apis)

# Add each api into a list
apis = apis.split('\n\n')

# remove empty strings from the list
apis = list(filter(None, apis))

function_system_prompt = "You are a helpful assistant designed to output python function based on curl command. For example: \n"

function_example_output = '''
Given a curl command, generate a python function in following format and return it:

def function_name(parameter1, parameter2, ...):
    url = "https://api-url"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json
    }
    payload = json.dumps({
        "parameter1": parameter1,
        "parameter2": parameter2,
        ...
    })

    response = requests.post(url, headers=headers, data=payload)
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to fetch data", "status_code": response.status_code}


For example, given the following curl command:

Given a curl request like this:
curl -X 'POST' \
  'https://api-yomu-writer-470e5c0e3608.herokuapp.com/paraphrase' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "text": "string",
  "plan": "paid",
  "prefer_gpt": "gpt3",
  "custom_style": "string",
  "language": "EN_US"
}'

This is python function generated for the curl request above:
# Function to call the external API for paraphrasing
def paraphrase_text(text, plan="paid", prefer_gpt="gpt3", custom_style="", language="EN_US"):
    url = "https://api-yomu-writer-470e5c0e3608.herokuapp.com/paraphrase"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "ACCESS_TOKEN": f"{ACCESS_TOKEN}"
    }
    payload = json.dumps({
        "text": text,
        "plan": plan,
        "prefer_gpt": prefer_gpt,
        "custom_style": custom_style,
        "language": language
    })

    response = requests.post(url, headers=headers, data=payload)
    if response.status_code == 200:
        return response.json()  # Return the JSON response from the API
    else:
        return {"error": "Failed to fetch data", "status_code": response.status_code}
'''

# loop through the APIs and generate python function for each API
for api in apis:
    # print (api)
    function_system_prompt += api + '\n\n'
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": function_system_prompt},
            {"role": "user", "content": api}
        ],
    )
    print(response.choices[0].message.content)
    break

# loop through the APIs and generate tool description for each API

tool_system_prompt = "You are a helpful assistant designed to output tool description json based on curl command. For example: \n"

tool_example_output = '''
Given a curl request like this:
curl -X 'POST' \
  'https://api-yomu-writer-470e5c0e3608.herokuapp.com/paraphrase' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "text": "string",
  "plan": "paid",
  "prefer_gpt": "gpt3",
  "custom_style": "string",
  "language": "EN_US"
}'

This is the tool description json generated for the curl request:
{
    "type": "function",
    "function": {
        "name": "paraphrase_text",
        "description": "Paraphrases the provided text using an external API",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text to be paraphrased"
                },
                "plan": {
                    "type": "string",
                    "enum": ["paid"],
                    "description": "Type of plan"
                },
                "prefer_gpt": {
                    "type": "string",
                    "enum": ["gpt3"],
                    "description": "Preferred GPT model"
                },
                "custom_style": {
                    "type": "string",
                    "description": "Custom styling for the paraphrasing"
                },
                "language": {
                    "type": "string",
                    "enum": ["EN_US"],
                    "description": "Language of the text"
                }
            },
            "required": ["text"]
        }
    }
}

Given the curl example, generate its tool description json according to the format above.
'''

# function_system_prompt += tool_example_output

# for api in apis:
#     tool_system_prompt += api + '\n\n'
#     response = client.chat.completions.create(
#         model="gpt-3.5-turbo",
#         response_format={ "type": "json_object" },
#         messages=[
#             {"role": "system", "content": tool_system_prompt},
#             {"role": "user", "content": api}
#         ]
#     )
#     print(response.choices[0].message.content)
#     break