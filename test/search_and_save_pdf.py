from PIL import Image
import pytesseract
from PIL import ImageDraw
import os
from datetime import datetime
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

# Search for a keyword in entire screenshots and save the results as a PDF file
def search_and_save_pdf(keyword):

    # If there is no search_results folder, create one
    if not os.path.exists("search_results"):
        os.makedirs("search_results")


    # Get all the files in entire_screenshot_metadata folder
    entire_screenshot_metadata_files = os.listdir('entire_screenshot_metadata')
    entire_screenshot_metadata_files.sort()  # Ensure the order is correct

    if not entire_screenshot_metadata_files:
        print("No metadata files found. Please run the screen_tracker.py script to capture screenshots and OCR data.")
        return

    # Initialize a list to store images for the PDF
    images_for_pdf = []

    # Read the OCR data from each file, find the keyword, draw a box around it
    for file in entire_screenshot_metadata_files:
        # print(f"Searching for keyword in {file}")
        metadata_file_path = f"entire_screenshot_metadata/{file}"
        coordinate_list = find_text_coordinates(metadata_file_path, keyword)
        
        if coordinate_list:
            image_path = f"entire_screenshot/{file.replace('.txt', '.jpg')}"
            with Image.open(image_path) as img:
                draw = ImageDraw.Draw(img)
                for box in coordinate_list:
                    draw.rectangle(box, outline="red", width=3)
                img_converted = img.convert('RGB')
                images_for_pdf.append(img_converted)

    # Save the images as a PDF file if any images were found
    if images_for_pdf:
        # add timestamp to the pdf file name
        current_date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        pdf_file_name = f"search_results/search_results_{current_date}.pdf"
        images_for_pdf[0].save(pdf_file_name, save_all=True, append_images=images_for_pdf[1:])

        # open the pdf file
        os.system(f"open {pdf_file_name}")

    else:
        print("No matches found for the keyword.")

if __name__ == "__main__":
    while True:
#         # # Prompt user to enter a keyword to search in the screenshots
        keyword = input("Enter a keyword to search in your OS: ")
        search_and_save_pdf (keyword)

   