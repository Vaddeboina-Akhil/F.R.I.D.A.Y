import subprocess
import os
import winreg


COMMON_APPS = {
    "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "vs code": "C:\\Users\\akhil\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
    "vscode": "C:\\Users\\akhil\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe",
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "file explorer": "explorer.exe",
    "explorer": "explorer.exe",
    "whatsapp": "C:\\Users\\akhil\\AppData\\Local\\WhatsApp\\WhatsApp.exe",
    "brave": "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe",
    "spotify": "C:\\Users\\akhil\\AppData\\Roaming\\Spotify\\Spotify.exe",
    "discord": "C:\\Users\\akhil\\AppData\\Local\\Discord\\app-1.0.9005\\Discord.exe",
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


def open_app(app_name):
    """Open an application by name with smart dynamic detection"""
    try:
        import webbrowser
        
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
        
        app_lower = app_name.lower().strip()
        
        # Browser apps - open URLs directly
        if app_lower in BROWSER_APPS:
            webbrowser.open(BROWSER_APPS[app_lower])
            return True
        
        # Step 1: Check COMMON_APPS dictionary as quick lookup cache
        if app_lower in COMMON_APPS:
            path = COMMON_APPS[app_lower]
            if os.path.exists(path):
                subprocess.Popen(path)
                return True
        
        # Step 2: Search Windows registry
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                f"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\App Paths\\{app_lower}.exe")
            path = winreg.QueryValue(key, None)
            if path and os.path.exists(path):
                subprocess.Popen(path)
                return True
        except:
            pass
        
        # Step 3: Search common folders dynamically with os.walk
        try:
            search_dirs = [
                "C:\\Program Files",
                "C:\\Program Files (x86)",
                f"C:\\Users\\{os.getlogin()}\\AppData\\Local",
                f"C:\\Users\\{os.getlogin()}\\AppData\\Roaming"
            ]
            
            for folder in search_dirs:
                if not os.path.exists(folder):
                    continue
                
                for root, dirs, files in os.walk(folder):
                    # Skip temp directories
                    dirs[:] = [d for d in dirs if d.lower() != "temp"]
                    
                    for file in files:
                        if file.lower() == f"{app_lower}.exe":
                            full_path = os.path.join(root, file)
                            subprocess.Popen(full_path)
                            return True
        except:
            pass
        
        # Step 4: Try Windows shell as last resort
        try:
            os.system(f"start {app_lower}")
            return True
        except:
            pass
        
        return False
    
    except Exception as e:
        print(f"Error opening app: {e}")
        return False


def close_app(app_name):
    """Close an application by name"""
    try:
        subprocess.run(["taskkill", "/f", "/im", f"{app_name}.exe"])
        return True
    except Exception as e:
        print(f"Error closing app: {e}")
        return False


def is_app_open(app_name):
    """Check if an application is currently open"""
    try:
        result = subprocess.run(["tasklist"], capture_output=True, text=True)
        return app_name.lower() in result.stdout.lower()
    except Exception as e:
        print(f"Error checking app status: {e}")
        return False
