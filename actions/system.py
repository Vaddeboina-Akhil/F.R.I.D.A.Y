import subprocess
import os
import datetime
import platform
import pyautogui
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
