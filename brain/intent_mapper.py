"""
Intent mapper for FRIDAY AI assistant.
Maps different user phrases to standardized intents for flexible command parsing.
"""

# Website targets that should always trigger "open_website" intent
# Override normal intent detection to ensure website commands are properly routed
WEBSITE_TARGETS = ["youtube", "google", "chatgpt", "gmail"]

# Map intents to keywords that trigger them
# Multiple keywords can trigger the same intent (e.g., "open", "launch", "start" all trigger "open_app")
INTENTS = {
    "open_app": ["open", "launch", "start", "run"],
    "open_website": ["open", "go to", "visit", "browse"],
    "search": ["search", "find", "look for", "google"],
    "get_time": ["time", "what time", "current time"],
    "get_date": ["date", "today", "what day"],
    "close_app": ["close", "quit", "kill", "stop"],
    "take_screenshot": ["screenshot", "capture", "screen shot", "snap"],
    "get_battery": ["battery", "battery level", "charge"],
    "shutdown": ["shutdown", "power off", "turn off"],
    "restart": ["restart", "reboot"],
}

# Keywords to remove when extracting target
COMMON_KEYWORDS = set()
for keywords in INTENTS.values():
    COMMON_KEYWORDS.update(keywords)
COMMON_KEYWORDS.update(["the", "a", "an", "for", "with", "of"])


def extract_intent(user_input):
    """
    Extract intent from user input by matching keywords.
    
    Uses two-tier detection:
    1. WEBSITE_TARGETS override: If any website target is found, always return "open_website"
       This ensures "open youtube", "launch youtube", "go to youtube" all route to open_website
    2. Keyword matching: Loop through INTENTS dict to find matching keywords
    
    Args:
        user_input: User's natural language command
        
    Returns:
        Intent name (str) if found, None otherwise
        
    Example:
        extract_intent("open youtube") → "open_website" (WEBSITE_TARGETS override)
        extract_intent("launch youtube") → "open_website" (WEBSITE_TARGETS override)
        extract_intent("open chrome") → "open_app"
        extract_intent("search google") → "open_website" (WEBSITE_TARGETS override, not search!)
        extract_intent("what time is it") → "get_time"
    """
    text = user_input.lower().strip()
    
    # PRIORITY 1: Check for website targets first (override normal intent detection)
    # This ensures website names always trigger "open_website" regardless of other keywords
    for target in WEBSITE_TARGETS:
        if target in text:
            return "open_website"
    
    # PRIORITY 2: Loop through each intent and its keywords (normal detection)
    for intent, keywords in INTENTS.items():
        for keyword in keywords:
            if keyword in text:
                return intent
    
    return None


def extract_target(user_input):
    """
    Extract the target/object from user input.
    Removes known keywords and returns the meaningful part.
    
    Note: WEBSITE_TARGETS are NOT removed, so they're preserved in output
    Example: "open youtube" → "youtube", "launch gmail" → "gmail"
    
    Args:
        user_input: User's natural language command
        
    Returns:
        Target text (str) or empty string if nothing meaningful
        
    Example:
        extract_target("open chrome") → "chrome"
        extract_target("launch youtube") → "youtube"
        extract_target("search for recipes") → "recipes"
        extract_target("what time is it") → ""
    """
    text = user_input.lower().strip()
    
    # Remove each known keyword from the text, keep the rest
    for keyword in COMMON_KEYWORDS:
        text = text.replace(keyword, " ")
    
    # Clean up multiple spaces
    target = " ".join(text.split()).strip()
    
    return target


def normalize_command(user_input):
    """
    Normalize user input into structured intent + target format.
    Combines intent extraction and target extraction.
    
    Uses website target override for known sites:
    - WEBSITE_TARGETS (youtube, google, chatgpt, gmail) always → "open_website" intent
    
    Args:
        user_input: User's natural language command
        
    Returns:
        Dict with "intent" and "target" keys
        
    Example:
        normalize_command("open chrome") → 
            {"intent": "open_app", "target": "chrome"}
        
        normalize_command("launch youtube") →
            {"intent": "open_website", "target": "youtube"}
        
        normalize_command("go to gmail") →
            {"intent": "open_website", "target": "gmail"}
        
        normalize_command("search for recipes") →
            {"intent": "search", "target": "recipes"}
    """
    intent = extract_intent(user_input)
    target = extract_target(user_input)
    
    return {
        "intent": intent,
        "target": target
    }
