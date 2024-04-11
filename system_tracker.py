import time
import csv
import os
from datetime import datetime
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

    data_path = f'usage_data/{current_date}/'
    # Create a directory for today's data 
    os.makedirs(data_path,exist_ok=True)
    
    # Open the CSV file for the current date in append mode
    csv_file_path =  os.path.join (data_path, f'{current_date}_usage.csv')
    with open(csv_file_path, 'a', newline='') as file:
        writer = csv.writer(file)
        # Write the header row if the file is empty
        if file.tell() == 0:
            writer.writerow(['Timestamp', 'Application', 'Usage Time'])
        
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

# Start tracking application usage
track_application_usage()

