import csv
from datetime import datetime, timedelta
from collections import defaultdict

def analyze_usage_behavior(csv_file_path, summary_file_path):
    # Read the CSV file
    with open(csv_file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        data = list(reader)

    # Convert usage time to timedelta
    for row in data:
        row[2] = timedelta(seconds=float(row[2].split(':')[-1]))

    # Calculate total usage time for each application
    app_usage_time = defaultdict(timedelta)
    for _, app, usage_time in data:
        app_usage_time[app] += usage_time

    # Identify most frequently used applications
    most_used_apps = sorted(app_usage_time.items(), key=lambda x: x[1], reverse=True)

    # Analyze usage patterns over time (hourly breakdown)
    hourly_usage = defaultdict(lambda: defaultdict(timedelta))
    for timestamp, app, usage_time in data:
        hour = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S').hour
        hourly_usage[hour][app] += usage_time

    # # Analyze application switching behavior
    # app_switches = defaultdict(int)
    # for i in range(1, len(data)):
    #     prev_app = data[i-1][1]
    #     curr_app = data[i][1]
    #     if prev_app != curr_app:
    #         app_switches[(prev_app, curr_app)] += 1

    # Analyze average usage duration per application
    app_usage_count = defaultdict(int)
    for _, app, usage_time in data:
        app_usage_count[app] += 1

    # Generate summary report
    with open(summary_file_path, 'w') as summary_file:
        summary_file.write("Summary Report:\n\n")
        summary_file.write("Most frequently used applications:\n")
        counter = 1
        for app, usage_time in most_used_apps:
            line = f"{counter}. {app}: {usage_time}\n"
            # print (line)/
            summary_file.write(f"{counter}. {app}: {usage_time}\n")
            # summary_file.write(f"{counter}+'. '+{app}: {usage_time}\n")
            counter += 1

    # with open(summary_file_path, 'w') as summary_file:
        summary_file.write("\nUsage patterns over time (hourly breakdown):\n")
        for hour in range(24):
            if hour == 0:
                time_format = "12 AM"
            elif hour < 12:
                time_format = f"{hour} AM"
            elif hour == 12:
                time_format = "12 PM"
            else:
                time_format = f"{hour - 12} PM"

            summary_file.write(f"{time_format}:\n")
            for app, usage_time in hourly_usage[hour].items():
                summary_file.write(f"- {app}: {usage_time}\n")

    # # with open(summary_file_path, 'w') as summary_file:            
    #     summary_file.write("\nApplication switching behavior:\n")
    #     for (app1, app2), count in app_switches.items():
    #         summary_file.write(f"{app1} -> {app2}: {count} switches\n")

        counter = 1
        # with open(summary_file_path, 'w') as summary_file:
        summary_file.write("\nAverage usage duration per application:\n")
        for app, total_time in app_usage_time.items():
            count = app_usage_count[app]
            avg_duration = total_time / count
            summary_file.write(f"{counter}. {app}: {avg_duration}\n")
            counter += 1