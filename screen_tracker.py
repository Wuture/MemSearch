import pyautogui
import pytesseract
from PIL import Image
import time
import os
from AppKit import NSWorkspace
from datetime import datetime
from PIL import Image
# from active_window_tracker import ActiveWindowTracker
from active_window import get_active_window_screenshot
import numpy as np
from skimage.metrics import structural_similarity as ssim

# Perform OCR and save the data to a text file
def save_ocr_data_to_file(data, file_path):
    with open(file_path, 'w') as file:
        file.write(data)

def get_latest_file(directory):
    """Get the most recent file in a given directory."""
    files = [os.path.join(directory, f) for f in os.listdir(directory)]
    if not files:  # Check if the list is empty
        return None
    latest_file = max(files, key=os.path.getctime)
    # print (latest_file)
    return latest_file

def compare_images(img1, img2):
    """Convert images to grayscale and compute the SSIM index."""
    img1 = np.array(img1.convert('L'))  # Convert image to grayscale
    img2 = np.array(img2.convert('L'))
    score, _ = ssim(img1, img2, full=True)
    return score

def process_active_window_screenshot():
    directory = "active_screenshot"
    metadata_directory = "active_screenshot_metadata"

    if not os.path.exists(directory):
        os.makedirs(directory)
    if not os.path.exists(metadata_directory):
        os.makedirs(metadata_directory)

    # Get the current date and time
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Get active window screenshot
    active_window_screenshot, app_name, window_name = get_active_window_screenshot()

    # convert to RGB
    screenshot = active_window_screenshot.convert("RGB")
    # save to active_screenshot folder
    active_app_screenshot_name = f"active_screenshot/{app_name}_{current_date}.jpg"
    screenshot.save(active_app_screenshot_name, 'JPEG', optimize=True, quality=95)

    # Get the active window screenshot image
    active_window_screenshot_image = Image.open(active_app_screenshot_name)
    # Perform OCR on the active window screenshot image
    active_window_screenshot_data = pytesseract.image_to_data(active_window_screenshot_image)

    # save the active window screenshot data into a text file into folder active_screenshot_metadata
    active_screenshot_metadata = f"active_screenshot_metadata/{app_name}_{current_date}.txt"

    # Save the OCR data to a text file
    save_ocr_data_to_file(active_window_screenshot_data, active_screenshot_metadata)

# Process the entire screen screenshot
def process_entire_screenshot():
    # Get the list of running applications
    workspace = NSWorkspace.sharedWorkspace()
    active_app_info = workspace.activeApplication()  # Get active application info
    # get the list of running apps and the active app
    active_app_name = active_app_info.get('NSApplicationName')

    directory = "entire_screenshot"
    metadata_directory = "entire_screenshot_metadata"

    if not os.path.exists(directory):
        os.makedirs(directory)
    if not os.path.exists(metadata_directory):
        os.makedirs(metadata_directory)

    # Get the current date and time
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Capture screenshot of the screen
    entire_screenshot = pyautogui.screenshot()

    latest_file_path = get_latest_file(directory)
    # make sure its not .DS_Store file
    if latest_file_path and not latest_file_path.endswith(".DS_Store"):
        latest_screenshot = Image.open(latest_file_path)
        similarity_score = compare_images(latest_screenshot, entire_screenshot)
        # print (f"Similarity score: {similarity_score}")
        if similarity_score > 0.9:
            # print("No significant changes detected, not saving this screenshot.")
            return

    # Save the entire screenshot as an image file named with current date and time
    entire_screenshot_name = f"entire_screenshot/{active_app_name}_{current_date}.jpg"

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
    entire_screenshot_metadata = f"entire_screenshot_metadata/{active_app_name}_{current_date}.txt"

    # Save the OCR data to a text file
    save_ocr_data_to_file(entire_screenshot_data, entire_screenshot_metadata)


# process both active window and entire screen screenshot
def process_screenshot ():
    active_screenshot_directory = "active_screenshot"
    entire_screenshot_directory = "entire_screenshot"
    active_screenshot_metadata_directory = "active_screenshot_metadata"
    entire_screenshot_metadata_directory = "entire_screenshot_metadata"

    # Check if they exist, if not create them
    if not os.path.exists(active_screenshot_directory):
        os.makedirs(active_screenshot_directory)
    if not os.path.exists(entire_screenshot_directory):
        os.makedirs(entire_screenshot_directory)
    if not os.path.exists(active_screenshot_metadata_directory):
        os.makedirs(active_screenshot_metadata_directory)
    if not os.path.exists(entire_screenshot_metadata_directory):
        os.makedirs(entire_screenshot_metadata_directory)
    
    # Get the current date and time
    current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Capture screenshot of the entire screen
    entire_screenshot = pyautogui.screenshot()

    # See if there is a significant change in the entire screenshot
    latest_file_path = get_latest_file(entire_screenshot_directory)
    # make sure its not .DS_Store file
    if latest_file_path and not latest_file_path.endswith(".DS_Store"):
        latest_screenshot = Image.open(latest_file_path)
        similarity_score = compare_images(latest_screenshot, entire_screenshot)
        # print (f"Similarity score: {similarity_score}")
        if similarity_score > 0.95:
            # print("No significant changes detected, not saving this screenshot.")
            return

    # If there is a significant change, screenshot the active window
    active_window_screenshot, app_name, window_name = get_active_window_screenshot()

    # Convert the entire screenshot and active window screen shot  image from RGBA to RGB
    entire_screenshot = entire_screenshot.convert("RGB")
    active_window_screenshot = active_window_screenshot.convert("RGB")

    # Save the entire screenshot and active window screenshot as an image file named with current date and time
    entire_screenshot_name = f"{entire_screenshot_directory}/{app_name}_{current_date}.jpg"
    active_window_screenshot_name = f"{active_screenshot_directory}/{app_name}_{current_date}.jpg"

    # Save the entire screenshot and active window screenshot
    entire_screenshot.save(entire_screenshot_name, 'JPEG', optimize=True, quality=50)
    active_window_screenshot.save(active_window_screenshot_name, 'JPEG', optimize=True, quality=95)

    # Open the entire screenshot and active window screenshot image
    entire_screenshot_image = Image.open(entire_screenshot_name)
    active_window_screenshot_image = Image.open(active_window_screenshot_name)

    # Perform OCR on the entire screenshot and active window screenshot image
    entire_screenshot_data = pytesseract.image_to_data(entire_screenshot_image)
    active_window_screenshot_data = pytesseract.image_to_data(active_window_screenshot_image)

    # save the entire screenshot and active window screenshot data into a text file into folder entire_screenshot_metadata and active_screenshot_metadata
    entire_screenshot_metadata = f"{entire_screenshot_metadata_directory}/{app_name}_{current_date}.txt"
    active_screenshot_metadata = f"{active_screenshot_metadata_directory}/{app_name}_{current_date}.txt"

    # Save the OCR data to a text file
    save_ocr_data_to_file(entire_screenshot_data, entire_screenshot_metadata)
    save_ocr_data_to_file(active_window_screenshot_data, active_screenshot_metadata)


def main():

    
    while True:
        # # Process the active window screenshot
        # process_active_window_screenshot()

        # Process the entire screen screenshot
        # process_entire_screenshot()

        # Process both active window and entire screen screenshot
        process_screenshot()

        # Wait for 5 seconds before taking the next screenshot
        time.sleep(5)
        

if __name__ == "__main__":
    main()
