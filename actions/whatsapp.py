import pyautogui
import pytesseract
import cv2
import numpy as np
from PIL import Image
import time
import pyperclip
import subprocess
import os
import webbrowser


# Contact name aliases for easier voice commands
CONTACT_ALIASES = {
    "myself": "+91 93925 24228 (You)",
    "my own number": "+91 93925 24228 (You)",
    "my number": "+91 93925 24228 (You)",
    "me": "+91 93925 24228 (You)",
    "personal": "+91 93925 24228 (You)",
    "minegang": "Minegang",
    "mine gang": "Minegang",
}


# Tesseract OCR path
TESSERACT_PATH = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


def find_text_on_screen(search_text, confidence=50):
    """
    Find text on screen using OCR.
    
    Args:
        search_text (str): Text to search for
        confidence (int): Minimum confidence threshold (0-100)
    
    Returns:
        tuple: (center_x, center_y) if found, None otherwise
    """
    try:
        # Take full screenshot
        screenshot = pyautogui.screenshot()
        
        # Convert to numpy array
        img_array = np.array(screenshot)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Apply threshold
        _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
        
        # Use OCR to extract text data
        data = pytesseract.image_to_data(thresh, output_type=pytesseract.Output.DICT)
        
        # Loop through detected words
        for i in range(len(data['text'])):
            word = data['text'][i].lower()
            conf = int(data['conf'][i])
            
            if search_text.lower() in word and conf > confidence:
                # Calculate center of detected text
                x = data['left'][i] + data['width'][i] // 2
                y = data['top'][i] + data['height'][i] // 2
                return (x, y)
        
        return None
    
    except Exception as e:
        print(f"Error finding text on screen: {str(e)}")
        return None


def click_on_text(search_text, confidence=50):
    """
    Find text on screen and click on it.
    
    Args:
        search_text (str): Text to search for
        confidence (int): Minimum confidence threshold (0-100)
    
    Returns:
        bool: True if found and clicked, False otherwise
    """
    try:
        coords = find_text_on_screen(search_text, confidence)
        
        if coords:
            pyautogui.click(coords[0], coords[1])
            time.sleep(0.5)
            return True
        
        return False
    
    except Exception as e:
        print(f"Error clicking on text: {str(e)}")
        return False


def is_whatsapp_loaded():
    """
    Check if WhatsApp is fully loaded using OCR.
    Detects the search box text "Search or start a new chat"
    
    Returns:
        bool: True if WhatsApp UI is loaded
    """
    try:
        screenshot = pyautogui.screenshot()
        img_array = np.array(screenshot)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
        
        # Look for WhatsApp UI indicators
        for i in range(len(data['text'])):
            word = data['text'][i].lower()
            if "search" in word and ("chat" in word or "start" in word):
                print(f"[DEBUG] WhatsApp loaded! Detected: '{word}'")
                return True
            elif word == "chats":
                print(f"[DEBUG] WhatsApp loaded! Detected: 'Chats' heading")
                return True
        
        return False
    except Exception as e:
        print(f"Error checking WhatsApp load status: {str(e)}")
        return False


def wait_for_whatsapp_load(max_wait=10):
    """
    Wait for WhatsApp to load by monitoring screen for UI elements.
    
    Args:
        max_wait (int): Maximum seconds to wait
    
    Returns:
        bool: True if WhatsApp loaded, False if timeout
    """
    print(f"[DEBUG] Waiting for WhatsApp to load (max {max_wait} seconds)...")
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        if is_whatsapp_loaded():
            elapsed = time.time() - start_time
            print(f"[DEBUG] WhatsApp loaded in {elapsed:.1f} seconds")
            return True
        time.sleep(0.5)  # Check every 500ms
    
    print(f"[DEBUG] WhatsApp did not load after {max_wait} seconds")
    return False


def is_chat_message_box_ready():
    """
    Check if the chat message input box is visible using OCR.
    Detects "Type a message" placeholder text
    
    Returns:
        bool: True if message box is ready
    """
    try:
        screenshot = pyautogui.screenshot()
        img_array = np.array(screenshot)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
        
        for i in range(len(data['text'])):
            word = data['text'][i].lower()
            if "message" in word or "type" in word:
                print(f"[DEBUG] Chat message box detected: '{word}'")
                return True
        
        return False
    except Exception as e:
        print(f"Error checking message box: {str(e)}")
        return False


def wait_for_chat_load(max_wait=8):
    """
    Wait for chat window to fully load.
    
    Args:
        max_wait (int): Maximum seconds to wait
    
    Returns:
        bool: True if chat loaded, False if timeout
    """
    print(f"[DEBUG] Waiting for chat window to load (max {max_wait} seconds)...")
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        if is_chat_message_box_ready():
            elapsed = time.time() - start_time
            print(f"[DEBUG] Chat loaded in {elapsed:.1f} seconds")
            return True
        time.sleep(0.5)
    
    print(f"[DEBUG] Chat did not load after {max_wait} seconds")
    return False


def open_whatsapp():
    """
    Open WhatsApp application.
    Tries multiple paths for desktop app, falls back to web version.
    
    Returns:
        bool: True if successful
    """
    try:
        # Try multiple WhatsApp paths
        paths = [
            "C:\\Program Files\\WindowsApps\\5319275A.WhatsAppDesktop_2.2613.101.0_x64__cv1g1gvanyjgm\\WhatsApp.Root.exe",
            "C:\\Users\\akhil\\AppData\\Local\\Microsoft\\WindowsApps\\WhatsApp.exe",
            "C:\\Program Files\\WindowsApps\\WhatsApp.exe",
        ]
        
        for path in paths:
            if os.path.exists(path):
                subprocess.Popen([path])
                time.sleep(5)
                return True
        
        # Fallback: Open web WhatsApp
        webbrowser.open("https://web.whatsapp.com")
        time.sleep(5)
        return True
    
    except Exception as e:
        print(f"Error opening WhatsApp: {str(e)}")
        return False


def send_whatsapp_message(contact_name, message):
    """
    Send a WhatsApp message to a contact using screen automation for desktop app.
    
    Args:
        contact_name (str): Name of the contact
        message (str): Message to send
    
    Returns:
        tuple: (success: bool, response: str)
    """
    try:
        # Step 0: Map contact aliases to actual contact names
        contact_lower = contact_name.lower().strip()
        if contact_lower in CONTACT_ALIASES:
            contact_name = CONTACT_ALIASES[contact_lower]
            print(f"[DEBUG] Mapped '{contact_lower}' to '{contact_name}'")
        
        # Step 1: Open WhatsApp (if not already open)
        open_whatsapp()
        
        # Step 2: Wait for WhatsApp to load by monitoring screen (adaptive wait)
        if not wait_for_whatsapp_load(max_wait=10):
            return False, "WhatsApp took too long to load boss."
        
        # Step 3: Click on WhatsApp window to ensure focus
        print("[DEBUG] Clicking on WhatsApp to ensure focus...")
        pyautogui.click(900, 300)  # Click on the right side to avoid opening chats
        time.sleep(0.3)
        
        # Step 4: Press Ctrl+F to focus search box
        print("[DEBUG] Pressing Ctrl+F to open search...")
        pyautogui.hotkey('ctrl', 'f')
        time.sleep(0.8)  # Give search box time to activate
        
        # Step 5: Select all text in search box and clear it
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.3)
        
        # Step 6: Type contact name using clipboard (more reliable)
        print(f"[DEBUG] Pasting contact name: {contact_name}")
        pyperclip.copy(contact_name)
        time.sleep(0.2)
        pyautogui.hotkey('ctrl', 'v')
        print(f"[DEBUG] Pasted: {contact_name}")
        time.sleep(2.5)  # Wait for search results to appear
        
        # Step 7: Press Down arrow to select from search results
        print("[DEBUG] Selecting first search result...")
        pyautogui.press('down')
        time.sleep(0.5)
        
        # Step 7: Press Enter to open the selected chat
        print("[DEBUG] Opening chat...")
        pyautogui.press('enter')
        
        # Step 8: Wait for chat window to load by monitoring screen (adaptive wait)
        if not wait_for_chat_load(max_wait=8):
            print("[DEBUG] Warning: Chat may not have fully loaded, proceeding anyway...")
        
        # Step 10: Click on the message input box (bottom right area)
        # "Type a message" box coordinates
        msg_input_x, msg_input_y = 900, 732
        print(f"[DEBUG] Clicking message input at ({msg_input_x}, {msg_input_y})")
        pyautogui.click(msg_input_x, msg_input_y)
        time.sleep(1)
        
        # Step 10: Type the message
        print(f"[DEBUG] Typing message: {message}")
        pyperclip.copy(message)
        time.sleep(0.2)
        pyautogui.hotkey('ctrl', 'v')
        print(f"[DEBUG] Message pasted")
        time.sleep(0.5)
        
        # Step 11: Press Enter to send
        print("[DEBUG] Sending message...")
        pyautogui.press('enter')
        time.sleep(0.5)
        
        print("[DEBUG] Message sent successfully!")
        return True, f"Message sent to {contact_name} boss."
    
    except Exception as e:
        print(f"[ERROR] WhatsApp error: {str(e)}")
        return False, f"Failed boss: {str(e)}"


def send_whatsapp_flow(initial_command=""):
    """
    Interactive flow for sending WhatsApp message using voice.
    Smart contact detection from initial command.
    
    Args:
        initial_command (str): Initial command that triggered this flow (e.g., 'to self', 'minegang')
    
    Returns:
        str: Result message
    """
    try:
        from voice.tts import speak
        from voice.stt import listen
        
        # Step 1: Determine contact
        contact = None
        
        # Debug: Show what we received
        print(f"[DEBUG] send_whatsapp_flow initial_command: '{initial_command}'")
        
        # Parse contact from initial command if available
        if initial_command:
            initial_lower = initial_command.lower().strip()
            print(f"[DEBUG] Checking contact from: '{initial_lower}'")
            
            # First, check for direct contact aliases using word boundaries
            import re
            for alias in CONTACT_ALIASES.keys():
                # Use word boundaries to match whole words only
                pattern = r'\b' + re.escape(alias) + r'\b'
                if re.search(pattern, initial_lower):
                    contact = alias
                    print(f"[DEBUG] Detected alias: {alias}")
                    break
            
            # If no alias found, try to extract contact name from command
            # Look for patterns like "to [name]" or "message [name]"
            if not contact:
                # Pattern: to [word]
                match = re.search(r'to\s+(\w+)', initial_lower)
                if match:
                    contact = match.group(1)
                    print(f"[DEBUG] Extracted contact from command: {contact}")
        
        # If contact found in command, use it
        if contact:
            print(f"[DEBUG] Contact detected from command: {contact}")
            speak(f"Messaging {contact} boss.")
        else:
            # Only ask if contact not detected from command
            print("[DEBUG] No contact detected, asking user")
            speak("Who should I message boss?")
            contact = listen()
        
        if not contact:
            return "Couldn't hear the contact name boss."
        
        # Step 2: Ask for message
        speak(f"What should I say boss?")
        message = listen()
        
        if not message:
            return "Couldn't hear the message boss."
        
        # Step 3: Send message
        speak(f"Sending message boss.")
        success, msg = send_whatsapp_message(contact, message)
        
        return msg
    
    except Exception as e:
        print(f"[ERROR] WhatsApp flow error: {str(e)}")
        return f"WhatsApp flow error: {str(e)}"


def send_message_to_contact(contact_name, message):
    """
    Wrapper function for sending WhatsApp message to a contact.
    
    Args:
        contact_name (str): Name of the contact
        message (str): Message to send
    
    Returns:
        tuple: (success: bool, response: str)
    """
    return send_whatsapp_message(contact_name, message)
