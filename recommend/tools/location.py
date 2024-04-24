import subprocess
from urllib.parse import quote

def search_location_in_maps(location):
    """
    Opens the specified location in Apple Maps using a command line instruction to open the web browser.

    Args:
    location (str): The location to search for, as an address or place name.

    Returns:
    str: A message indicating that the command was executed, or an error message if it fails.
    """
    # URL encode the location for use in a URL
    location_encoded = quote(location)

    # Construct the URL for Apple Maps
    url = f"https://maps.apple.com/?address={location_encoded}"

    # Construct the command to open the URL in the default web browser
    command = ['open', url]

    # Execute the command using subprocess
    try:
        subprocess.run(command, check=True)
        return "Apple Maps opened in browser via command line."
    except subprocess.CalledProcessError as e:
        return f"Failed to open Apple Maps: {e}"

