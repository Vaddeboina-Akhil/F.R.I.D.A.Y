"""
Screen interaction module for FRIDAY AI assistant.
Handles OCR-based text detection, automated clicking, scrolling, and typing.
Uses Tesseract OCR for accurate text recognition and PyAutoGUI for automation.
"""

import pyautogui
import pytesseract
import cv2
import numpy as np
from PIL import Image
import time
import os
import pyperclip
import pygetwindow

# ===== Tesseract OCR Configuration =====
# Path to Tesseract executable on Windows
# This is REQUIRED for pytesseract to work
# Install from: https://github.com/UB-Mannheim/tesseract/wiki
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


def take_screenshot():
    """
    Capture screenshot and save to disk while returning PIL Image.
    
    Returns:
        PIL.Image object of the screenshot
    """
    try:
        # Create memory directory if needed
        os.makedirs("memory", exist_ok=True)
        
        # Capture screenshot
        screenshot = pyautogui.screenshot()
        
        # Save to disk
        screenshot.save("memory/screenshot.png")
        
        return screenshot
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        return None


def get_screen_text():
    """
    Extract all text from current screen using OCR.
    
    Uses thresholding to improve OCR accuracy on the screenshot.
    Returns cleaned text with whitespace normalized.
    
    Returns:
        String containing all detected text from screen
    """
    try:
        # STEP 1: Take screenshot
        screenshot = take_screenshot()
        if screenshot is None:
            return ""
        
        # STEP 2: Convert PIL Image to numpy array
        img_array = np.array(screenshot)
        
        # STEP 3: Convert to grayscale for better OCR
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # STEP 4: Apply Otsu's threshold for binary image
        # This improves OCR accuracy by creating clear black text on white background
        _, thresholded = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # STEP 5: Run OCR on thresholded image
        text = pytesseract.image_to_string(thresholded)
        
        # STEP 6: Clean up text - remove extra whitespace and empty lines
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        cleaned_text = '\n'.join(lines)
        
        return cleaned_text
    
    except Exception as e:
        print(f"Error getting screen text: {e}")
        return ""


def find_text_on_screen(search_text):
    """
    Find specific text on screen using OCR and return its center coordinates.
    
    Uses pytesseract.image_to_data() with confidence filtering to accurately
    locate the position of text on screen.
    
    Args:
        search_text: Text to search for (case-insensitive)
        
    Returns:
        Tuple (center_x, center_y) if found, None if not found
        
    Example:
        coords = find_text_on_screen("Submit")
        if coords:
            click_text("Submit")
    """
    try:
        # STEP 1: Take screenshot
        screenshot = take_screenshot()
        if screenshot is None:
            return None
        
        # STEP 2: Convert PIL Image to numpy array
        img_array = np.array(screenshot)
        
        # STEP 3: Convert to grayscale
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # STEP 4: Apply threshold for consistency
        _, thresholded = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # STEP 5: Use pytesseract.image_to_data() with DICT output format
        # This returns coordinates for each detected word
        data = pytesseract.image_to_data(thresholded, output_type=pytesseract.Output.DICT)
        
        # STEP 6: Loop through detected words and search for match
        for i in range(len(data['text'])):
            detected_word = data['text'][i].strip()
            confidence = int(data['conf'][i])
            
            # Skip empty words and low-confidence detections
            if not detected_word or confidence < 60:
                continue
            
            # STEP 7: Case-insensitive matching
            if search_text.lower() in detected_word.lower():
                # STEP 8: Calculate center coordinates of bounding box
                left = data['left'][i]
                top = data['top'][i]
                width = data['width'][i]
                height = data['height'][i]
                
                center_x = left + (width // 2)
                center_y = top + (height // 2)
                
                print(f"Found '{detected_word}' at ({center_x}, {center_y}) with confidence {confidence}%")
                return (center_x, center_y)
        
        # STEP 9: Not found
        print(f"Text '{search_text}' not found on screen")
        return None
    
    except Exception as e:
        print(f"Error finding text on screen: {e}")
        return None


def click_text(search_text):
    """
    Find text on screen and click on it using OCR detection.
    
    Uses smooth mouse movement and proper timing for reliable interaction.
    Includes safety delays to prevent accidental double-clicks.
    
    Args:
        search_text: Text to find and click
        
    Returns:
        Tuple (success: bool, message: str)
        
    Example:
        success, message = click_text("Submit")
        if success:
            print(f"Clicked successfully: {message}")
        else:
            print(f"Click failed: {message}")
    """
    try:
        # STEP 1: Find text coordinates
        coords = find_text_on_screen(search_text)
        
        if coords is None:
            return False, f"Text '{search_text}' not found on screen"
        
        x, y = coords
        
        # STEP 2: Move mouse to coordinates with smooth animation
        # duration=0.3 creates smooth 0.3-second movement
        pyautogui.moveTo(x, y, duration=0.3)
        
        # STEP 3: Wait for movement to complete
        time.sleep(0.2)
        
        # STEP 4: Click
        pyautogui.click()
        
        # STEP 5: Wait after click to let UI respond
        time.sleep(0.5)
        
        return True, f"Clicked '{search_text}' at ({x}, {y})"
    
    except Exception as e:
        print(f"Error clicking text: {e}")
        return False, f"Error clicking text: {str(e)}"


def read_screen_area(x, y, width, height):
    """
    Extract text from a specific region of the screen using OCR.
    
    Useful for reading text in specific UI areas like input fields,
    message boxes, or document regions.
    
    Args:
        x: Left coordinate of region
        y: Top coordinate of region
        width: Width of region in pixels
        height: Height of region in pixels
        
    Returns:
        String of detected text from the region
        
    Example:
        text = read_screen_area(100, 100, 400, 200)
        print(f"Text in region: {text}")
    """
    try:
        # STEP 1: Capture specific region
        # region=(x, y, width, height) captures rectangle starting at (x,y)
        region_screenshot = pyautogui.screenshot(region=(x, y, width, height))
        
        # STEP 2: Convert to numpy array
        img_array = np.array(region_screenshot)
        
        # STEP 3: Convert to grayscale
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # STEP 4: Apply threshold
        _, thresholded = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # STEP 5: Run OCR
        text = pytesseract.image_to_string(thresholded)
        
        # STEP 6: Clean and return
        cleaned_text = ' '.join(text.split())
        return cleaned_text
    
    except Exception as e:
        print(f"Error reading screen area: {e}")
        return ""


def scroll_down(amount=3):
    """
    Scroll down on screen.
    
    Args:
        amount: Number of scroll increments (default 3)
        
    Returns:
        True if successful
    """
    try:
        # Negative value scrolls down
        # Each unit = ~100 pixels
        pyautogui.scroll(-amount * 100)
        time.sleep(0.3)
        return True
    except Exception as e:
        print(f"Error scrolling down: {e}")
        return False


def scroll_up(amount=3):
    """
    Scroll up on screen.
    
    Args:
        amount: Number of scroll increments (default 3)
        
    Returns:
        True if successful
    """
    try:
        # Positive value scrolls up
        # Each unit = ~100 pixels
        pyautogui.scroll(amount * 100)
        time.sleep(0.3)
        return True
    except Exception as e:
        print(f"Error scrolling up: {e}")
        return False


def type_text(text):
    """
    Type text with smart handling for spaces and special characters.
    
    For simple alphanumeric text: Uses typewrite() with interval.
    For text with spaces/special chars: Uses clipboard paste method.
    
    Args:
        text: String to type
        
    Returns:
        True if successful
        
    Example:
        type_text("Hello World")
        type_text("search@gmail.com")
    """
    try:
        # STEP 1: Ensure focus on current window
        time.sleep(0.5)
        pyautogui.click()  # Click to ensure focus
        time.sleep(0.3)
        
        # STEP 2: Check if text has spaces or special characters
        if ' ' in text or any(char in text for char in '!@#$%^&*()-_=+[]{}|;:,.<>?'):
            # STEP 3a: Text with spaces/special chars - use clipboard paste
            pyperclip.copy(text)
            pyautogui.hotkey('ctrl', 'v')
        else:
            # STEP 3b: Simple alphanumeric - use typewrite
            pyautogui.typewrite(text, interval=0.08)
        
        time.sleep(0.3)
        return True
    except Exception as e:
        print(f"Error typing text: {e}")
        return False


def press_key(key):
    """
    Press a single keyboard key.
    
    Args:
        key: Key name as string (e.g., 'enter', 'tab', 'esc', 'backspace')
        
    Returns:
        True if successful
        
    Example:
        press_key('enter')    # Press Enter key
        press_key('tab')      # Press Tab key
        press_key('esc')      # Press Escape key
        press_key('backspace')  # Press Backspace key
    """
    try:
        pyautogui.press(key)
        time.sleep(0.2)
        return True
    except Exception as e:
        print(f"Error pressing key '{key}': {e}")
        return False
