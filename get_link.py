from appscript import app
import pyautogui

def get_active_browser_url(browser_name):
    try:
        browser = app(browser_name)
        window = browser.windows.first.get()
        tab = window.tabs.first.get()
        return tab.URL.get()
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

# Get the URL of the active tab in Arc Browser
chrome_url = get_active_browser_url("Google Chrome")
print("Active URL in ARC:", chrome_url)

# Get the URL of the active tab in Safari
safari_url = get_active_browser_url('Safari')
print("Active URL in Safari:", safari_url)

def get_active_browser_url():
    try:
        # Simulate pressing Command+L to focus on the address bar
        pyautogui.hotkey('command', 'l')
        
        # Simulate pressing Command+C to copy the URL
        pyautogui.hotkey('command', 'c')
        
        # Retrieve the copied URL from the clipboard
        url = pyautogui.clipboard.paste()
        
        return url
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

# Get the URL of the active tab in the frontmost browser
active_url = get_active_browser_url()
print("Active URL:", active_url)