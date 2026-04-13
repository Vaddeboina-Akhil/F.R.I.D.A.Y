import pyautogui
import pytesseract
import cv2
import numpy as np
import time
import subprocess
import os
import re
import pygetwindow as gw
from datetime import datetime, timedelta


TESSERACT_PATH = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH


def focus_window(window_title):
    """Focus a window by clicking on it."""
    try:
        # Try using pygetwindow
        windows = gw.getWindowsWithTitle(window_title)
        if windows:
            try:
                windows[0].activate()
                time.sleep(0.5)
                return True
            except:
                # If activate fails, try clicking on the window instead
                try:
                    x, y = windows[0].center
                    pyautogui.click(int(x), int(y))
                    time.sleep(0.5)
                    return True
                except:
                    pass
        
        # Fallback: just click in the middle of the screen (Clock app opens centered)
        print("[DEBUG] Window not found, clicking center of screen...")
        pyautogui.click(640, 360)
        time.sleep(0.5)
        return True
    
    except Exception as e:
        print(f"Error focusing window: {str(e)}")
        # Fallback: click center
        try:
            pyautogui.click(640, 360)
            time.sleep(0.5)
            return True
        except:
            return False


def open_clock():
    """
    Open Windows Clock app and make it fullscreen.
    
    Returns:
        bool: True if successful
    """
    try:
        print("[DEBUG] Opening Windows Clock app...")
        
        # Kill any existing Clock windows first
        try:
            subprocess.run(['taskkill', '/IM', 'WindowsAlarms.exe', '/F'], capture_output=True, stderr=subprocess.DEVNULL)
            time.sleep(1)
        except:
            pass
        
        # Open Clock app fresh
        print("[DEBUG] Launching Clock app with ms-clock: URI...")
        os.system("start ms-clock:")
        time.sleep(4)
        
        # Focus the Clock window
        print("[DEBUG] Focusing Clock app...")
        focus_window("Clock")
        time.sleep(1)
        
        # Make it fullscreen - use Alt+F10 to maximize
        print("[DEBUG] Making Clock app fullscreen...")
        pyautogui.hotkey('alt', 'f10')  # Maximize window
        time.sleep(2)
        
        # Also try to click maximize button as backup
        pyautogui.click(1497, 19)  # Maximize button on title bar
        time.sleep(2)
        
        # Wait for fullscreen animations to complete
        time.sleep(1)
        
        print("[DEBUG] Clock app opened and fullscreen!")
        return True
    
    except Exception as e:
        print(f"[ERROR] Error opening Clock: {str(e)}")
        return False


def click_timer_tab():
    """
    Click the Timer tab in the Clock app sidebar.
    Timer tab is the 2nd item in the left sidebar.
    """
    try:
        print("[DEBUG] Clicking Timer tab...")
        # Timer is the 2nd menu item, below Focus sessions
        # Y coordinate around 100 is the Timer option
        pyautogui.click(67, 100)
        time.sleep(1.5)
        print("[DEBUG] Timer tab clicked!")
        return True
    except Exception as e:
        print(f"[ERROR] Error clicking Timer tab: {str(e)}")
        return False


def is_clock_loaded():
    """
    Check if Clock app is loaded using OCR.
    
    Returns:
        bool: True if Clock UI is loaded
    """
    try:
        screenshot = pyautogui.screenshot()
        img_array = np.array(screenshot)
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
        
        for i in range(len(data['text'])):
            word = data['text'][i].lower()
            if "alarm" in word or "timer" in word or "clock" in word:
                print(f"[DEBUG] Clock loaded! Detected: '{word}'")
                return True
        
        return False
    except Exception as e:
        print(f"Error checking Clock load status: {str(e)}")
        return False


def wait_for_clock_load(max_wait=5):
    """
    Wait for Clock app to load.
    
    Args:
        max_wait (int): Maximum seconds to wait
    
    Returns:
        bool: True if Clock loaded, False if timeout
    """
    print(f"[DEBUG] Waiting for Clock to load (max {max_wait} seconds)...")
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        if is_clock_loaded():
            elapsed = time.time() - start_time
            print(f"[DEBUG] Clock loaded in {elapsed:.1f} seconds")
            return True
        time.sleep(0.3)
    
    print(f"[DEBUG] Clock did not load after {max_wait} seconds")
    return False


def set_timer(duration_str):
    """
    Set a timer using Windows Clock app.
    Duration format: "5 minutes", "30 seconds", "1 hour", etc.
    
    Args:
        duration_str (str): Timer duration (e.g., "5 minutes", "30 seconds")
    
    Returns:
        tuple: (success: bool, response: str)
    """
    try:
        # Parse duration
        match = re.search(r'(\d+)\s*(minute|second|hour|min|sec|hr)?', duration_str.lower())
        if not match:
            return False, "Couldn't understand the timer duration boss."
        
        duration = int(match.group(1))
        unit = match.group(2) or "minute"
        
        # Normalize unit
        if unit in ["minute", "min"]:
            display = f"{duration} minute{'s' if duration > 1 else ''}"
            # Pre-built timers in Clock app: 5, 10, 1, 2, 30
            button_targets = {1: "1 min", 2: "2 min", 5: "5 min", 10: "10 min", 30: "30 min"}
        elif unit in ["second", "sec"]:
            display = f"{duration} second{'s' if duration > 1 else ''}"
            button_targets = {}
        elif unit in ["hour", "hr"]:
            display = f"{duration} hour{'s' if duration > 1 else ''}"
            button_targets = {}
        else:
            return False, "Invalid timer unit boss."
        
        # Open Clock app and ensure it's focused
        print("[DEBUG] Opening and focusing Clock app...")
        if not open_clock():
            return False, "Couldn't open Clock app boss. Is it installed on your system?"
        
        # Wait for app to fully load
        time.sleep(1)
        
        # Ensure window is focused
        print("[DEBUG] Clicking to focus Clock app...")
        focus_window("Clock")
        time.sleep(0.5)
        
        # If duration matches a preset timer, click its play button
        if duration in button_targets:
            print(f"[DEBUG] Clicking play button for {display}...")
            
            # Wait longer for Clock app to fully render and become responsive
            time.sleep(3)
            
            # Play button coordinates for pre-built timers in Clock app (USER VERIFIED)
            # Row 1: 1min(626,4178)  2min(1110,4188)  5min(1589,4228)
            # Row 2: 10min(625,8394) 15min(1106,8428) 30min(1586,8398)
            timer_play_buttons = {
                1: (626, 419),     # 1 min - top-left
                2: (1106, 418),    # 2 min - top-middle
                5: (1591, 417),    # 5 min - top-right
                10: (626, 842),    # 10 min - bottom-left
                15: (1106, 842),   # 15 min - bottom-middle
                30: (1591, 842),   # 30 min - bottom-right
            }
            
            if duration in timer_play_buttons:
                x, y = timer_play_buttons[duration]
                print(f"[DEBUG] Play button coordinates for {duration}min: ({x}, {y})")
                
                # Move mouse to button location first (helps with event generation)
                print(f"[DEBUG] Moving mouse to play button...")
                pyautogui.moveTo(x, y, duration=0.3)
                
                # Add delay before clicking
                time.sleep(0.3)
                
                # Perform left mouse click
                print(f"[DEBUG] Clicking play button at ({x}, {y})...")
                pyautogui.click(x, y)
                
                # Give window time to process the click
                time.sleep(0.5)
                print(f"[DEBUG] Play button clicked!")
                time.sleep(1)
                
                return True, f"Timer set for {display} boss. Clock app is keeping track!"
        
        # Fallback: just keep the app open
        print(f"[DEBUG] Timer duration not in pre-built timers, keeping Clock app open...")
        
        return True, f"Clock app is open boss. Set timer to {display} manually!"
    
    except Exception as e:
        print(f"[ERROR] Timer error: {str(e)}")
        return False, f"Failed to set timer boss: {str(e)}"


def set_alarm(alarm_time_str):
    """
    Set an alarm using Windows Clock app.
    Time format: "7 AM", "14:30", "2:30 PM", etc.
    
    Args:
        alarm_time_str (str): Alarm time (e.g., "7 AM", "14:30")
    
    Returns:
        tuple: (success: bool, response: str)
    """
    try:
        # Parse time
        # Handle formats: "7 AM", "7:30 AM", "14:30", "2:30 PM"
        time_match = re.search(r'(\d{1,2}):?(\d{0,2})\s*(am|pm)?', alarm_time_str.lower())
        if not time_match:
            return False, "Couldn't understand the alarm time boss."
        
        hour = int(time_match.group(1))
        minute = int(time_match.group(2)) if time_match.group(2) else 0
        meridiem = time_match.group(3)  # am/pm
        
        # Convert to 24-hour format
        if meridiem:
            if meridiem == "pm" and hour != 12:
                hour += 12
            elif meridiem == "am" and hour == 12:
                hour = 0
        
        alarm_display = f"{hour:02d}:{minute:02d}"
        
        # Open Clock app
        open_clock()
        
        # Wait for Clock to load
        if not wait_for_clock_load():
            return False, "Clock app took too long to load boss."
        
        # Click on Alarm tab
        print("[DEBUG] Clicking Alarm tab...")
        pyautogui.click(1100, 100)  # Adjust coordinates as needed
        time.sleep(1)
        
        # Click "Add alarm" or "+" button
        print("[DEBUG] Adding new alarm...")
        pyautogui.click(1300, 150)  # Adjust to actual Add button location
        time.sleep(1)
        
        # Enter alarm time
        print(f"[DEBUG] Setting alarm for {alarm_display}...")
        pyautogui.typewrite(f"{hour:02d}{minute:02d}")
        time.sleep(0.5)
        
        # Click Save/OK button
        pyautogui.click(1100, 600)  # Adjust to actual Save button location
        time.sleep(1)
        
        return True, f"Alarm set for {alarm_display} boss."
    
    except Exception as e:
        print(f"[ERROR] Alarm error: {str(e)}")
        return False, f"Failed to set alarm boss: {str(e)}"


def close_clock():
    """
    Close Windows Clock app.
    
    Returns:
        bool: True if successful
    """
    try:
        print("[DEBUG] Closing Clock app...")
        os.system("taskkill /IM WindowsAlarms.exe /F")
        return True
    except Exception as e:
        print(f"Error closing Clock: {str(e)}")
        return False
