from appscript import app, k
import time
import pyautogui


def get_active_browser_url(browser_name):
    try:
        browser = app(browser_name)
        windows = browser.windows.get()
        if windows:
            window = windows[0]
            tabs = window.tabs.get()
            if tabs:
                tab = tabs[0]
                return tab.URL.get()
            else:
                print(f"No active tab found in {browser_name}.")
        else:
            print(f"No active window found in {browser_name}.")
    except Exception as e:
        print(f"Error: {str(e)}")
    return None

# Get the URL of the active tab in Arc Browser
chrome_url = get_active_browser_url("Google Chrome")
print("\nActive URL in Chrome: ", chrome_url)

# Get the URL of the active tab in Safari
safari_url = get_active_browser_url('Safari')
print("\nActive URL in Safari:", safari_url)

# arc_url = get_active_browser_url("Arc")
# print("\nActive URL in Arc: ", arc_url)


def make_links_clickable(image_path):
    try:
        # Open the image in Preview
        preview = app('Preview')
        preview.open(image_path)
        
        # # Wait for the image to load
        # time.sleep(2)
        
        # # Get the current document
        # document = preview.documents.first.get()
        
        # # Enable editing mode
        # document.editable.set(True)
        
        # # Enable link annotations
        # document.link_annotations_enabled.set(True)
        
        # # Save the changes
        # document.save()
        
        # # Close the document
        # document.close()
        
        print("Links on the image are now clickable.")
    except Exception as e:
        print(f"Error: {str(e)}")

# Specify the path to your image file
image_path = ""

# Make the links on the image clickable
make_links_clickable('test/test.png')

# def get_active_browser_url():
#     try:
#         # Simulate pressing Command+L to focus on the address bar
#         pyautogui.hotkey('command', 'l')
        
#         # Simulate pressing Command+C to copy the URL
#         pyautogui.hotkey('command', 'c')
        
#         # Retrieve the copied URL from the clipboard
#         url = pyautogui.clipboard.paste()
        
#         return url
#     except Exception as e:
#         print(f"Error: {str(e)}")
#         return None

# # Get the URL of the active tab in the frontmost browser
# active_url = get_active_browser_url()
# print("Active URL:", active_url)