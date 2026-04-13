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
    Send a WhatsApp message to a contact using screen automation.
    
    Args:
        contact_name (str): Name of the contact
        message (str): Message to send
    
    Returns:
        tuple: (success: bool, response: str)
    """
    try:
        # Step 1: Open WhatsApp
        open_whatsapp()
        
        # Step 2: Find and click search box
        if not click_on_text("Search"):
            if not click_on_text("search or start"):
                pyautogui.hotkey('ctrl', 'f')
        time.sleep(1)
        
        # Step 3: Type contact name
        pyperclip.copy(contact_name)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(2)
        
        # Step 4: Find contact in results
        coords = find_text_on_screen(contact_name)
        if coords:
            pyautogui.click(coords[0], coords[1])
        else:
            pyautogui.press('enter')
        time.sleep(1)
        
        # Step 5: Find and click message box
        if not click_on_text("Type a message"):
            if not click_on_text("message"):
                pyautogui.press('tab')
        time.sleep(0.5)
        
        # Step 6: Type and send message
        pyperclip.copy(message)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.3)
        pyautogui.press('enter')
        time.sleep(0.5)
        
        return True, f"Message sent to {contact_name} boss."
    
    except Exception as e:
        return False, f"Failed boss: {str(e)}"


def send_whatsapp_flow():
    """
    Interactive flow for sending WhatsApp message using voice.
    
    Returns:
        str: Result message
    """
    try:
        from voice.tts import speak
        from voice.stt import listen
        
        # Step 1: Ask for contact
        speak("Who should I message boss?")
        contact = listen()
        
        if not contact:
            return "Couldn't hear the contact name boss."
        
        # Step 2: Ask for message
        speak(f"What should I say to {contact} boss?")
        message = listen()
        
        if not message:
            return "Couldn't hear the message boss."
        
        # Step 3: Send message
        speak(f"Sending message to {contact} boss.")
        success, msg = send_whatsapp_message(contact, message)
        
        return msg
    
    except Exception as e:
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
