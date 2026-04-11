import subprocess
import os
import datetime
import platform
import pyautogui
import cv2
import pytesseract
import numpy as np
import time


def get_time():
    """Get current time"""
    try:
        now = datetime.datetime.now()
        hour = now.hour
        minute = now.minute
        am_pm = "AM" if hour < 12 else "PM"
        hour_12 = hour if hour <= 12 else hour - 12
        if hour_12 == 0:
            hour_12 = 12
        return f"It's {hour_12}:{minute:02d} {am_pm}"
    except Exception as e:
        print(f"Error getting time: {e}")
        return "I couldn't get the time."


def get_date():
    """Get current date"""
    try:
        now = datetime.datetime.now()
        weekday = now.strftime("%A")
        day = now.day
        month = now.strftime("%B")
        year = now.year
        return f"Today is {weekday}, {day} {month} {year}"
    except Exception as e:
        print(f"Error getting date: {e}")
        return "I couldn't get the date."


def shutdown_pc():
    """Shutdown the PC in 30 seconds"""
    try:
        subprocess.run(["shutdown", "/s", "/t", "30"])
        return "Shutting down in 30 seconds boss."
    except Exception as e:
        print(f"Error initiating shutdown: {e}")
        return "I couldn't shutdown the PC."


def restart_pc():
    """Restart the PC in 30 seconds"""
    try:
        subprocess.run(["shutdown", "/r", "/t", "30"])
        return "Restarting in 30 seconds boss."
    except Exception as e:
        print(f"Error initiating restart: {e}")
        return "I couldn't restart the PC."


def cancel_shutdown():
    """Cancel scheduled shutdown"""
    try:
        subprocess.run(["shutdown", "/a"])
        return "Shutdown cancelled boss."
    except Exception as e:
        print(f"Error cancelling shutdown: {e}")
        return "No shutdown to cancel."


def get_battery():
    """Get battery percentage"""
    try:
        import psutil
        battery = psutil.sensors_battery()
        if battery:
            percent = int(battery.percent)
            return f"Battery is at {percent}%"
        else:
            return "Battery info not available"
    except Exception as e:
        print(f"Error getting battery: {e}")
        return "Battery info not available"


def take_screenshot():
    """Take a screenshot and save it to memory and Windows Screenshots folder"""
    try:
        screenshot = pyautogui.screenshot()
        
        # Create memory directory if it doesn't exist
        os.makedirs("memory", exist_ok=True)
        
        # Save to memory folder
        screenshot.save("memory/screenshot.png")
        
        # Save to Windows Screenshots folder with timestamp
        try:
            screenshots_folder = os.path.join(os.path.expanduser("~"), "Pictures", "Screenshots")
            os.makedirs(screenshots_folder, exist_ok=True)
            filename = f"FRIDAY_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            full_path = os.path.join(screenshots_folder, filename)
            screenshot.save(full_path)
        except Exception as e:
            print(f"Warning: Could not save to Pictures/Screenshots: {e}")
        
        return "Screenshot taken and saved to Pictures boss."
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        return "I couldn't take a screenshot."


def find_text_on_screen(target_text):
    """
    Find specific text on screen using OCR and return its center coordinates.
    
    Uses pytesseract (Tesseract OCR engine) to detect all text on screen,
    then searches for the target text and returns pixel coordinates.
    
    Args:
        target_text: Text to search for (e.g., "Submit", "Username", "Login")
        
    Returns:
        Tuple (center_x, center_y) if found, None if not found
        
    Raises:
        ImportError: If pytesseract or tesseract-ocr is not installed
        
    Example:
        coords = find_text_on_screen("Submit")
        if coords:
            x, y = coords
            pyautogui.click(x, y)  # Click on the Submit button
        else:
            print("Text not found on screen")
    """
    try:
        # STEP 1: Capture screenshot into memory (PIL Image)
        # This avoids writing to disk and is faster than loading from file
        screenshot = pyautogui.screenshot()
        
        # STEP 2: Convert PIL Image to numpy array for cv2 processing
        # cv2 works with numpy arrays, not PIL Images
        img_array = np.array(screenshot)
        
        # STEP 3: Convert BGR (OpenCV color space) to RGB
        # pyautogui.screenshot() returns RGB, cv2 expects BGR
        img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # STEP 4: Convert to grayscale for better OCR accuracy
        # Grayscale simplifies the image and improves text detection
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        
        # STEP 5: Use pytesseract.image_to_data() to detect all text with coordinates
        # Returns detailed info: x, y, width, height for each detected word
        data = pytesseract.image_to_data(gray)
        
        # STEP 6: Parse OCR results and search for target text
        # image_to_data returns tab-separated values with headers
        lines = data.split('\n')
        
        for line in lines[1:]:  # Skip header line
            if not line.strip():
                continue
                
            parts = line.split('\t')
            if len(parts) < 12:  # Ensure we have all required fields
                continue
            
            # Extract coordinates from OCR result
            x = int(parts[1])           # Left position
            y = int(parts[2])           # Top position
            w = int(parts[3])           # Width
            h = int(parts[4])           # Height
            detected_text = parts[11]   # Text content (0-indexed)
            
            # STEP 7: Check if target text matches (case-insensitive)
            # Use .lower() for case-insensitive matching
            if target_text.lower() in detected_text.lower():
                # STEP 8: Calculate center coordinates
                # Center point is useful for clicking on buttons/text
                center_x = x + (w // 2)
                center_y = y + (h // 2)
                
                print(f"Found '{detected_text}' at ({center_x}, {center_y})")
                return (center_x, center_y)
        
        # STEP 9: Return None if text not found on screen
        print(f"Text '{target_text}' not found on screen")
        return None
        
    except ImportError as e:
        print(f"Error: pytesseract or tesseract-ocr not installed: {e}")
        print("Install with: pip install pytesseract")
        print("Also install tesseract-ocr from: https://github.com/UB-Mannheim/tesseract/wiki")
        return None
    except Exception as e:
        print(f"Error finding text on screen: {e}")
        return None


def click_text(target_text):
    """
    Find text on screen and click on it using OCR.
    
    This function combines OCR detection with automated clicking to interact
    with UI elements based on visible text. Useful for clicking buttons,
    links, or form fields when their positions are not hardcoded.
    
    Args:
        target_text: Text to find and click on (e.g., "Submit", "Login", "Next")
        
    Returns:
        String message indicating success or failure
        
    Safety Features:
        - 0.5 second delay before clicking (prevents accidental rapid clicks)
        - Returns feedback message for logging and debugging
        - Graceful error handling for missing text or OCR failures
        
    Example:
        result = click_text("Submit")
        # Returns: "Clicked on Submit" or "Couldn't find Submit on screen"
    """
    try:
        # SAFETY 1: Find text before clicking to ensure it exists
        # This prevents accidental clicks at wrong coordinates
        position = find_text_on_screen(target_text)
        
        if position:
            x, y = position
            
            # SAFETY 2: Small delay before clicking
            # 0.5 seconds gives the system time to stabilize after screen change
            # Also prevents rapid accidental double-clicks
            time.sleep(0.5)
            
            # SAFETY 3: Use pyautogui.click() with centered coordinates
            # Click is sent to the center of the text element (calculated in find_text_on_screen)
            pyautogui.click(x, y)
            
            return f"Clicked on {target_text}"
        else:
            # Text not found on screen
            return f"Couldn't find {target_text} on screen"
            
    except Exception as e:
        print(f"Error clicking text: {e}")
        return f"Error trying to click {target_text}: {str(e)}"
