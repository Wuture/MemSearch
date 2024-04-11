import datetime
import os
import csv

# # Get the current date
# current_date = datetime.date.today().strftime('%Y-%m-%d')

# # Create a directory for storing CSV files (if it doesn't exist)
# os.makedirs('usage_data', exist_ok=True)

# data_path = f'usage_data/{current_date}/'
# # Create a directory for today's data 
# os.makedirs(data_path, exist_ok=True)

# # Open the CSV file for the current date in append mode
# csv_file_path =  os.path.join (data_path, f'{current_date}.csv')
# with open(csv_file_path, 'a', newline='') as file:
#     writer = csv.writer(file)
#     # Write the header row if the file is empty
#     if file.tell() == 0:
#         writer.writerow(['Timestamp', 'Application', 'Usage Time'])


# datetime.now().strftime("%H:%M:%S")


text = "Messages: sehran"
print (text.split(': '))