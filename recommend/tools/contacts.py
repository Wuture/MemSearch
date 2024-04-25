import platform
from app_utils import run_applescript_capture

class Contacts:
    @staticmethod
    def get_phone_number(contact_name):
        print ("The contact name is:", contact_name)

        """
        Returns the phone number of a contact by name.
        """
        if platform.system() != 'Darwin':
            return "This method is only supported on MacOS"
        
        script = f'''
        tell application "Contacts"
            set thePerson to first person whose name is "{contact_name}"
            set theNumber to value of first phone of thePerson
            return theNumber
        end tell
        '''
        stout, stderr = run_applescript_capture(script)
        # If the person is not found, we will try to find similar contacts
        if "Can’t get person" in stderr:
            names= Contacts.get_full_names_from_first_name(contact_name)
            if names == "No contacts found":
                return "No contacts found"
            else:
                # Language model friendly error message
                return f"A contact for '{contact_name}' was not found, perhaps one of these similar contacts might be what you are looking for? {names} \n Please try again and provide a more specific contact name."
        else:
            print ("The phone number is:", stout.replace('\n', ''))
            return stout.replace('\n', '')

    @staticmethod
    def get_email_address(contact_name):
        print ("The contact name is:", contact_name)    
        """
        Returns the email address of a contact by name.
        """
        if platform.system() != 'Darwin':
            return "This method is only supported on MacOS"
        
        script = f'''
        tell application "Contacts"
            set thePerson to first person whose name is "{contact_name}"
            set theEmail to value of first email of thePerson
            return theEmail
        end tell
        '''
        stout, stderr = run_applescript_capture(script)
        # If the person is not found, we will try to find similar contacts
        if "Can’t get person" in stderr:
            names= Contacts.get_full_names_from_first_name(contact_name)
            if names == "No contacts found":
                return "No contacts found"
            else:
                # Language model friendly error message
                return f"A contact for '{contact_name}' was not found, perhaps one of these similar contacts might be what you are looking for? {names} \n Please try again and provide a more specific contact name."
        else:
            return stout.replace('\n', '')

    @staticmethod
    def get_full_names_from_first_name(contact, first_name):
        
        """
        Returns a list of full names of contacts that contain the first name provided.
        """
        if platform.system() != 'Darwin':
            return "This method is only supported on MacOS"
        
        script = f'''
        tell application "Contacts"
            set matchingPeople to every person whose name contains "{first_name}"
            set namesList to {{}}
            repeat with aPerson in matchingPeople
                set end of namesList to name of aPerson
            end repeat
            return namesList
        end tell
        '''
        names, _ = run_applescript_capture(script)

        print ("The full names are:", names)
        if names:
            return names
        else:
            return "No contacts found."
        