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

    # Analyze usage patterns over time
    time_intervals = ['Early Morning', 'Morning', 'Noon', 'Afternoon', 'Evening', 'Night']
    interval_usage = defaultdict(lambda: defaultdict(timedelta))
    for timestamp, app, usage_time in data:
        hour = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S').hour
        if 4 <= hour < 8:
            interval = 'Early Morning'
        elif 8 <= hour < 12:
            interval = 'Morning'
        elif 12 <= hour < 14:
            interval = 'Noon'
        elif 14 <= hour < 18:
            interval = 'Afternoon'
        elif 18 <= hour < 22:
            interval = 'Evening'
        else:
            interval = 'Night'
        interval_usage[interval][app] += usage_time

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
        for app, usage_time in most_used_apps:
            summary_file.write(f"{app}: {usage_time}\n")
        summary_file.write("\nUsage patterns over time:\n")
        for interval, app_usage in interval_usage.items():
            summary_file.write(f"{interval}:\n")
            for app, usage_time in app_usage.items():
                summary_file.write(f"  {app}: {usage_time}\n")
        # summary_file.write("\nApplication switching behavior:\n")
        # for (app1, app2), count in app_switches.items():
        #     summary_file.write(f"{app1} -> {app2}: {count} switches\n")
        summary_file.write("\nAverage usage duration per application:\n")
        for app, total_time in app_usage_time.items():
            count = app_usage_count[app]
            avg_duration = total_time / count
            summary_file.write(f"{app}: {avg_duration}\n")