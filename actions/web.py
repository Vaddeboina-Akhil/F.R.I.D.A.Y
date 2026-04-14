import webbrowser
import subprocess
import os

WORLD_MONITOR_URL = "https://www.worldmonitor.app/?lat=20.0000&lon=0.0000&zoom=1.57&view=mena&timeRange=7d&layers=conflicts,hotspots,sanctions,weather,outages,natural,iranAttacks"

# Brave browser path on Windows
BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

# Chrome browser path on Windows
CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

# Flag to track if Brave registration was attempted
_brave_registered = False


def _register_brave_browser():
    """
    Register Brave browser as a webbrowser controller.
    This allows webbrowser.get() to use Brave for opening URLs.
    Only attempts registration once.
    """
    global _brave_registered
    
    if _brave_registered:
        return True
    
    try:
        if os.path.exists(BRAVE_PATH):
            # Register Brave as a new browser controller
            webbrowser.register('brave', None, webbrowser.BackgroundBrowser(BRAVE_PATH))
            _brave_registered = True
            return True
        else:
            print(f"Brave not found at {BRAVE_PATH}")
            _brave_registered = False
            return False
    except Exception as e:
        print(f"Error registering Brave browser: {e}")
        _brave_registered = False
        return False


def open_url(url):
    """
    Open a URL in the appropriate browser.
    
    Special handling:
    - YouTube → Opens in Brave browser directly via subprocess
    - Other URLs → Opens in default browser
    
    Args:
        url: The URL to open (can be full URL or domain like "youtube", "gmail")
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Normalize target to full URL
        if url == "youtube":
            url = "https://www.youtube.com"
        elif url == "gmail":
            url = "https://www.gmail.com"
        elif url == "google":
            url = "https://www.google.com"
        elif url == "chatgpt":
            url = "https://chatgpt.com"
        elif url == "claude":
            url = "https://claude.ai"
        elif not url.startswith("http"):
            # Add https if not present
            url = f"https://{url}"
        
        # YouTube special handling: Use Brave browser directly
        if "youtube" in url.lower():
            if os.path.exists(BRAVE_PATH):
                subprocess.Popen([BRAVE_PATH, url])
                return True
            else:
                print(f"Brave browser not found at {BRAVE_PATH}")
                webbrowser.open(url)
                return True
        else:
            # For other websites, use default browser
            webbrowser.open(url)
            return True
        
    except Exception as e:
        print(f"Error opening URL: {e}")
        return False


def search_google(query):
    """Search Google for a query"""
    try:
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        webbrowser.open(url)
        return True
    except Exception as e:
        print(f"Error searching Google: {e}")
        return False


def search_youtube(query):
    """
    Search YouTube for a query.
    Uses Brave browser directly via subprocess.
    
    Args:
        query: Search query string
        
    Returns:
        True if successful, False otherwise
    """
    try:
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        
        # Open YouTube search in Brave browser directly
        if os.path.exists(BRAVE_PATH):
            subprocess.Popen([BRAVE_PATH, url])
            return True
        else:
            print(f"Brave browser not found at {BRAVE_PATH}")
            webbrowser.open(url)
            return True
        
    except Exception as e:
        print(f"Error searching YouTube: {e}")
        return False


def open_world_monitor():
    """Open the World Monitor dashboard - checks if already open first"""
    try:
        # Check if world monitor is already open
        result = subprocess.run(["tasklist", "/v"], capture_output=True, text=True)
        if "worldmonitor" in result.stdout.lower() or "world" in result.stdout.lower():
            return False  # Already open, don't open again
        
        # Not open, so open it
        webbrowser.open(WORLD_MONITOR_URL)
        return True
    except Exception as e:
        print(f"Error opening World Monitor: {e}")
        return False


def open_claude():
    """Open Claude AI"""
    try:
        webbrowser.open("https://claude.ai")
        return True
    except Exception as e:
        print(f"Error opening Claude: {e}")
        return False


def open_chatgpt():
    """Open ChatGPT"""
    try:
        webbrowser.open("https://chatgpt.com")
        return True
    except Exception as e:
        print(f"Error opening ChatGPT: {e}")
        return False


def open_and_search(target):
    """
    Open a browser and search for a query on YouTube.
    
    Parses target in format "app_name|query" and opens the appropriate
    browser (Brave or Chrome) with YouTube search results.
    
    Args:
        target: Target string in format "app_name|query"
               (e.g., "brave|python tutorial", "chrome|mrbeast videos")
        
    Returns:
        String describing the action taken
        
    Examples:
        open_and_search("brave|python tutorial")
        open_and_search("chrome|mrbeast")
        open_and_search("|gaming") - defaults to brave
    """
    try:
        # STEP 1: Split target by pipe separator
        parts = target.split("|")
        app_name = parts[0].strip().lower() if len(parts) > 0 else "brave"
        query = parts[1].strip() if len(parts) > 1 else ""
        
        # Default to brave if app_name is empty
        if not app_name:
            app_name = "brave"
        
        # STEP 2: Build YouTube search URL
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        
        # STEP 3: Route to appropriate browser
        if "brave" in app_name:
            subprocess.Popen([BRAVE_PATH, url])
        elif "chrome" in app_name:
            subprocess.Popen([CHROME_PATH, url])
        else:
            # Default to Brave for unknown browsers
            subprocess.Popen([BRAVE_PATH, url])
        
        return f"Opening browser and searching for {query} boss."
    
    except Exception as e:
        print(f"Error in open_and_search: {e}")
        return f"Error performing search: {str(e)}"
