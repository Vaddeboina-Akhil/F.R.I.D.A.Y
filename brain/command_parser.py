KNOWN_APPS = [
    "chrome", "brave", "firefox", "edge", "spotify", "discord",
    "whatsapp", "telegram", "notepad", "calculator", "vlc", "steam",
    "vscode", "vs code", "code", "excel", "word", "powerpoint", "paint",
    "explorer", "file explorer", "task manager", "zoom", "teams", "slack",
    "obs", "blender", "photoshop", "illustrator", "premiere"
]

# Website targets that should never be treated as apps
# This safeguard prevents "open youtube" from becoming open_app
WEBSITE_TARGETS = ["youtube", "google", "chatgpt", "gmail"]

# YouTube-specific keywords - searches with these terms prefer YouTube
YOUTUBE_KEYWORDS = [
    "tutorial", "tutorials", "video", "videos", "song", "songs", "music",
    "movie", "movies", "watch", "mrbeast", "mr beast", "shorts", "gameplay",
    "review", "trailer", "vlog", "podcast", "anime", "funny", "comedy",
    "stream", "streaming", "live"
]

# Google-specific keywords - searches with these terms prefer Google
GOOGLE_KEYWORDS = [
    "news", "weather", "price", "definition", "meaning", "who is", "what is",
    "when did", "how much", "wikipedia", "wiki"
]

# Import intent mapper for flexible command parsing
from brain.intent_mapper import normalize_command


def parse_command(text):
    """Parse user input and extract action and target"""
    try:
        text = text.lower().strip()
        
        # ===== PRIORITY 0: Open and Search Commands (HIGHEST PRIORITY) =====
        # These should be checked before anything else
        
        # Check for "open" + "search" combination
        if "open" in text and "search" in text:
            app = text.split("and")[0].replace("open", "").strip()
            query = text.split("and")[1].replace("search for", "").replace("search", "").strip() if "and" in text else ""
            if app and query:
                return {"action": "open_and_search", "target": f"{app}|{query}"}
        
        # Check for "open" + "and" combination
        if "open" in text and "and" in text:
            app = text.split("and")[0].replace("open", "").strip()
            query = text.split("and")[1].replace("search for", "").replace("search", "").strip()
            if app and query:
                return {"action": "open_and_search", "target": f"{app}|{query}"}
        
        # Check if text starts with "search", "find", or "look up"
        text_words = text.split()
        if text_words and text_words[0] in ["search", "find", "look up"] or text.startswith("look up"):
            # Extract query
            if "for" in text:
                query = text.split("for", 1)[1].strip()
            else:
                # Skip the first word (search/find/look)
                if text.startswith("look up"):
                    query = text.replace("look up", "", 1).strip()
                else:
                    query = text.split(None, 1)[1] if len(text_words) > 1 else ""
            
            query = query.strip()
            
            # YouTube keywords for smart routing
            YOUTUBE_KEYWORDS = [
                "tutorial", "tutorials", "video", "videos", "song", "songs",
                "music", "movie", "movies", "watch", "mrbeast", "mr beast",
                "shorts", "gameplay", "review", "trailer", "vlog", "podcast",
                "anime", "funny", "comedy", "stream", "streaming", "live",
                "python", "coding"
            ]
            
            # If any keyword in query, search YouTube; default to YouTube
            if any(keyword in query.lower() for keyword in YOUTUBE_KEYWORDS):
                return {"action": "search_youtube", "target": query}
            
            return {"action": "search_youtube", "target": query}
        
        # ===== PRIORITY 1: Special Memory Commands (highest priority) =====
        # These are very specific and should not trigger intent mapping
        
        # Recall memory - MUST come before "Remember fact" to avoid false positives
        # "what do you remember" contains "remember" so it needs higher priority
        if "what do you know about me" in text or "what do you remember" in text:
            return {"action": "recall_memory", "target": None}
        
        # Clear memory
        if "clear memory" in text or "forget everything" in text:
            return {"action": "clear_memory", "target": None}
        
        # Get habits/most used commands
        if any(phrase in text for phrase in ["what do i usually", "most used", "my habits"]):
            return {"action": "get_habits", "target": None}
        
        # Remember fact - more generic, checks for "remember" anywhere in text
        # This runs after specific recall checks to avoid matching phrases like "what do you remember"
        if "remember" in text:
            fact = text.replace("remember", "").strip()
            
            # Validate fact to prevent storing invalid/incomplete statements
            # - Too short facts (< 5 chars) are usually mistakes or unclear
            # - Phrases with "what do you" indicate questions, not facts to remember
            # - Statements starting with "i said" are conversational, not factual
            # - Empty facts after cleanup should not be stored
            if len(fact) < 5 or "what do you" in fact or fact.startswith("i said") or not fact:
                return {"action": "invalid", "target": None}
            
            return {"action": "remember_fact", "target": fact}
        
        # ===== PRIORITY 2: Click Command (automated UI clicking) =====
        # "click submit", "click next", "click login" → find and click text on screen
        if "click" in text:
            target = text.replace("click", "").strip()
            if target:
                return {"action": "click_text", "target": target}
            else:
                return {"action": "invalid", "target": None}
        
        # ===== PRIORITY 3: Screen Reading Commands =====
        # Read current screen content using OCR
        if "read screen" in text or "what's on screen" in text or "whats on screen" in text:
            return {"action": "read_screen", "target": None}
        
        # Scroll down
        if "scroll down" in text:
            return {"action": "scroll_down", "target": None}
        
        # Scroll up
        if "scroll up" in text:
            return {"action": "scroll_up", "target": None}
        
        # Type text
        if "type" in text:
            target = text.replace("type", "").strip()
            if target:
                return {"action": "type_text", "target": target}
            else:
                return {"action": "invalid", "target": None}
        
        # Press keyboard keys
        if "press enter" in text or "hit enter" in text:
            return {"action": "press_key", "target": "enter"}
        
        
        if "press escape" in text or "hit escape" in text:
            return {"action": "press_key", "target": "escape"}
        
        # ===== PRIORITY 2: Screen Monitoring Commands =====
        # What can you see / What do you see / What's on screen
        if "what can you see" in text or "what do you see" in text or "whats on screen" in text or "what's on screen" in text:
            return {"action": "whats_on_screen", "target": None}
        
        # Can you see / Is there (on screen)
        if ("can you see" in text or "is there" in text) and "on screen" in text:
            target = text.replace("can you see", "").replace("is there", "").replace("on screen", "").strip()
            if target:
                return {"action": "is_text_visible", "target": target}
            else:
                return {"action": "invalid", "target": None}
        
        # Start monitoring / Watch screen
        if "start monitoring" in text or "watch screen" in text:
            return {"action": "start_monitoring", "target": None}
        
        # Stop monitoring / Stop watching
        if "stop monitoring" in text or "stop watching" in text:
            return {"action": "stop_monitoring", "target": None}
        
        # ===== PRIORITY 3: Intent Mapping (flexible, pattern-based) =====
        # Use intent mapper for flexible command parsing
        normalized = normalize_command(text)
        
        if normalized["intent"]:
            # Map detected intents to actions
            intent = normalized["intent"]
            target = normalized["target"]
            
            if intent == "open_app":
                # SAFEGUARD: Check if target is a website, not an app
                # This prevents "open youtube", "launch google", etc. from being treated as apps
                # Websites should always route to "open_url" action for proper browser handling
                if target and target.lower() in WEBSITE_TARGETS:
                    return {"action": "open_url", "target": target}
                return {"action": "open_app", "target": target}
            elif intent == "open_website":
                return {"action": "open_url", "target": target}
            elif intent == "search":
                return {"action": "search_google", "target": target}
            elif intent == "close_app":
                return {"action": "close_app", "target": target}
            elif intent == "take_screenshot":
                return {"action": "take_screenshot", "target": None}
            elif intent == "get_time":
                return {"action": "get_time", "target": None}
            elif intent == "get_date":
                return {"action": "get_date", "target": None}
            elif intent == "get_battery":
                return {"action": "get_battery", "target": None}
            elif intent == "shutdown":
                return {"action": "shutdown_pc", "target": None}
            elif intent == "restart":
                return {"action": "restart_pc", "target": None}
        
        # ===== PRIORITY 3: Specific website commands (high-value targets) =====
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
        
        # ===== PRIORITY 5: Default conversation =====
        # Default: pass to brain for conversation
        return {"action": "ask_brain", "target": text}
    
    except Exception as e:
        print(f"Error parsing command: {e}")
        return {"action": "ask_brain", "target": text}
