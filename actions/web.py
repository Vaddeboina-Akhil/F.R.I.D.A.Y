import webbrowser
import subprocess
import os

WORLD_MONITOR_URL = "https://www.worldmonitor.app/?lat=20.0000&lon=0.0000&zoom=1.57&view=mena&timeRange=7d&layers=conflicts,hotspots,sanctions,weather,outages,natural,iranAttacks"

# Brave browser path on Windows
BRAVE_PATH = r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"

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
    - YouTube → Opens in Brave browser (if available, otherwise default)
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
        
        # YouTube special handling: Use Brave browser
        if "youtube" in url.lower():
            if _register_brave_browser():
                # Try to use Brave browser
                try:
                    brave = webbrowser.get('brave')
                    brave.open(url)
                    return True
                except Exception as e:
                    print(f"Error opening with Brave: {e}. Falling back to default browser.")
                    # Fallback to default browser if Brave fails
                    webbrowser.open(url)
                    return True
            else:
                # Brave not available, use default browser
                print("Brave browser not available. Using default browser for YouTube.")
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
    Uses Brave browser for YouTube searches (if available).
    
    Args:
        query: Search query string
        
    Returns:
        True if successful, False otherwise
    """
    try:
        url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"
        
        # YouTube is special - use Brave browser
        if _register_brave_browser():
            try:
                brave = webbrowser.get('brave')
                brave.open(url)
                return True
            except Exception as e:
                print(f"Error opening YouTube search with Brave: {e}. Falling back to default browser.")
                webbrowser.open(url)
                return True
        else:
            # Fallback to default browser
            webbrowser.open(url)
            return True
        
    except Exception as e:
        print(f"Error searching YouTube: {e}")
        return False


def open_world_monitor():
    """Open the World Monitor dashboard"""
    try:
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
