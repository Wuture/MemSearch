import openai
import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import datetime
from dateutil.parser import parse
from openai import OpenAI

def authenticate_google_calendar():
    scopes = ['https://www.googleapis.com/auth/calendar']
    flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', scopes=scopes)
    credentials = flow.run_local_server(port=0)
    return credentials

def get_calendar_events(credentials, max_results=10):
    service = build('calendar', 'v3', credentials=credentials)
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=max_results, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    return events

def suggest_optimal_time(credentials, user_constraints):
    events = get_calendar_events(credentials)
    event_data = "Here are the scheduled events:\n"
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        event_data += f"Event: {event['summary']} from {start} to {end}\n"

    current_datetime = datetime.datetime.utcnow().isoformat() + 'Z'

    client = OpenAI()
    prompt = f"As of {current_datetime}, {event_data} User constraints: {user_constraints}"

    response = client.chat.completions.create(
      model="gpt-4-turbo",
      messages=[
          {"role": "system", "content": "You are an AI event scheduler assistant. The user has provided you with a list of events and some constraints for the meeting time. Your goal is to suggest the best time for the meeting based on the user's constraints and the existing events on their calendar. Avoid any time before 9am and after 9pm. Only return the best date and time in RFC3339 date format. For example, just return '2022-01-01T12:00:00Z' and nothing else in your response."},
          {"role": "user", "content": prompt}
      ]
    )
    
    print("Response:", response.choices[0])
    suggested_time = response.choices[0].message.content
    print("Suggested Optimal Time:", suggested_time)
    return suggested_time

def create_calendar_event(credentials, summary, location, start_time, end_time, attendees):
    service = build('calendar', 'v3', credentials=credentials)
    event = {
        'summary': summary,
        'location': location,
        'description': "This event was scheduled using MySocialApp.",
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

def parse_and_schedule_event(credentials, suggested_time, summary, location, attendees):
    start_time = parse(suggested_time)
    end_time = start_time + datetime.timedelta(hours=1)  # assuming the meeting lasts one hour

    # Format times to RFC3339
    start_time = start_time.isoformat()
    end_time = end_time.isoformat()

    create_calendar_event(credentials, summary, location, start_time, end_time, attendees)

if __name__ == '__main__':
    credentials = authenticate_google_calendar()
    summary = input("Enter the meeting name: ")
    location = input("Enter the meeting location (or 'Virtual' if online): ")
    attendees = input("Enter the email addresses of the attendees, separated by commas: ").split(',')
    user_input = input("Please enter any specific time constraints (e.g., 'Preferably on a weekday afternoon next week'): ")
    suggested_time = suggest_optimal_time(credentials, user_input)
    if suggested_time:
        parse_and_schedule_event(credentials, suggested_time, summary, location, attendees)
