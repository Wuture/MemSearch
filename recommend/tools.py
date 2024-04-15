import requests
import json
import os

# Get ACCESS_TOKEN from environment variable
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")

# print (ACCESS_TOKEN)

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

# Function to call the external API for paraphrasing
def paraphrase_text(text, plan="paid", prefer_gpt="gpt3", custom_style="", language="EN_US"):
    print (ACCESS_TOKEN)
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
