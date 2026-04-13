import subprocess
import time
import pyautogui
import pyperclip
import os
import pytesseract
import cv2
import numpy as np
from PIL import Image


# Chrome path
CHROME_PATH = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"

# Tesseract OCR path
TESSERACT_PATH = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# Gmail account credentials
PERSONAL_EMAIL = "akhilvaddeboina25@gmail.com"
COLLEGE_EMAIL = "23p61a05m5@vbithyd.ac.in"


def type_text(text):
    """
    Type text using clipboard paste (more reliable than direct typing).
    
    Args:
        text: Text to type (converted to string)
    """
    pyperclip.copy(str(text))
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.3)


def find_and_click_compose():
    """
    Find and click the Compose button using OCR.
    Optimized to scan left portion of screen first, then fallback to full screenshot.
    
    Returns:
        bool: True if compose button was found and clicked, False otherwise
    """
    try:
        # First try: Take screenshot of only LEFT portion (5x faster)
        screenshot = pyautogui.screenshot(region=(0, 100, 400, 400))
        
        # Convert to numpy array
        img_array = np.array(screenshot)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Use OCR to extract text data
        data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
        
        # Loop through detected words
        for i in range(len(data['text'])):
            word = data['text'][i].lower()
            confidence = int(data['conf'][i])
            
            if word == "compose" and confidence > 50:
                # Calculate center of detected text (adjust for region offset)
                x = data['left'][i] + data['width'][i] // 2 + 0
                y = data['top'][i] + data['height'][i] // 2 + 100
                
                # Click on the compose button
                pyautogui.click(x, y)
                time.sleep(1.5)
                return True
        
        # Fallback: Try full screenshot if not found in left portion
        screenshot = pyautogui.screenshot()
        
        # Convert to numpy array
        img_array = np.array(screenshot)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Use OCR to extract text data
        data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
        
        # Loop through detected words
        for i in range(len(data['text'])):
            word = data['text'][i].lower()
            confidence = int(data['conf'][i])
            
            if word == "compose" and confidence > 50:
                # Calculate center of detected text
                x = data['left'][i] + data['width'][i] // 2
                y = data['top'][i] + data['height'][i] // 2
                
                # Click on the compose button
                pyautogui.click(x, y)
                time.sleep(1.5)
                return True
        
        return False
    
    except Exception as e:
        print(f"Error finding compose button: {str(e)}")
        return False


def open_gmail_personal():
    """
    Open Gmail in personal Chrome profile and navigate to compose.
    
    Returns:
        bool: True if successful
    """
    try:
        # Open new tab in current Chrome window
        pyautogui.hotkey('ctrl', 't')
        time.sleep(1)
        
        # Focus address bar and navigate to Gmail
        pyautogui.hotkey('ctrl', 'l')
        time.sleep(0.3)
        pyperclip.copy("https://mail.google.com/mail/u/0/#inbox")
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press('enter')
        time.sleep(3)
        
        # Find and click compose button using OCR
        find_and_click_compose()
        
        return True
    
    except Exception as e:
        print(f"Error opening personal Gmail: {str(e)}")
        return False


def open_gmail_college():
    """
    Open Gmail in college Chrome profile and navigate to compose.
    
    Returns:
        bool: True if successful
    """
    try:
        # Open new tab in current Chrome window
        pyautogui.hotkey('ctrl', 't')
        time.sleep(1)
        
        # Focus address bar and navigate to Gmail
        pyautogui.hotkey('ctrl', 'l')
        time.sleep(0.3)
        pyperclip.copy("https://mail.google.com/mail/u/1/#inbox")
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press('enter')
        time.sleep(3)
        
        # Find and click compose button using OCR
        find_and_click_compose()
        
        return True
    
    except Exception as e:
        print(f"Error opening college Gmail: {str(e)}")
        return False


def find_and_click_text(text):
    """
    Find text on screen in compose window area and click it using OCR.
    
    Args:
        text (str): Text to find and click
    
    Returns:
        bool: True if found and clicked, False otherwise
    """
    try:
        # Take screenshot of compose window area
        screenshot = pyautogui.screenshot(region=(900, 300, 600, 300))
        
        # Convert to numpy array
        img_array = np.array(screenshot)
        
        # Convert to grayscale
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # Use OCR to extract text data
        data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
        
        # Loop through detected words
        for i in range(len(data['text'])):
            word = data['text'][i].lower()
            confidence = int(data['conf'][i])
            
            if text.lower() in word and confidence > 50:
                # Calculate center of detected text (adjust for region offset)
                x = data['left'][i] + data['width'][i] // 2 + 900
                y = data['top'][i] + data['height'][i] // 2 + 300
                
                # Click on the text
                pyautogui.click(x, y)
                time.sleep(0.5)
                return True
        
        return False
    
    except Exception as e:
        print(f"Error finding and clicking text: {str(e)}")
        return False


def fill_and_send(to_email, subject, body):
    """
    Fill Gmail compose form and send email.
    
    Args:
        to_email (str): Recipient email address
        subject (str): Email subject
        body (str): Email body text
    
    Returns:
        tuple: (success: bool, response: str)
    """
    try:
        # Wait for compose window to fully load
        time.sleep(1.5)
        
        # ===== STEP 1: Click TO field =====
        if not find_and_click_text("To"):
            # Fallback: use tab navigation
            pyautogui.hotkey('tab')
        time.sleep(0.5)
        
        # ===== STEP 2: Clear and type email =====
        pyautogui.hotkey('ctrl', 'a')
        pyautogui.press('delete')
        pyperclip.copy(to_email)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.3)
        pyautogui.press('tab')
        time.sleep(0.5)
        
        # ===== STEP 3: Type subject =====
        pyperclip.copy(subject)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.3)
        pyautogui.press('tab')
        time.sleep(0.5)
        
        # ===== STEP 4: Type body =====
        pyautogui.press('tab')
        time.sleep(0.3)
        pyperclip.copy(body)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.3)
        
        # ===== STEP 5: Send email =====
        pyautogui.hotkey('ctrl', 'enter')
        time.sleep(1)
        
        return True, "Email sent boss."
    
    except Exception as e:
        error_msg = f"Error filling form: {str(e)}"
        return False, error_msg


def send_email_personal(to_email, subject, body):
    """
    Send email from personal Gmail account.
    
    Args:
        to_email (str): Recipient email address
        subject (str): Email subject
        body (str): Email body text
    
    Returns:
        tuple: (success: bool, response: str)
    """
    try:
        open_gmail_personal()
        return fill_and_send(to_email, subject, body)
    
    except Exception as e:
        return False, f"Email failed boss: {str(e)}"


def send_email_college(to_email, subject, body):
    """
    Send email from college Gmail account.
    
    Args:
        to_email (str): Recipient email address
        subject (str): Email subject
        body (str): Email body text
    
    Returns:
        tuple: (success: bool, response: str)
    """
    try:
        open_gmail_college()
        return fill_and_send(to_email, subject, body)
    
    except Exception as e:
        return False, f"Email failed boss: {str(e)}"


