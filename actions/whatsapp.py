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
        
        # Step 2: EXTENDED WAIT for WhatsApp to fully load and UI to be ready
        print("[DEBUG] Waiting for WhatsApp UI to load...")
        time.sleep(6)  # INCREASED - Give WhatsApp time to fully load
        
        # Step 3: Press Ctrl+F to focus search box
        print("[DEBUG] Pressing Ctrl+F to open search...")
        pyautogui.hotkey('ctrl', 'f')
        time.sleep(0.8)  # Give search box time to activate
        
        # Step 4: Select all text in search box and clear it
        pyautogui.hotkey('ctrl', 'a')
        time.sleep(0.3)
        
        # Step 5: Type contact name using clipboard (more reliable)
        print(f"[DEBUG] Pasting contact name: {contact_name}")
        pyperclip.copy(contact_name)
        time.sleep(0.2)
        pyautogui.hotkey('ctrl', 'v')
        print(f"[DEBUG] Pasted: {contact_name}")
        time.sleep(2.5)  # Wait for search results to appear
        
        # Step 6: Press Down arrow to select from search results
        print("[DEBUG] Selecting first search result...")
        pyautogui.press('down')
        time.sleep(0.5)
        
        # Step 7: Press Enter to open the selected chat
        print("[DEBUG] Opening chat...")
        pyautogui.press('enter')
        time.sleep(2)  # Wait a bit for chat selection
        
        # Step 8: EXTENDED WAIT for chat window/message input to fully load
        print("[DEBUG] Waiting for chat window to fully load...")
        time.sleep(4)  # INCREASED - Let the chat interface fully render
        
        # Step 9: Click on the message input box (bottom right area)
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
            
            # Check for direct contact mentions (more flexible matching)
            if any(word in initial_lower for word in ["myself", "self", "me only", "it myself"]):
                contact = "myself"
                print(f"[DEBUG] Detected 'myself' contact")
            elif any(word in initial_lower for word in ["minegang", "mine gang", "mind game", "my gang"]):
                contact = "minegang"
                print(f"[DEBUG] Detected 'minegang' contact")
        
        # If contact found in command, skip asking
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
