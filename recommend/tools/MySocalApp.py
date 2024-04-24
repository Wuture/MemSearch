import openai
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import datetime
from dateutil.parser import parse
from openai import OpenAI
import json
import pytesseract
from PIL import Image
import re

client = OpenAI()

def authenticate_google_calendar():
    scopes = ['https://www.googleapis.com/auth/calendar']
    flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', scopes=scopes)
    credentials = flow.run_local_server(port=0)
    return credentials

def get_calendar_events(credentials, max_results=10):
    try:
        service = build('calendar', 'v3', credentials=credentials)
        print (service)
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    # events_result = service.events().list(calendarId='primary', timeMin=now,
    #                                       maxResults=max_results, singleEvents=True,
    #                                       orderBy='startTime').execute()

    # catch service events error
    try:
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=max_results, singleEvents=True,
                                              orderBy='startTime').execute()
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    
    events = events_result.get('items', [])
    return events

def create_calendar_event(credentials, summary, location, description, start_time, end_time, attendees):
    try:
        service = build('calendar', 'v3', credentials=credentials)
        print (service)
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    event = {
        'summary': summary,
        'location': location,
        'description': description,
        'start': {
            'dateTime': start_time,
            'timeZone': 'UTC',
        },
        'end': {
            'dateTime': end_time,
            'timeZone': 'UTC',
        },
        'attendees': [{'email': email} for email in attendees]
    }
    
    event = service.events().insert(calendarId='primary', body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))
    return event

def is_valid_email(email):
    # Simple regex for validating an email address, for a more complex validation consider using a library
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def get_valid_emails(attendees):
    valid_emails = []
    invalid_emails = []
    if "," in attendees:
        list_of_emails = attendees.split(',')
    else:
        list_of_emails = [attendees]
    for email in list_of_emails:
        if is_valid_email(email):
            valid_emails.append({'email': email})
        else:
            invalid_emails.append(email)
    return valid_emails, invalid_emails

def reprompt_for_missing_details(missing_fields):
    updated_details = {}
    print("Some details are missing or invalid. Please provide the following:")
    for field in missing_fields:
        updated_value = input(f"Enter {field}: ")
        updated_details[field] = updated_value
    return updated_details

def validate_event_details(details):
    missing_fields = []
    invalid_fields = {}

    print(details)

    # Check required fields
    required_fields = ['summary', 'location', 'description', 'attendees']
    for field in required_fields:
        if not details.get(field):
            missing_fields.append(field)

    # Validate email fields
    if 'attendees' in details and details['attendees']:
        valid_emails, invalid_emails = get_valid_emails(details['attendees'])
        if invalid_emails:
            invalid_fields['attendees'] = invalid_emails
        details['attendees'] = valid_emails

    return missing_fields, invalid_fields


def extract_text_from_image(image_path):
    try:
        return pytesseract.image_to_string(Image.open(image_path))
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def extract_event_details(user_input):
    message = '''
    You are a helpful assistant. Only return the event details into JSON format including meeting name, location, description, attendees separated by comma if multiple and time preferences.
    Sample JSON format to return if multiple attendees present: {'summary': 'Meeting with John and Alice', 'location': 'Coffee Shop', 'description': 'Discuss project details', 'attendees': 'john@example.com,alice@example.com', 'time_preferences': 'Next Tuesday at 3PM'\n
    Sample JSON format to return if single attendee present: {'summary': 'Meeting with John and Alice', 'location': 'Coffee Shop', 'description': 'Discuss project details', 'attendees': 'john@example.com', 'time_preferences': 'Next Tuesday at 3PM'
    '''
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[
            {"role": "system", "content": message},
            {"role": "user", "content": user_input}
        ],
        temperature=0
    )
    details_json = response.choices[0].message.content
    return details_json

def suggest_optimal_time(credentials, user_constraints):
    events = get_calendar_events(credentials)
    event_data = "Here are the scheduled events:\n"
    print ("All events:", events)
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        event_data += f"Event: {event['summary']} from {start} to {end}\n"

    current_datetime = datetime.datetime.utcnow().isoformat() + 'Z'

    prompt = f"As of today:{current_datetime},\n {event_data}\n with time preference: {user_constraints}"

    response = client.chat.completions.create(
      model="gpt-4-turbo",
      messages=[
          {"role": "system", "content": f"You are an AI event scheduler assistant and today's date is {current_datetime}. Your goal is to suggest the best time for the meeting based on any mentioned time preferences and the existing events on their calendar. Avoid any time before 9am and after 9pm. Only return the best date and time in RFC3339 date format. For example, just return '2022-01-01T12:00:00Z' and nothing else in your response."},
          {"role": "user", "content": prompt}
      ],
      temperature=0
    )
    
    suggested_time = response.choices[0].message.content
    print("Suggested Optimal Time:", suggested_time)
    return suggested_time

def suggest_and_schedule_event(credentials, details_json):
    details = json.loads(details_json)  # Convert JSON string back to dictionary
    missing_fields, invalid_fields = validate_event_details(details)
    
    # Loop to handle missing fields
    while missing_fields:
        print(f"Missing required details: {', '.join(missing_fields)}")
        new_details = reprompt_for_missing_details(missing_fields)
        # Update details with the new information provided by the user
        details.update(new_details)
        # Re-validate the updated details
        missing_fields, invalid_fields = validate_event_details(details)
    
    # Loop to handle invalid fields
    while invalid_fields.get('attendees'):
        print("Invalid email addresses:", ', '.join(invalid_fields['attendees']))
        new_emails = input("Enter valid email addresses separated by commas: ").split(',')
        # Update the details with the new emails
        details['attendees'], invalid_emails = get_valid_emails(new_emails)
        invalid_fields['attendees'] = invalid_emails
    
    summary = details.get("summary")
    location = details.get("location")
    description = details.get("description")
    attendees = [attendee['email'] for attendee in details.get("attendees", [])]
    user_constraints = details.get("time_preferences")
    print("Details:", details)
    
    suggested_time = suggest_optimal_time(credentials, user_constraints)
    print ("The suggested time is:", suggested_time)
    if suggested_time:
        return parse_and_schedule_event(credentials, suggested_time, summary, location, description, attendees)


def parse_and_schedule_event(credentials, suggested_time, summary, location, description, attendees):
    start_time = parse(suggested_time)
    end_time = start_time + datetime.timedelta(hours=1)  # assuming the meeting lasts one hour

    # Format times to RFC3339
    start_time = start_time.isoformat()
    end_time = end_time.isoformat()

    return create_calendar_event(credentials, summary, location, description, start_time, end_time, attendees)

def schedule_event_from_description():
    credentials = authenticate_google_calendar()
    user_input = input("Please describe the event you want to schedule, including the name, location, description, attendees, and any time preferences: ")
    event_details = extract_event_details(user_input)
    suggest_and_schedule_event(credentials, event_details)

def extract_details_from_image_and_schedule(image_path):
    text = extract_text_from_image(image_path)
    if text:
        event_details_json = extract_event_details(text)
        credentials = authenticate_google_calendar()
        suggest_and_schedule_event(credentials, event_details_json)
    else:
        print("No text could be extracted from the image.")

if __name__ == '__main__':
    #schedule_event_from_description()
    extract_details_from_image_and_schedule('sample_image_2.png')

def create_google_calendar_event (snapshot_details):
    print('snapshot_details:', snapshot_details)
    credentials = authenticate_google_calendar()
    #user_input = input("Please describe the event you want to schedule, including the name, location, description, attendees, and any time preferences: ")
    event_details = extract_event_details(snapshot_details)
    return suggest_and_schedule_event(credentials, event_details)
