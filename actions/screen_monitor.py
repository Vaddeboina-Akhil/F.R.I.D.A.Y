"""
Screen monitoring module for FRIDAY AI assistant.
Continuously monitors screen content in background using threading.
Enables responsive detection of UI changes and text appearance.
"""

import threading
import time
import pyautogui
import pytesseract
import cv2
import numpy as np
from PIL import Image
import os
import warnings
import subprocess
import sys

# ===== Suppress Warnings and Stderr =====
os.environ["PYTHONWARNINGS"] = "ignore"
warnings.filterwarnings("ignore")

# ===== Tesseract OCR Configuration =====
TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH

# ===== Global Monitoring State =====
is_monitoring = False
current_screen_text = ""
screen_lock = threading.Lock()
monitor_thread = None


def capture_and_read():
    """
    Capture screenshot and extract text using OCR with optimized settings.
    
    Process:
    1. Take screenshot with pyautogui
    2. Convert PIL Image to numpy array
    3. Convert to grayscale for better OCR
    4. Apply Otsu threshold for binary image
    5. Run pytesseract OCR with custom config
    6. Clean text (remove empty lines)
    
    Returns:
        String containing all detected text from screen
    """
    try:
        # STEP 1: Take screenshot
        screenshot = pyautogui.screenshot()
        
        # STEP 2: Convert PIL Image to numpy array
        img_array = np.array(screenshot)
        
        # STEP 3: Convert to grayscale for better OCR
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        
        # STEP 4: Apply Otsu's threshold for binary image
        _, thresholded = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # STEP 5: Run pytesseract OCR with optimized custom config
        # OEM 3 = use both legacy and LSTM models
        # PSM 6 = block text (best for screen monitoring)
        # Whitelist restricts to printable characters for better accuracy
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 !@#$%&*()-_+=[]{}|;:,.<>?/'
        text = pytesseract.image_to_string(thresholded, config=custom_config)
        
        # STEP 6: Clean text - remove empty lines and strip whitespace
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        cleaned_text = '\n'.join(lines)
        
        return cleaned_text
    
    except Exception:
        # Silently fail - no error messages from OCR
        return ""


def monitor_loop(interval=2):
    """
    Continuous monitoring loop that runs in background thread.
    
    Periodically captures screen and updates current_screen_text.
    Runs while is_monitoring is True.
    
    Args:
        interval: Time in seconds between screen captures (default 2)
    """
    global current_screen_text, is_monitoring
    
    while is_monitoring:
        try:
            # Capture and read screen
            text = capture_and_read()
            
            # Update global variable with thread safety
            with screen_lock:
                current_screen_text = text
        
        except Exception:
            # Silently continue on error
            pass
        
        # Wait before next capture
        time.sleep(interval)


def start_monitoring(interval=2):
    """
    Start continuous background screen monitoring.
    
    Launches a daemon thread that periodically captures and analyzes screen content.
    Safe to call multiple times - will not start if already monitoring.
    
    Args:
        interval: Time in seconds between screen captures (default 2)
    """
    global is_monitoring, monitor_thread
    
    # Don't start if already monitoring
    if is_monitoring:
        print("Screen monitoring is already running.")
        return
    
    # Start monitoring
    is_monitoring = True
    monitor_thread = threading.Thread(
        target=monitor_loop,
        args=(interval,),
        daemon=True
    )
    monitor_thread.start()
    print("Screen monitoring started.")


def stop_monitoring():
    """
    Stop continuous background screen monitoring.
    
    Sets is_monitoring flag to False, allowing monitor_loop to exit.
    The background thread will terminate gracefully.
    """
    global is_monitoring
    
    is_monitoring = False
    print("Screen monitoring stopped.")


def get_current_screen():
    """
    Get the most recently captured screen text.
    
    Thread-safe access to current_screen_text.
    
    Returns:
        String containing detected text from last screen capture
    """
    with screen_lock:
        return current_screen_text


def is_text_on_screen(search_text):
    """
    Check if specific text appears on current screen.
    
    Performs case-insensitive substring matching against
    the most recently captured screen content.
    
    Args:
        search_text: Text to search for
        
    Returns:
        True if text found on screen, False otherwise
        
    Example:
        if is_text_on_screen("Submit"):
            print("Submit button visible")
    """
    text = get_current_screen()
    return search_text.lower() in text.lower()


def wait_for_text(search_text, timeout=10):
    """
    Wait for specific text to appear on screen.
    
    Polls screen content until text is found or timeout expires.
    Useful for waiting for UI elements to load or responses to appear.
    
    Args:
        search_text: Text to wait for
        timeout: Maximum time in seconds to wait (default 10)
        
    Returns:
        True if text was found within timeout, False if timed out
        
    Example:
        if wait_for_text("Loading complete", timeout=15):
            print("Page loaded successfully")
        else:
            print("Page load timed out")
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        # Check if text is on screen
        if is_text_on_screen(search_text):
            return True
        
        # Brief sleep before next check
        time.sleep(0.5)
    
    # Timeout reached without finding text
    return False
