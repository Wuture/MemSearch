from openai import OpenAI
from datetime import datetime
from analyze_usage_behavior import analyze_usage_behavior

# Use OpenAI to generate a summary of the daily usage behavior an user based on data collected
# gets API Key from environment variable OPENAI_API_KEY
client = OpenAI()

# Get the previous day's date
today = datetime.now().date()
today_str = today.strftime('%Y-%m-%d')

# Construct the CSV file path for the previous day
csv_file_path = f'usage_data/{today_str}/{today_str}_usage.csv'
summary_file_path = f'usage_data/{today_str}/{today_str}_summary.txt'
ai_summary_file_path = f'usage_data/{today_str}/{today_str}_ai_summary.txt'


# analyze today's usage
def analyze_today_usage():
    
    # Call the analyze_usage_behavior function with the CSV file path
    analyze_usage_behavior(csv_file_path, summary_file_path)

def summerize (messages):
    with open(summary_file_path, 'r') as file:
        summary = file.read()

    # append the summary to the messages
    messages.append(
        {
            "role": "user",
            "content": summary,
        }
    )

    # print (messages)
    # Generate a summary of the daily usage behavior
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
    )

    ai_summary = completion.choices[0].message.content
    # append the AI summary to the messages
    messages.append(
        {
            "role": "assistant",
            "content": ai_summary,
        }
    )

    with open(ai_summary_file_path, 'w') as file:
        file.write(ai_summary)
    
    with open(summary_file_path, 'r') as file:
        summary = file.read()
    
    print ("The user has provided the following summary: ")
    print (summary)
    print ("The AI has generated the following summary: ")
    print (ai_summary)
    print ("\n")
    return messages

if __name__ == '__main__':
    analyze_today_usage()
    
    messages = []
    # add system prompts to the messages
    messages.append(
        {
            "role": "system",
            "content": "You are an expert at analyzing usage behavior. Summarize the daily usage behavior of the user based on the data collected, be as detailed as possible. The summary should include the apps used, the time spent on each app, the number of times each app was used, and any other relevant information.",
        }
    )
    messages = summerize(messages)


    # Now allow the user to ask questions about the summary
    print ("-"*10 + "You can now ask questions about the summary" + "-"*10)

    # print ("You can now ask questions about the summary.")
    while True:
        current_timestamp = datetime.now().strftime('%H:%M:%S')

        time_message = "Right now the time is " + current_timestamp + ". "
        user_input = input("You: ")
        if user_input.lower() == 'exit':
            break
        # Generate a response to the user's question
        # add user input to the messages
        messages.append(
            {
                "role": "user",
                "content":  user_input,
            }
        )
        completion = client.chat.completions.create(
            model="gpt-4",
            messages=messages,
        )
        response = completion.choices[0].message.content
        print("AI: " + response)

        # 
        # add the response to the messages
        messages.append(
            {
                "role": "assistant",
                "content": response,
            }
        )
