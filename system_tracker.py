import time
import csv
import os
from datetime import datetime, timedelta
from AppKit import NSWorkspace

def is_user_application(app):
    # List of common system application bundle identifiers to exclude
    system_app_identifiers = [
        'com.apple.systemuiserver',
        'com.apple.dock',
        'com.apple.Finder',
        'com.apple.loginwindow',
        'com.apple.Family',
        # Add more system application identifiers as needed
    ]

    return app.bundleIdentifier() not in system_app_identifiers

def track_application_usage():
    # Get the current date
    current_date = datetime.now().strftime('%Y-%m-%d')

    # Create a directory for storing CSV files (if it doesn't exist)
    os.makedirs('usage_data', exist_ok=True)

    # Dictionary to keep track of running applications and their start times
    running_apps_dict = {}


    # Open the CSV file for the current date in append mode
    csv_file_path = f'usage_data/{current_date}.csv'
    with open(csv_file_path, 'a', newline='') as file:
        writer = csv.writer(file)

        # Write the header row if the file is empty
        if file.tell() == 0:
            writer.writerow(['Timestamp', 'Application', 'Bundle Identifier', 'Start Time', 'Status (Active/Dormant'])

        while True:
            # Get the list of running applications
            workspace = NSWorkspace.sharedWorkspace()
            running_apps = workspace.runningApplications()
            active_app_info = workspace.activeApplication()  # Get active application info
            active_app_name = active_app_info.get('NSApplicationName')  # Get the name of the active app

            print (active_app_name)
            # Get the current timestamp
            current_timestamp = datetime.now()

            # Iterate over each running application
            for app in running_apps:
                try:
                    # Get application information
                    app_name = app.localizedName()
                    app_bundle_id = app.bundleIdentifier()

                    # Check if the application is user-opened (not a system application)
                    if is_user_application(app):
                        # Get the application's process information
                        status = "Active" if app_name == active_app_name else "Dormant"
                        app_pid = app.processIdentifier()
                        app_start_time = datetime.fromtimestamp(app.launchDate().timeIntervalSince1970())

                        # Check if the start time is from a previous day
                        if app_start_time.date() < current_timestamp.date():
                            # Reset the start time to midnight of the current day
                            app_start_time = current_timestamp.replace(hour=0, minute=0, second=0, microsecond=0)

                        # Calculate the duration of the application
                        duration = (current_timestamp - app_start_time).total_seconds()

                        data = [current_timestamp, app_name, app_bundle_id, app_start_time, status]

                        # print(data)
                        # Write the application usage data to the CSV file
                        writer.writerow(data)
                        print (data)

                except AttributeError:
                    pass

            # Flush the file buffer to ensure data is written to disk
            file.flush()

            # Wait for a certain interval before tracking again
            time.sleep(5)  # Adjust the interval as needed

# Start tracking application usage
track_application_usage()


