import pywhatkit
import datetime
import time
import webbrowser
import pyautogui


# WhatsApp contacts directory
CONTACTS = {
    "mom": "+91XXXXXXXXXX",
    "dad": "+91XXXXXXXXXX",
    "friend": "+91XXXXXXXXXX"
}


def send_whatsapp_message(phone_number, message):
    """
    Send a WhatsApp message to a specified phone number.
    
    Args:
        phone_number (str): Phone number in international format (e.g., +91XXXXXXXXXX)
        message (str): Message to send
    
    Returns:
        tuple: (success: bool, response: str)
    """
    try:
        pywhatkit.sendwhatmsg_instantly(
            phone_no=phone_number,
            message=message,
            wait_time=10,
            tab_close=True
        )
        return True, f"Message sent to {phone_number} boss."
    except Exception as e:
        error_msg = f"Failed to send WhatsApp message: {str(e)}"
        return False, error_msg


def get_contact_number(name):
    """
    Get a contact's phone number by name.
    
    Args:
        name (str): Contact name
    
    Returns:
        str: Phone number if found, None otherwise
    """
    name = name.lower().strip()
    
    if name in CONTACTS:
        return CONTACTS[name]
    
    return None


def send_message_to_contact(contact_name, message):
    """
    Send a WhatsApp message to a named contact.
    
    Args:
        contact_name (str): Name of the contact
        message (str): Message to send
    
    Returns:
        tuple: (success: bool, response: str)
    """
    number = get_contact_number(contact_name)
    
    if number is None:
        return False, f"I don't have {contact_name}'s number boss."
    
    return send_whatsapp_message(number, message)
