import subprocess
import os
import winreg
import getpass
import webbrowser


COMMON_APPS = {
    "whatsapp": "C:\\Program Files\\WindowsApps\\5319275A.WhatsAppDesktop_2.2613.101.0_x64__cv1g1gvanyjgm\\WhatsApp.Root.exe",
    "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "brave": "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
    "file manager": "explorer.exe",
    "file explorer": "explorer.exe",
    "explorer": "explorer.exe",
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "vs code": "C:\\Users\\akhil\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
    "vscode": "C:\\Users\\akhil\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
    "discord": "C:\\Users\\akhil\\AppData\\Local\\Discord\\Update.exe --processStart Discord.exe",
    "spotify": "C:\\Users\\akhil\\AppData\\Roaming\\Spotify\\Spotify.exe",
    "task manager": "taskmgr.exe",
    "paint": "mspaint.exe",
    "word": "winword.exe",
    "excel": "excel.exe",
    "powerpoint": "powerpnt.exe",
    "vlc": "C:\\Program Files\\VideoLAN\\VLC\\vlc.exe",
    "steam": "C:\\Program Files (x86)\\Steam\\steam.exe",
    "github desktop": "C:\\Users\\akhil\\AppData\\Local\\GitHubDesktop\\GitHubDesktop.exe",
    "notion": "C:\\Users\\akhil\\AppData\\Local\\Programs\\Notion\\Notion.exe",
    "postman": "C:\\Users\\akhil\\AppData\\Local\\Postman\\Postman.exe",
    "obs": "C:\\Program Files\\obs-studio\\bin\\64bit\\obs64.exe",
    "figma": "C:\\Users\\akhil\\AppData\\Local\\Figma\\Figma.exe",
}


def open_chrome_personal():
    """
    Open Chrome with personal profile (Default, now default profile).
    Opens new tab if Chrome is running, otherwise opens maximized window.
    
    Returns:
        bool: True if successful
    """
    try:
        CHROME = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
        
        # Check if Chrome is already running
        result = subprocess.run(["tasklist"], capture_output=True, text=True)
        
        if "chrome.exe" in result.stdout.lower():
            # Chrome is running: open new tab in existing window
            subprocess.Popen([CHROME, "--new-tab", "chrome://newtab"])
        else:
            # Chrome not running: open with default profile (Default), maximized
            subprocess.Popen([CHROME, "--start-maximized"])
        
        return True
    
    except Exception as e:
        print(f"Error opening Chrome: {e}")
        return False


def open_app(app_name):
    """
    Open an application by name with smart detection.
    Uses only subprocess.Popen - no terminal windows.
    
    Args:
        app_name (str): Name of application to open
    
    Returns:
        bool: True if app opened successfully, False otherwise
    """
    try:
        BROWSER_APPS = {
            "github": "https://github.com",
            "netflix": "https://netflix.com", 
            "instagram": "https://instagram.com",
            "twitter": "https://twitter.com",
            "linkedin": "https://linkedin.com",
            "reddit": "https://reddit.com",
            "amazon": "https://amazon.in",
            "flipkart": "https://flipkart.com",
            "perplexity": "https://perplexity.ai",
            "gemini": "https://gemini.google.com",
            "claude": "https://claude.ai",
            "chatgpt": "https://chatgpt.com"
        }
        
        # Clean app name
        app_lower = app_name.lower().strip()
        print(f"[DEBUG] Opening app: {app_lower}")
        
        # Remove filler words
        filler_words = ["the", "my", "a", "an", "app"]
        for word in filler_words:
            app_lower = app_lower.replace(f" {word} ", " ").replace(f"{word} ", "").replace(f" {word}", "")
        app_lower = app_lower.strip()
        print(f"[DEBUG] After cleanup: {app_lower}")
        
        # ===== STEP 1: Check browser apps first =====
        if app_lower in BROWSER_APPS:
            print(f"[DEBUG] Found in BROWSER_APPS: {app_lower}")
            webbrowser.open(BROWSER_APPS[app_lower])
            return True
        
        # ===== STEP 2: Check COMMON_APPS dictionary =====
        print(f"[DEBUG] Checking COMMON_APPS...")
        
        # Special handling for Chrome
        if app_lower == "chrome":
            print(f"[DEBUG] Chrome detected, calling open_chrome_personal()")
            result = open_chrome_personal()
            print(f"[DEBUG] open_chrome_personal() returned: {result}")
            return result
        
        if app_lower in COMMON_APPS:
            path = COMMON_APPS[app_lower]
            print(f"[DEBUG] Found in COMMON_APPS: {app_lower} -> {path}")
            
            # Check if it's a full path or simple executable name
            if "\\" in path:
                # Full path like "C:\\Program Files\\..."
                if os.path.exists(path):
                    print(f"[DEBUG] Full path exists, launching: {path}")
                    subprocess.Popen([path])
                    return True
                else:
                    print(f"[DEBUG] Full path NOT found: {path}")
            else:
                # Simple executable name like "explorer.exe", "calc.exe"
                print(f"[DEBUG] Simple executable name, launching: {path}")
                subprocess.Popen(path)
                return True
        
        print(f"[DEBUG] Not in COMMON_APPS")
        
        # ===== STEP 3: Search Windows registry =====
        print(f"[DEBUG] Searching registry...")
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\{app_lower}.exe")
            path = winreg.QueryValue(key, None)
            if path and os.path.exists(path):
                print(f"[DEBUG] Found in registry: {path}")
                subprocess.Popen([path])
                return True
        except Exception as e:
            print(f"[DEBUG] Registry search failed: {e}")
            pass
        
        # ===== STEP 4: Search common folders dynamically =====
        print(f"[DEBUG] Searching common folders...")
        try:
            user = getpass.getuser()
            search_dirs = [
                "C:\\Program Files",
                "C:\\Program Files (x86)",
                f"C:\\Users\\{user}\\AppData\\Local",
                f"C:\\Users\\{user}\\AppData\\Roaming",
                f"C:\\Users\\{user}\\AppData\\Local\\Microsoft\\WindowsApps"
            ]
            
            for folder in search_dirs:
                if not os.path.exists(folder):
                    continue
                
                for root, dirs, files in os.walk(folder):
                    # Skip temp/cache folders
                    dirs[:] = [d for d in dirs if d.lower() not in ["temp", "cache", "log", "logs"]]
                    
                    for file in files:
                        if file.lower() == f"{app_lower}.exe":
                            full_path = os.path.join(root, file)
                            print(f"[DEBUG] Found in folder search: {full_path}")
                            subprocess.Popen([full_path])
                            return True
        except Exception as e:
            print(f"[DEBUG] Folder search failed: {e}")
            pass
        
        print(f"[DEBUG] App not found: {app_lower}")
        # ===== STEP 5: Return False =====
        return False
    
    except Exception as e:
        print(f"[ERROR] in open_app: {e}")
        return False


def close_app(app_name):
    """
    Close an application by name.
    Handles multiple naming variations.
    
    Args:
        app_name (str): Name of app to close
        
    Returns:
        bool: True if app was closed
    """
    try:
        app_lower = app_name.lower().strip()
        
        # Map app names to process names
        process_map = {
            "whatsapp": "WhatsApp.Root.exe",
            "chrome": "chrome.exe",
            "brave": "brave.exe",
            "edge": "msedge.exe",
            "firefox": "firefox.exe",
            "spotify": "spotify.exe",
            "discord": "discord.exe",
            "vscode": "code.exe",
            "vs code": "code.exe",
            "excel": "excel.exe",
            "word": "winword.exe",
            "powerpoint": "powerpnt.exe",
            "telegram": "telegram.exe",
            "steam": "steam.exe"
        }
        
        # Get the process name
        process_name = process_map.get(app_lower, f"{app_lower}.exe")
        
        # Kill the process
        subprocess.run(["taskkill", "/f", "/im", process_name], 
                      capture_output=True, text=True, timeout=5)
        print(f"[DEBUG] Closed {app_name} ({process_name})")
        return True
    
    except Exception as e:
        print(f"[DEBUG] Error closing {app_name}: {e}")
        return False


def close_all_apps():
    """
    Close all user applications except system critical apps.
    
    Returns:
        bool: True if successful
    """
    try:
        # Apps to close
        apps_to_close = [
            "WhatsApp.Root.exe",
            "chrome.exe",
            "brave.exe",
            "firefox.exe",
            "msedge.exe",
            "discord.exe",
            "spotify.exe",
            "code.exe",
            "telegram.exe",
            "slack.exe",
            "teams.exe",
            "vlc.exe",
            "steam.exe",
            "obs64.exe"
        ]
        
        # Kill each app
        for process_name in apps_to_close:
            try:
                subprocess.run(["taskkill", "/f", "/im", process_name], 
                              capture_output=True, text=True, timeout=3)
                print(f"[DEBUG] Closed {process_name}")
            except:
                pass  # App not running, skip
        
        return True
    
    except Exception as e:
        print(f"[DEBUG] Error closing all apps: {e}")
        return False


def is_app_open(app_name):
    """Check if an application is currently open"""
    try:
        result = subprocess.run(["tasklist"], capture_output=True, text=True)
        return app_name.lower() in result.stdout.lower()
    except Exception as e:
        print(f"Error checking app status: {e}")
        return False
