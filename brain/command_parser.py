KNOWN_APPS = [
    "chrome", "brave", "firefox", "edge", "spotify", "discord",
    "whatsapp", "telegram", "notepad", "calculator", "vlc", "steam",
    "vscode", "vs code", "code", "excel", "word", "powerpoint", "paint",
    "explorer", "file explorer", "task manager", "zoom", "teams", "slack",
    "obs", "blender", "photoshop", "illustrator", "premiere"
]


def parse_command(text):
    """Parse user input and extract action and target"""
    try:
        text = text.lower().strip()
        
        # Open/Launch/Start apps
        if any(cmd in text for cmd in ["open", "launch", "start"]):
            for cmd in ["open", "launch", "start"]:
                if cmd in text:
                    app_name = text.split(cmd, 1)[1].strip()
                    if app_name and (app_name in KNOWN_APPS or len(app_name) > 0):
                        return {"action": "open_app", "target": app_name}
        
        # Close/Kill apps
        if "close" in text or "kill" in text:
            for cmd in ["close", "kill"]:
                if cmd in text:
                    app_name = text.split(cmd, 1)[1].strip()
                    if app_name:
                        return {"action": "close_app", "target": app_name}
        
        # YouTube search
        if "search" in text and "youtube" in text:
            query = text
            if "search youtube for" in text:
                query = text.split("search youtube for")[1].strip()
            elif "for" in text:
                query = text.split("for")[1].strip()
            else:
                query = text.split("youtube")[1].strip()
            return {"action": "search_youtube", "target": query}
        
        # Google search
        if "search" in text or "google" in text:
            query = text
            if "search for" in text:
                query = text.split("search for")[1].strip()
            elif "search" in text:
                query = text.split("search")[1].strip()
            elif "google for" in text:
                query = text.split("google for")[1].strip()
            elif "google" in text:
                query = text.split("google")[1].strip()
            return {"action": "search_google", "target": query}
        
        # Open YouTube
        if "youtube" in text:
            return {"action": "open_url", "target": "youtube"}
        
        # Open Claude
        if "claude" in text or "cloud" in text:
            return {"action": "open_url", "target": "claude"}
        
        # Open ChatGPT
        if "chatgpt" in text or "gpt" in text:
            return {"action": "open_url", "target": "chatgpt"}
        
        # World Monitor
        if any(word in text for word in ["world", "whats going on", "what's going on", "outside"]):
            return {"action": "open_world_monitor", "target": None}
        
        # Time
        if "time" in text:
            return {"action": "get_time", "target": None}
        
        # Date
        if "date" in text:
            return {"action": "get_date", "target": None}
        
        # Battery
        if "battery" in text:
            return {"action": "get_battery", "target": None}
        
        # Screenshot
        if "screenshot" in text:
            return {"action": "take_screenshot", "target": None}
        
        # Shutdown
        if "shutdown" in text:
            return {"action": "shutdown_pc", "target": None}
        
        # Restart
        if "restart" in text:
            return {"action": "restart_pc", "target": None}
        
        # Default: pass to brain for conversation
        return {"action": "ask_brain", "target": text}
    
    except Exception as e:
        print(f"Error parsing command: {e}")
        return {"action": "ask_brain", "target": text}
