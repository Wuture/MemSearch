import Quartz
from AppKit import NSWorkspace
import pyautogui
import subprocess
from io import BytesIO
import base64


# screenshot based on the active window
def screenshot (window):
    # Get the coordinates and dimensions of the active window
    x = window['kCGWindowBounds']['X']
    y = window['kCGWindowBounds']['Y']
    width = window['kCGWindowBounds']['Width']
    height = window['kCGWindowBounds']['Height']

    app_name = window['kCGWindowOwnerName']
    window_name = window['kCGWindowName']

    # make them integers
    x, y, width, height = int(x), int(y), int(width), int(height)

    # Capture the active window
    screenshot = pyautogui.screenshot(region=(x, y, width, height))
    
    # return the screenshot, app name, and window name
    return screenshot, app_name, window_name


# Get the active window and take a screenshot
def get_active_window_screenshot ():
    # Get the active window
    options = Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements
    active_window_list = Quartz.CGWindowListCopyWindowInfo(options, Quartz.kCGNullWindowID)

    # Get the list of running applications
    workspace = NSWorkspace.sharedWorkspace()
    active_app_info = workspace.activeApplication()

    # Get the active application name
    active_app_name = active_app_info.get('NSApplicationName')

    # Iterate through all windows to find the active window
    for window in active_window_list:
        if window['kCGWindowOwnerName'] == active_app_name and window['kCGWindowName'] != '':
            # screenshot based on the active window
            results  = screenshot(window)
            # print (window['kCGWindowOwnerName'])
            # print (results)
            return results 
        

def run_applescript(script):
    """
    Runs the given AppleScript using osascript and returns the result.
    """
    # print("Running this AppleScript:\n", script)
    # print(
    #     "---\nFeel free to directly run AppleScript to accomplish the user's task. This gives you more granular control than the `computer` module, but it is slower."
    # )
    args = ["osascript", "-e", script]
    return subprocess.check_output(args, universal_newlines=True)


def run_applescript_capture(script):
    """
    Runs the given AppleScript using osascript, captures the output and error, and returns them.
    """
    # print("Running this AppleScript:\n", script)
    # print(
    #     "---\nFeel free to directly run AppleScript to accomplish the user's task. This gives you more granular control than the `computer` module, but it is slower."
    # )
    args = ["osascript", "-e", script]
    result = subprocess.run(args, capture_output=True, text=True, check=False)
    stdout, stderr = result.stdout, result.stderr
    return stdout, stderr


# Function to encode the image
def encode_image(image):
    buffered = BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')
