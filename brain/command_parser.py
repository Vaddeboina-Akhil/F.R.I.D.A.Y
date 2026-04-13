KNOWN_APPS = [
    "chrome", "brave", "firefox", "edge", "spotify", "discord",
    "whatsapp", "telegram", "notepad", "calculator", "vlc", "steam",
    "vscode", "vs code", "code", "excel", "word", "powerpoint", "paint",
    "explorer", "github", "notion", "postman", "figma", "obs", "zoom",
    "teams", "slack", "task manager"
]

YOUTUBE_KEYWORDS = [
    "tutorial", "tutorials", "video", "videos", "song", "songs",
    "music", "movie", "movies", "watch", "shorts", "gameplay", "review", 
    "trailer", "vlog", "podcast", "anime", "funny", "comedy", "stream", 
    "streaming", "live stream", "coding", "mrbeast", "how to", "diy", 
    "recipe", "dance", "cover", "remix", "highlights", "match highlights"
]

GOOGLE_KEYWORDS = [
    "score", "scores", "news", "weather", "price", "prices",
    "wiki", "wikipedia", "who is", "when", "how much", "stock", "rate", 
    "result", "results", "ipl", "cricket", "football", "nba", "today",
    "latest", "current", "election", "population", "capital", "distance",
    "meaning", "definition", "what is", "where is", "history of",
    "top team", "best team", "standings", "table", "ranking", 
    "leaderboard", "points table", "who won", "winner", "champion",
    "premier league", "bundesliga", "la liga", "serie a", "champions league"
]

WEBSITES = [
    "youtube", "google", "claude", "chatgpt", "github.com",
    "netflix", "instagram", "twitter", "facebook", "linkedin", "reddit",
    "amazon", "flipkart", "world monitor"
]


def parse_command(text):
    """Parse user input and extract action and target in priority order"""
    try:
        text = text.lower().strip()
        
        # ===== CHECK 0: Close App Commands (HIGHEST PRIORITY) =====
        if "close" in text:
            if "close all" in text:
                return {"action": "close_all_apps", "target": None}
            # Extract app name after "close"
            target = text.replace("close", "").strip()
            if target:
                return {"action": "close_app", "target": target}
        
        # ===== CHECK 1: Open + And + Search (HIGHEST PRIORITY) =====
        if "open" in text and "and" in text and "search" in text:
            parts = text.split("and", 1)
            app = parts[0].replace("open", "").strip()
            query = parts[1].replace("search for", "").replace("search", "").strip()
            if app and query:
                return {"action": "open_and_search", "target": f"{app}|{query}"}
        
        # ===== CHECK 2: Open App or Website =====
        if text.startswith("open") or text.startswith("launch") or text.startswith("start"):
            target = text.replace("open", "").replace("launch", "").replace("start", "").strip()
            target = target.replace("the ", "").replace("my ", "").strip()
            
            if target:
                FILE_MANAGER_WORDS = ["file manager", "file explorer", "files", "explorer", "my files", "folders"]
                if any(word in target for word in FILE_MANAGER_WORDS):
                    return {"action": "open_app", "target": "explorer"}
                
                WHATSAPP_WORDS = ["whatsapp", "whats app", "what's app"]
                if any(word in target for word in WHATSAPP_WORDS):
                    return {"action": "open_app", "target": "whatsapp"}
                
                # Check if it's a website
                if any(website in target for website in WEBSITES):
                    return {"action": "open_url", "target": target}
                
                return {"action": "open_app", "target": target}
        
        # ===== CHECK 3: Explicit YouTube Search =====
        if "youtube" in text and ("search" in text or "find" in text or "look" in text):
            query = text.replace("youtube", "").replace("search", "").replace("for", "").replace("find", "").strip()
            return {"action": "search_youtube", "target": query}
        
        # ===== CHECK 4: Explicit Google Search =====
        if "google" in text and ("search" in text or "find" in text):
            query = text.replace("google", "").replace("search", "").replace("for", "").strip()
            return {"action": "search_google", "target": query}
        
        # ===== CHECK 5: News and Scores Direct Routing =====
        direct_google_phrases = [
            "news", "score", "scores", "ipl", "cricket score", "cricket", 
            "weather", "temperature", "price", "stock", "rate", "result", 
            "who won", "what happened"
        ]
        if any(phrase in text for phrase in direct_google_phrases):
            return {"action": "search_google", "target": text}
        
        # ===== CHECK 6: General Search =====
        if "search" in text or "find" in text or "look up" in text:
            query = text
            for word in ["search for", "search", "find", "look up", "for"]:
                query = query.replace(word, "").strip()
            
            # Check YouTube keywords first
            if any(keyword in query.lower() for keyword in YOUTUBE_KEYWORDS):
                return {"action": "search_youtube", "target": query}
            
            # Default to Google for other searches
            return {"action": "search_google", "target": query}
        
        # ===== CHECK 7: World Briefing (News) =====
        briefing_phrases = [
            "what's going on", "whats going on", "what is going on",
            "what's happening", "whats happening", "what is happening",
            "around the world", "world news", "global news", "brief me",
            "world briefing", "news briefing", "catch me up", "latest news", "today's news"
        ]
        if any(phrase in text for phrase in briefing_phrases):
            return {"action": "world_briefing", "target": None}
        
        # News + specific topic
        if "news" in text:
            TOPIC_KEYWORDS = ["tech", "sports", "cricket", "football", "business", "india", "market"]
            for keyword in TOPIC_KEYWORDS:
                if keyword in text:
                    topic = text.replace("news", "").replace("about", "").strip()
                    return {"action": "get_news_topic", "target": topic}
        
        # ===== CHECK 8: World Monitor =====
        if any(word in text for word in ["world", "outside", "global"]):
            return {"action": "open_world_monitor", "target": None}
        
        # ===== CHECK 9: Screen Commands =====
        if "what do you see" in text or "what can you see" in text or "whats on screen" in text:
            return {"action": "whats_on_screen", "target": None}
        
        if "scroll down" in text:
            return {"action": "scroll_down", "target": None}
        
        if "scroll up" in text:
            return {"action": "scroll_up", "target": None}
        
        if "click" in text:
            target = text.replace("click", "").strip()
            return {"action": "click_text", "target": target}
        
        if "type" in text:
            target = text.replace("type", "").strip()
            return {"action": "type_text", "target": target}
        
        if "press enter" in text:
            return {"action": "press_key", "target": "enter"}
        
        # ===== CHECK 10: Timer and Alarm Commands (BEFORE time check!) =====
        # Timer: has duration keywords (minutes, seconds, hours, etc)
        if ("timer" in text and ("minute" in text or "second" in text or "hour" in text or "min" in text or "sec" in text or "hr" in text)):
            duration = text.replace("set", "").replace("timer", "").replace("a", "").strip()
            if duration:
                return {"action": "set_timer", "target": duration}
        
        # Alarm: has time keywords (AM, PM, o'clock) or time pattern (digits without duration keywords)
        if ("alarm" in text and ("am" in text or "pm" in text or "o'clock" in text or "oclock" in text)):
            time_str = text.replace("set", "").replace("alarm", "").replace("for", "").strip()
            if time_str:
                return {"action": "set_alarm", "target": time_str}
        
        # Alarm with just time (e.g., "alarm for 7" where 7 is clearly a time)
        if "alarm" in text:
            time_str = text.replace("set", "").replace("alarm", "").replace("for", "").strip()
            # Only treat as alarm if it looks like a time (has digits but no duration keywords)
            if time_str and not any(word in time_str for word in ["minute", "second", "hour", "min", "sec", "hr"]):
                return {"action": "set_alarm", "target": time_str}
        
        if "open clock" in text or "open timer" in text:
            return {"action": "open_clock", "target": None}
        
        # ===== CHECK 11: System Commands =====
        # Check time but exclude timer, alarm
        if "time" in text and "timer" not in text and "alarm" not in text:
            return {"action": "get_time", "target": None}
        
        if "date" in text:
            return {"action": "get_date", "target": None}
        
        if "battery" in text:
            return {"action": "get_battery", "target": None}
        
        if "screenshot" in text:
            return {"action": "take_screenshot", "target": None}
        
        if "shutdown" in text:
            return {"action": "shutdown_pc", "target": None}
        
        if "restart" in text:
            return {"action": "restart_pc", "target": None}
        
        # ===== CHECK 11: Memory Commands =====
        if "remember" in text:
            fact = text.replace("remember", "").strip()
            return {"action": "remember_fact", "target": fact}
        
        if "what do you know about me" in text or "what do you remember" in text:
            return {"action": "recall_memory", "target": None}
        
        if "most used" in text or "my habits" in text:
            return {"action": "get_habits", "target": None}
        
        # ===== CHECK 12: Screen Analysis Commands =====
        # Check for explicit screen observation phrases
        screen_phrases = [
            "what's on my screen", "whats on my screen", "what do you see",
            "what can you see", "what is on my screen", "read my screen",
            "what's on screen", "screen"
        ]
        if any(phrase in text for phrase in screen_phrases):
            return {"action": "whats_on_screen", "target": None}
        
        # Check for "what" + "screen" combination
        if "what" in text and "screen" in text:
            return {"action": "whats_on_screen", "target": None}
        
        # Check for repositories/repos context with screen or github
        if "repositories" in text or "repos" in text:
            if "screen" in text or "github" in text:
                return {"action": "whats_on_screen", "target": None}
        
        # ===== CHECK 12: Sports and Standings Queries =====
        # Explicit sports team/standings queries
        if "which team" in text or "who is leading" in text or "top of" in text:
            return {"action": "search_google", "target": text}
        
        # Which + sport word combination
        if "which" in text:
            SPORT_WORDS = [
                "league", "team", "club", "player", "match", "tournament",
                "ipl", "cricket", "football", "basketball", "tennis", "fifa"
            ]
            if any(sport in text for sport in SPORT_WORDS):
                return {"action": "search_google", "target": text}
        
        # ===== CHECK 13: Send WhatsApp Message =====
        # Check 1: "send" + "whatsapp"
        if "send" in text and "whatsapp" in text:
            return {"action": "whatsapp_flow", "target": text}
        
        # Check 2: "write/send a message" with contact
        if "message" in text and ("send" in text or "write" in text):
            COMMON_NAMES = ["sai", "akhil", "john", "sarah", "mom", "dad", "brother", "sister", "friend"]
            DIRECT_TARGETS = ["myself", "me", "self", "minegang", "mine gang", "mummy", "mommy", "mom"]
            
            # Check for direct targets first
            for target in DIRECT_TARGETS:
                if target in text:
                    return {"action": "whatsapp_flow", "target": text}
            
            # Then check common names
            if any(name in text for name in COMMON_NAMES):
                return {"action": "whatsapp_flow", "target": text}
        
        # Check 3: "whatsapp" without "open" or "close"
        if "whatsapp" in text and "open" not in text and "close" not in text:
            return {"action": "whatsapp_flow", "target": text}
        
        # ===== CHECK 14: Send Email =====
        if "send email" in text or ("email" in text and "send" in text):
            contact = ""
            subject = "Message from FRIDAY"
            body = ""
            
            if " to " in text:
                after_to = text.split(" to ", 1)[1]
                contact = after_to.split()[0].strip() if after_to else ""
                
                # Extract subject
                if " subject " in text:
                    subject_part = text.split(" subject ", 1)[1]
                    subject = subject_part.split()[0] if subject_part else "Message from FRIDAY"
                
                # Extract body (text after "saying", "body", or "message")
                for body_word in ["saying", "body", "message"]:
                    if f" {body_word} " in text:
                        body = text.split(f" {body_word} ", 1)[1].strip()
                        break
            
            if contact and body:
                return {"action": "send_email", "target": f"{contact}|{subject}|{body}"}
        
        # ===== CHECK 15: Open/Check WhatsApp =====
        if "read whatsapp" in text or "check whatsapp" in text or "any messages" in text:
            return {"action": "open_whatsapp", "target": None}
        
        # ===== CHECK 16: Email Flow (Comprehensive Email Detection) =====
        # Main email triggers
        if any(phrase in text for phrase in ["send email", "send mail", "compose email", "write email", "email to"]):
            # Check for personal account
            if any(word in text for word in ["personal", "gmail", "personal account"]):
                return {"action": "email_flow", "target": "to personal account"}
            
            # Check for college account
            if any(word in text for word in ["college", "vbit", "college mail", "college account"]):
                return {"action": "email_flow", "target": "to college account"}
            
            # Default to email_flow with full text
            return {"action": "email_flow", "target": text}
        
        # Alternative email trigger: "send" + "mail"
        if "send" in text and "mail" in text:
            if any(word in text for word in ["college", "vbit"]):
                return {"action": "email_flow", "target": "to college account"}
            elif "personal" in text:
                return {"action": "email_flow", "target": "to personal account"}
            else:
                return {"action": "email_flow", "target": text}
        
        # ===== CHECK 17: Open Gmail =====
        if "open gmail" in text or "check email" in text or "check mail" in text:
            if "college" in text:
                return {"action": "open_gmail", "target": "college"}
            else:
                return {"action": "open_gmail", "target": "personal"}

        
        # ===== DEFAULT: Use AI to decide action (smart fallback) =====
        from brain.ollama import decide_action
        result = decide_action(text)
        print(f"AI decided: {result}")
        return result
    
    except Exception as e:
        print(f"Error parsing command: {e}")
        return {"action": "ask_brain", "target": text}
