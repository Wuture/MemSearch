from PIL import Image
from PIL import ImageDraw
import os
import string

# Function to find the coordinates of the target text in the OCR data
def find_text_coordinates(metadata_file_path, target_text):
    # Convert the target text to lowercase
    # target_text = target_text.lower()
    target_text = target_text.lower().translate(str.maketrans("", "", string.punctuation))
    
    # Split the target text into individual words
    target_words = target_text.split()
    
    # Open the metadata file
    with open(metadata_file_path, 'r') as file:
        data = file.read()
    
    coordinate_list = []
    matching_words = []
    
    # Split the data by lines
    for i, line in enumerate(data.splitlines()):
        if i > 0:  # Skip the first line because it contains the headers
            line_data = line.split()
            
            if len(line_data) == 12:
                x, y, width, height = map(int, line_data[6:10])
                # text = line_data[11].lower()  # Convert the OCR text to lowercase
                text = line_data[11].lower().translate(str.maketrans("", "", string.punctuation))
                
                if target_words and text == target_words[len(matching_words)]:
                    # print (text)
                    matching_words.append((x, y, width, height))
                    
                    if len(matching_words) == len(target_words):
                        # All target words found in the correct order
                        x_min = min(x for x, _, _, _ in matching_words)
                        y_min = min(y for _, y, _, _ in matching_words)
                        x_max = max(x + width for x, _, width, _ in matching_words)
                        y_max = max(y + height for _, y, _, height in matching_words)
                        
                        coordinate_list.append((x_min, y_min, x_max, y_max))
                        matching_words = []  # Reset matching words for the next search
    
    if coordinate_list:
        return coordinate_list
    
    return None

# Function to draw a box on the image
def draw_box_on_image(image_path, coordinate_list):
    # Open an image file
    with Image.open(image_path) as img:
        # Initialize the drawing context with the image as background
        draw_img = ImageDraw.Draw(img)
        for box in coordinate_list:
            # Draw a rectangle (box) in the image. The box is a tuple of (left, top, right, bottom)
            draw_img.rectangle(box, outline="red", width=3)
        
    return img


def search_keyword(keyword):

    labelled_images = []

    # Specify the directory containing the screenshots
    screenshot_directory = "entire_screenshot"

    # make sure the directory exists
    if not os.path.exists(screenshot_directory):
        print(f"Directory '{screenshot_directory}' does not exist.")
        return labelled_images
    
    # Create a list to store the screenshot paths
    screenshot_paths = []
    
    # Iterate over the files in the screenshot directory
    for filename in os.listdir(screenshot_directory):
        if filename.endswith(".jpg"):
            screenshot_path = os.path.join(screenshot_directory, filename)
            screenshot_paths.append(screenshot_path)
    
    # Iterate over the screenshot paths
    for screenshot_path in screenshot_paths:
        # Get the metadata file path corresponding to the screenshot
        metadata_file_path = os.path.join("entire_screenshot_metadata", os.path.basename(screenshot_path).replace(".jpg", ".txt"))

        # if the metadata file does not exist, skip the current iteration
        if not os.path.exists(metadata_file_path):
            continue
        
        # Find the coordinates of the keyword in the OCR data
        coordinate_list = find_text_coordinates(metadata_file_path, keyword)
        
        # Draw a box around the keyword in the screenshot
        if coordinate_list:
            img_with_box = draw_box_on_image(screenshot_path, coordinate_list)
            labelled_images.append(img_with_box)
        else:
            # print(f"Keyword '{keyword}' not found in screenshot: {screenshot_path}")
            pass 

    
    return labelled_images