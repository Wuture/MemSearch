from appscript import app, k
import time
import pyautogui

from AppKit import NSWorkspace
import json

def get_active_browser_url(browser_name):
    try:
        browser = app(browser_name)
        windows = browser.windows.get()
        print (windows)
        for window in windows:
            tabs = window.tabs.get()
            for tab in tabs:
                print (tab.URL.get())
        # if windows:
        #     window = windows[0]
        #     tabs = window.tabs.get()
        #     if tabs:
        #         tab = tabs[0]
        #         return tab.URL.get()
        #     else:
        #         print(f"No active tab found in {browser_name}.")
        # else:
        #     print(f"No active window found in {browser_name}.")
    except Exception as e:
        print(f"Error: {str(e)}")
    return None

# # Get the URL of the active tab in Safari
# safari_url = get_active_browser_url('Safari')
# print("\nActive URL in Safari:", safari_url)

# arc_url = get_active_browser_url("Arc")
# print("\nActive URL in Arc: ", arc_url)

chrome_url = get_active_browser_url("Google Chrome")
print("\nActive URL in Chrome: ", chrome_url)

# while True:
#     # Get the URL of the active tab in Arc Browser
#     chrome_url = get_active_browser_url("Google Chrome")
#     print("\nActive URL in Chrome: ", chrome_url)
#     time.sleep(5)