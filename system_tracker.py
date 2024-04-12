# import time
# import csv
# import os
# from datetime import datetime
# from AppKit import NSWorkspace

# def is_user_application(app):
#     # List of common system application bundle identifiers to exclude
#     system_app_identifiers = [
#         'com.apple.systemuiserver',
#         'com.apple.dock',
#         'com.apple.Finder',
#         'com.apple.loginwindow',
#         'com.apple.Family',
#         # Add more system application identifiers as needed
#     ]
#     return app.bundleIdentifier() not in system_app_identifiers

# def track_application_usage():
#     # Get the current date
#     current_date = datetime.now().strftime('%Y-%m-%d')
    
#     # Create a directory for storing CSV files (if it doesn't exist)
#     os.makedirs('usage_data', exist_ok=True)

#     data_path = f'usage_data/{current_date}/'
#     # Create a directory for today's data 
#     os.makedirs(data_path,exist_ok=True)
    
#     # Open the CSV file for the current date in append mode
#     csv_file_path =  os.path.join (data_path, f'{current_date}_usage.csv')
#     with open(csv_file_path, 'a', newline='') as file:
#         writer = csv.writer(file)
#         # Write the header row if the file is empty
#         if file.tell() == 0:
#             writer.writerow(['Timestamp', 'Application', 'Usage Time'])
        
#         # Dictionary to keep track of the last active application and its start time
#         last_active_app = None
#         last_active_app_start_time = None
        
#         while True:
#             # Get the current timestamp
#             current_timestamp = datetime.now()
            
#             # Get the list of running applications
#             workspace = NSWorkspace.sharedWorkspace()
#             active_app_info = workspace.activeApplication()
            
#             # Get the active application name
#             active_app_name = active_app_info.get('NSApplicationName')
            
#             # Check if the active application has changed
#             if active_app_name != last_active_app:
#                 # Write the usage data of the previous active application to the CSV file
#                 if last_active_app is not None:
#                     usage_time = current_timestamp - last_active_app_start_time
#                     usage_status = [current_timestamp.strftime('%Y-%m-%d %H:%M:%S'), last_active_app, str(usage_time)]
#                     writer.writerow(usage_status)
                
#                 # Update the last active application and its start time
#                 last_active_app = active_app_name
#                 last_active_app_start_time = current_timestamp
            
#             # Flush the file buffer to ensure data is written to disk
#             file.flush()
            
#             # Wait for a certain interval before tracking again
#             time.sleep(1)  # Adjust the interval as needed

# # Start tracking application usage
# track_application_usage()

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

def reset_tracking_data():
    # Get the current date
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    # Create a directory for storing CSV files (if it doesn't exist)
    os.makedirs('usage_data', exist_ok=True)

    data_path = f'usage_data/{current_date}/'
    # Create a directory for today's data 
    os.makedirs(data_path, exist_ok=True)

    # Open the CSV file for the current date in write mode
    csv_file_path = os.path.join(data_path, f'{current_date}_usage.csv')
    # if the CSV doesnt exist, then write 
    # Check if the CSV file already exists
    if not os.path.exists(csv_file_path):
        # Write the header row if the file is empty
        with open(csv_file_path, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Timestamp', 'Application', 'Usage Time'])

def track_application_usage():
    # Flag to track whether a new day has started
    new_day_started = False


    while True:
        # Get the current time
        current_time = datetime.now()
        
        # Check if it's after midnight and a new day has started
        if current_time.hour == 0 and current_time.minute == 0 and current_time.second == 0 and not new_day_started:
            # Reset the tracking data for the new day
            reset_tracking_data()
            new_day_started = True
        elif current_time.hour != 0 or current_time.minute != 0 or current_time.second != 0:
            # Reset the flag if it's not midnight
            new_day_started = False

            continue_tracking()

def continue_tracking():

     # Get the current date
    current_date = datetime.now().strftime('%Y-%m-%d')
    
    # Open the CSV file for the current date in append mode
    csv_file_path = os.path.join('usage_data', current_date, f'{current_date}_usage.csv')
    with open(csv_file_path, 'a', newline='') as file:
        writer = csv.writer(file)
        
        # Dictionary to keep track of the last active application and its start time
        last_active_app = None
        last_active_app_start_time = None
        
        while True:
            # Get the current timestamp
            current_timestamp = datetime.now()
            
            # Get the list of running applications
            workspace = NSWorkspace.sharedWorkspace()
            active_app_info = workspace.activeApplication()
            
            # Get the active application name
            active_app_name = active_app_info.get('NSApplicationName')
            
            # Check if the active application has changed
            if active_app_name != last_active_app:
                # Write the usage data of the previous active application to the CSV file
                if last_active_app is not None:
                    usage_time = current_timestamp - last_active_app_start_time
                    usage_status = [current_timestamp.strftime('%Y-%m-%d %H:%M:%S'), last_active_app, str(usage_time)]
                    writer.writerow(usage_status)
                
                # Update the last active application and its start time
                last_active_app = active_app_name
                last_active_app_start_time = current_timestamp
            
            # Flush the file buffer to ensure data is written to disk
            file.flush()
            
            # Wait for a certain interval before tracking again
            time.sleep(1)  # Adjust the interval as needed

if __name__ == "__main__":
    # Initialize the CSV file
    reset_tracking_data()

    # Start tracking application usage
    track_application_usage()


