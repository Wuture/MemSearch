import os
import datetime
import platform
import subprocess
from app_utils import run_applescript, run_applescript_capture

calendar_app = "Calendar"
def create_event(
    title: str,
    start_date: datetime.datetime,
    end_date: datetime.datetime,
    location: str = "",
    notes: str = "",
    calendar: str = None,
) -> str:
    """
    Creates a new calendar event in the default calendar with the given parameters using AppleScript.
    """
    if platform.system() != "Darwin":
        return "This method is only supported on MacOS"

    # Format datetime for AppleScript
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S')
    applescript_start_date = start_date.strftime("%B %d, %Y at %I:%M:%S %p")
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%dT%H:%M:%S')
    applescript_end_date = end_date.strftime("%B %d, %Y at %I:%M:%S %p")

    # If there is no calendar, lets use the first calendar applescript returns. This should probably be modified in the future
    if calendar is None:
        calendar = get_first_calendar()
        if calendar is None:
            return "Can't find a default calendar. Please try again and specify a calendar name."

    script = f"""
    -- Open and activate calendar first
    tell application "System Events"
        set calendarIsRunning to (name of processes) contains "{calendar_app}"
        if calendarIsRunning then
            tell application "{calendar_app}" to activate
        else
            tell application "{calendar_app}" to launch
            delay 1 -- Wait for the application to open
            tell application "{calendar_app}" to activate
        end if
    end tell
    tell application "{calendar_app}"
        tell calendar "{calendar}"
            set startDate to date "{applescript_start_date}"
            set endDate to date "{applescript_end_date}"
            make new event at end with properties {{summary:"{title}", start date:startDate, end date:endDate, location:"{location}", description:"{notes}"}}
        end tell
        -- tell the Calendar app to refresh if it's running, so the new event shows up immediately
        tell application "{calendar_app}" to reload calendars
    end tell
    """

    try:
        run_applescript(script)
        return f"""Event created successfully in the "{calendar}" calendar."""
    except subprocess.CalledProcessError as e:
        return str(e)
    
def get_first_calendar() -> str:
    # Literally just gets the first calendar name of all the calendars on the system. AppleScript does not provide a way to get the "default" calendar
    script = f"""
        -- Open calendar first
        tell application "System Events"
            set calendarIsRunning to (name of processes) contains "{calendar_app}"
            if calendarIsRunning is false then
                tell application "{calendar_app}" to launch
                delay 1 -- Wait for the application to open
            end if
        end tell
        tell application "{calendar_app}"
        -- Get the name of the first calendar
            set firstCalendarName to name of first calendar
        end tell
        return firstCalendarName
        """
    stdout = run_applescript_capture(script)
    print (stdout)
    if stdout:
        return stdout[0].strip()
    else:
        return None

# # test get_first_calendar
# print (get_first_calendar())

# test create_event
title = "Meeting with John"
start_date = "2024-04-18T09:00:00"
end_date = "2024-04-18T10:00:00"
location = "Starbucks"
notes = "Discuss project timeline"
calendar = "Work"
print (create_event(title, start_date, end_date, location, notes, calendar))
