import pyautogui
import pytesseract
from PIL import Image
import time
import os
from AppKit import NSWorkspace
from datetime import datetime
from PIL import Image
from active_window_tracker import ActiveWindowTracker

# Perform OCR and save the data to a text file
def save_ocr_data_to_file(data, file_path):
    with open(file_path, 'w') as file:
        file.write(data)

def process_active_window_screenshot():
    # if active_screenshot folder does not exist, create one
    if not os.path.exists("active_screenshot"):
        os.makedirs("active_screenshot")
    
    # if active_screenshot_metadata folder does not exist, create one
    if not os.path.exists("active_screenshot_metadata"):
        os.makedirs("active_screenshot_metadata")

    # Get the current date and time
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Get the list of running applications
    workspace = NSWorkspace.sharedWorkspace()
    active_app_info = workspace.activeApplication()  # Get active application info
    # get the list of running apps and the active app
    active_app_name = active_app_info.get('NSApplicationName')
    tracker = ActiveWindowTracker()
    # Get the window ID of the active application

    # ------ Active Window Screenshot ------

    print (active_app_name + " is active\n")

    # Save the active window screenshot as an image file named with current date and time
    active_app_screenshot_name = f"active_screenshot/{active_app_name}_{current_date}.jpg"
    # Create an instance of the ActiveWindowTracker class
    tracker = ActiveWindowTracker()
    # Get the window ID of the active application
    window_id = tracker.get_window_id()
    # Capture the active window and save it as a screenshot
    tracker.capture_active_window(window_id, active_app_screenshot_name)

    # Get the active window screenshot image
    active_window_screenshot_image = Image.open(active_app_screenshot_name)
    # Perform OCR on the active window screenshot image
    active_window_screenshot_data = pytesseract.image_to_data(active_window_screenshot_image)

    # save the active window screenshot data into a text file into folder active_screenshot_metadata
    active_screenshot_metadata = f"active_screenshot_metadata/{active_app_name}_{current_date}.txt"

    # Save the OCR data to a text file
    save_ocr_data_to_file(active_window_screenshot_data, active_screenshot_metadata)

def process_entire_screenshot():
    # if entire_screenshot folder does not exist, create one
    if not os.path.exists("entire_screenshot"):
        os.makedirs("entire_screenshot")

    # if entire_screenshot_metadata folder does not exist, create one
    if not os.path.exists("entire_screenshot_metadata"):
        os.makedirs("entire_screenshot_metadata")

    # Get the current date and time
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Capture screenshot of the screen
    entire_screenshot = pyautogui.screenshot()

    # Save the entire screenshot as an image file named with current date and time
    entire_screenshot_name = f"entire_screenshot/screenshot_{current_date}.jpg"

    # # Convert the image from RGBA to RGB
    entire_screenshot = entire_screenshot.convert("RGB")

    # Compress the image to reduce the file size, then save it
    entire_screenshot.save(entire_screenshot_name, 'JPEG', optimize=True, quality=50)
    # entire_screenshot.save(entire_screenshot_name)

    # Open the entire screenshot image
    entire_screenshot_image = Image.open(entire_screenshot_name)
    # Perform OCR on the entire screenshot image
    # Use pytesseract to do OCR on the image
    entire_screenshot_data = pytesseract.image_to_data(entire_screenshot_image)

    # save the entire screenshot data into a text file into folder entire_screenshot_metadata
    entire_screenshot_metadata = f"entire_screenshot_metadata/screenshot_{current_date}.txt"

    # Save the OCR data to a text file
    save_ocr_data_to_file(entire_screenshot_data, entire_screenshot_metadata)

def main():

    # Continue until user type exit
    
    while True:
        # # Process the active window screenshot
        # process_active_window_screenshot(current_date)

        # Process the entire screen screenshot
        process_entire_screenshot()

        # Wait for 5 seconds before taking the next screenshot
        time.sleep(5)
        

if __name__ == "__main__":
    main()
