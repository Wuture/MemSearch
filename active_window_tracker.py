from asyncio import sleep
import subprocess
import Quartz
from AppKit import NSWorkspace

# Rewrite the active_window as class object
class ActiveWindowTracker:
    def __init__(self):
        pass

    def get_window_id(self):
        # Get the active workspace
        workspace = NSWorkspace.sharedWorkspace()

        # Get the PID of the active application
        active_app = workspace.frontmostApplication()

        active_app_pid = active_app.processIdentifier()
        # Get the list of windows
        window_list = Quartz.CGWindowListCopyWindowInfo(
            Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements,
            Quartz.kCGNullWindowID
        )

        # Find the window ID of the frontmost application's main window
        for window in window_list:
            if window['kCGWindowOwnerPID'] == active_app_pid and window['kCGWindowLayer'] == 0:
                return window['kCGWindowNumber']
        return None

    def capture_active_window(self, window_id, filename):
        # Use the screencapture command-line tool to capture the window by its ID
        subprocess.call(['screencapture', '-l', str(window_id), filename])



def get_active_window():
    # Get the shared workspace
    workspace = NSWorkspace.sharedWorkspace()
    
    # Get the frontmost (active) application
    active_app = workspace.frontmostApplication()
    
    # Get the bundle identifier of the active application
    bundle_identifier = active_app.bundleIdentifier()
    
    # Get the window title of the active application
    window_title = active_app.localizedName()
    
    print("Active Application Bundle Identifier:", bundle_identifier)
    print("Active Window Title:", window_title)
    
    return bundle_identifier, window_title
