from pydantic import create_model
import inspect, json 
from inspect import Parameter
import platform
import subprocess


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


# sum two numbers
def sums(a: int, b: int) -> int:
    "Adds a and b and returns the result"    
    return a + b

def generate_scheme_from_function(f):
    kw = {n:(o.annotation, ... if o.default==Parameter.empty else o.default)
        for n,o in inspect.signature(f).parameters.items()}
    s = create_model(f'Input for `{f.__name__}`', **kw).schema()
    return dict(name=f.__name__, description=f.__doc__, parameters=s)

def send_sms(to: str, message: str) -> str:
        "Sends an SMS message to the specified recipient using the Messages app."
        # Check if the operating system is MacOS, as this functionality is MacOS-specific.
        if platform.system() != 'Darwin':
            return "This method is only supported on MacOS"
        
        # Remove any newline characters from the recipient number.
        to = to.replace("\n", "")
        # Escape double quotes in the message and recipient variables to prevent script errors.
        escaped_message = message.replace('"', '\\"')
        escaped_to = to.replace('"', '\\"')

        script = f"""
        tell application "Messages"                                                   
            set targetBuddy to buddy "{escaped_to}" of service 1                        
            send "{escaped_message}" to targetBuddy                                
        end tell 
        """
        try:
            run_applescript(script)
            return "SMS message sent"
        except subprocess.CalledProcessError:
            return "An error occurred while sending the SMS. Please check the recipient number and try again."



# print (generate_scheme_from_function(send_sms))