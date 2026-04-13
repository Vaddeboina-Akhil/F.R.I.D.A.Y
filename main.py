import time
import datetime
import random
import webbrowser
from voice.tts import speak_streaming, speak
from voice.stt import listen
from voice.wake_word import listen_for_wake_word, is_wake_word
from brain.ollama import ask_brain, is_ollama_running, correct_command
from brain.command_parser import parse_command
from memory.memory import cache_command, log_failure, get_most_used_commands, remember_fact, recall_facts, clear_memory, get_cached_command
from memory.memory import load_memory
from actions.apps import open_app, close_app, close_all_apps
from actions.whatsapp import send_message_to_contact, send_whatsapp_flow
from actions.email_sender import send_email_to_contact
from actions.email_flow import run_email_flow
from actions.web import (open_url, search_google, search_youtube, 
                         open_world_monitor, open_claude, open_chatgpt, open_and_search)
from actions.web_reader import search_and_read
from actions.news_reader import get_greeting, get_world_briefing, get_india_briefing, get_news_by_topic
from actions.system import (get_time, get_date, get_battery, take_screenshot, 
                            shutdown_pc, restart_pc)
from actions.clock import open_clock, set_timer, set_alarm, close_clock
from actions.screen import click_text, find_text_on_screen, get_screen_text, scroll_down, scroll_up, type_text, press_key
from actions.screen_monitor import start_monitoring, stop_monitoring, get_current_screen, is_text_on_screen


# Response variations for natural, conversational feel
RESPONSE_VARIATIONS = {
    "open_app_success": [
        "Opening {target} now.",
        "Launching {target} for you.",
        "Got it. Starting {target}.",
        "Opening {target}.",
        "I'll launch {target} right away.",
        "Starting up {target}.",
    ],
    "open_app_failure": [
        "I couldn't find {target} on your system.",
        "Hmm, I don't see {target} installed.",
        "I can't locate {target}.",
        "That application doesn't seem to be installed.",
    ],
    "open_url": [
        "Launching {target} now.",
        "Opening {target} for you.",
        "Got it. Loading {target}.",
        "Taking you to {target}.",
        "Opening {target}.",
    ],
    "search_google": [
        "Searching for {target} now.",
        "Let me find that for you.",
        "Searching Google for {target}.",
        "Looking that up for you.",
        "I'll search for {target}.",
    ],
    "search_youtube": [
        "Searching YouTube for {target}.",
        "Let me find that on YouTube.",
        "Looking up {target} on YouTube.",
        "Searching YouTube now.",
    ],
    "open_world_monitor": [
        "Opening World Monitor. You can see live global conflicts, hotspots, sanctions, weather and outages.",
        "Pulling up World Monitor for you.",
        "Loading World Monitor. Check out what's happening globally.",
    ],
    "remember_fact_success": [
        "Got it. I'll remember that.",
        "Noted. I'll keep that in mind.",
        "You got it boss. I'll remember.",
        "Got that. I'll save that one.",
    ],
    "remember_fact_failure": [
        "I had trouble remembering that one.",
        "Something went wrong saving that.",
        "I couldn't store that fact.",
    ],
    "recall_memory_success": [
        "I remember: {facts}.",
        "Here's what I know about you: {facts}.",
        "I've got this: {facts}.",
    ],
    "recall_memory_none": [
        "I don't remember anything about you yet.",
        "We're just getting started, so I haven't learned much yet.",
        "No facts stored yet. Tell me something about yourself.",
    ],
    "get_habits": [
        "Your most used commands are: {habits}.",
        "Here's what you usually do: {habits}.",
        "You've been using these a lot: {habits}.",
    ],
    "get_habits_none": [
        "You haven't built up any habits yet.",
        "Not enough data yet. Keep using commands and I'll learn your patterns.",
        "No habits recorded yet. Start using me more.",
    ],
    "clear_memory_success": [
        "Memory cleared. I've forgotten everything.",
        "Done. Wiped the slate clean.",
        "All cleared. Starting fresh.",
    ],
    "clear_memory_failure": [
        "I had trouble clearing memory.",
        "Something went wrong with clearing memory.",
        "I couldn't clear that.",
    ],
    "invalid_command": [
        "That didn't make sense. Try saying something longer or more specific.",
        "I didn't catch that. Could you say it differently?",
        "Sorry, I didn't understand. Can you rephrase that?",
        "That's unclear. Give me more details.",
    ],
}


def get_response(response_type, **kwargs):
    """Get a random response variation and format with context"""
    options = RESPONSE_VARIATIONS.get(response_type, ["OK boss."])
    return random.choice(options).format(**kwargs)


def execute_command(command, original_text=""):
    """Execute a parsed command and return response with learning"""
    try:
        action = command.get("action")
        target = command.get("target")
        response = None
        
        # Open apps
        if action == "open_app":
            result = open_app(target)
            if result:
                response = get_response("open_app_success", target=target)
            else:
                response = get_response("open_app_failure", target=target)
        
        # Close apps
        elif action == "close_app":
            result = close_app(target)
            if result:
                response = f"Closed {target} boss."
            else:
                response = f"Couldn't close {target} boss."
        
        # Close all apps
        elif action == "close_all_apps":
            result = close_all_apps()
            if result:
                response = "Closed all apps boss."
            else:
                response = "Error closing apps boss."
        
        # Open URLs
        elif action == "open_url":
            if target == "youtube":
                open_url("https://youtube.com")
            elif target == "claude":
                open_claude()
            elif target == "chatgpt":
                open_chatgpt()
            response = get_response("open_url", target=target)
        
        # Search Google
        elif action == "search_google":
            result = search_and_read(target)
            if result:
                response = f"According to Google: {result}"
            else:
                search_google(target)
                response = f"I've opened Google results for {target} boss."
        
        # Search YouTube
        elif action == "search_youtube":
            search_youtube(target)
            response = f"Searching YouTube for {target} boss."
        
        # Open and Search (combined action)
        elif action == "open_and_search":
            response = open_and_search(target)
        
        # World news briefing
        elif action == "world_briefing":
            speak_streaming("Give me a second boss, let me check...")
            data = get_world_briefing()
            open_world_monitor()
            
            # Build prompt for Ollama to deliver briefing in FRIDAY's style
            prompt = f"""You are FRIDAY from Iron Man. Deliver this world news briefing 
in your signature style - confident, sharp, slightly dramatic like a real 
intelligence briefing. Make it sound like you actually care about what's 
happening. Keep it under 4 sentences total. 
Global headlines: {data['raw']}
India headlines: {data['india_raw']}
Deliver the briefing now:"""
            
            response = ask_brain(prompt)
            response += " I've opened the World Monitor so you can track it visually boss."
        
        # India news briefing
        elif action == "india_briefing":
            speak_streaming("Checking India news boss...")
            data = get_india_briefing()
            
            # Build prompt for Ollama to deliver India briefing
            prompt = f"""You are FRIDAY from Iron Man. Deliver this India news briefing 
in your signature style. Sharp, confident, 3 sentences max.
Headlines: {data['raw']}
Deliver now:"""
            
            response = ask_brain(prompt)
        # News by topic
        elif action == "get_news_topic":
            headlines = get_news_by_topic(target)
            if not headlines:
                response = "Couldn't fetch that news boss."
            else:
                response = f"Here's the latest on {target} boss. "
                for headline in headlines:
                    response += f"{headline}. "
                response = response.strip()
        
        # Open World Monitor
        elif action == "open_world_monitor":
            speak_streaming("Opening World Monitor boss.")
            open_world_monitor()
            response = "World Monitor is now open boss."
        
        # Send WhatsApp message
        elif action == "send_whatsapp":
            parts = target.split("|")
            contact = parts[0].strip() if len(parts) > 0 else ""
            message = parts[1].strip() if len(parts) > 1 else "Hello"
            
            if not contact:
                response = "Who should I send the message to boss?"
            else:
                speak(f"Sending WhatsApp message to {contact} boss.")
                success, msg = send_message_to_contact(contact, message)
                response = msg
        
        # Send email
        elif action == "send_email":
            parts = target.split("|")
            contact = parts[0].strip() if len(parts) > 0 else ""
            subject = parts[1].strip() if len(parts) > 1 else "Message from FRIDAY"
            body = parts[2].strip() if len(parts) > 2 else ""
            
            if not contact:
                response = "Who should I send the email to boss?"
            else:
                speak(f"Sending email to {contact} boss.")
                success, msg = send_email_to_contact(contact, subject, body)
                response = msg
        
        # Open WhatsApp
        elif action == "open_whatsapp":
            open_app("whatsapp")
            response = "Opening WhatsApp boss."
        
        # Email flow (conversational email composition)
        elif action == "email_flow":
            speak("Starting email flow boss.")
            result = run_email_flow(target)
            response = result
        
        # WhatsApp flow (conversational WhatsApp messaging)
        elif action == "whatsapp_flow":
            result = send_whatsapp_flow(target)  # Pass target contact if available
            response = result
        
        # Open Gmail
        elif action == "open_gmail":
            if target == "college":
                webbrowser.open("https://mail.google.com/mail/u/1/")
                response = "Opening college Gmail boss."
            else:
                webbrowser.open("https://mail.google.com/mail/u/0/")
                response = "Opening personal Gmail boss."
        
        # Get time
        elif action == "get_time":
            response = get_time()
        
        # Get date
        elif action == "get_date":
            response = get_date()
        
        # Get battery
        elif action == "get_battery":
            response = get_battery()
        
        # Set Timer
        elif action == "set_timer":
            speak("Setting up timer boss.")
            success, msg = set_timer(target)
            response = msg
        
        # Set Alarm
        elif action == "set_alarm":
            speak("Setting up alarm boss.")
            success, msg = set_alarm(target)
            response = msg
        
        # Open Clock
        elif action == "open_clock":
            speak("Opening clock app boss.")
            open_clock()
            response = "Clock app is now open boss."
        
        # Take screenshot
        elif action == "take_screenshot":
            response = take_screenshot()
        
        # Click text on screen using OCR
        elif action == "click_text":
            success, msg = click_text(target)
            return msg
        
        # Read screen text using OCR
        elif action == "read_screen":
            text = get_screen_text()
            if not text:
                return "I cannot read anything on screen boss."
            return f"{text[:200]}...that's what I can see boss."
        
        # Scroll down
        elif action == "scroll_down":
            scroll_down()
            return "Scrolling down boss."
        
        # Scroll up
        elif action == "scroll_up":
            scroll_up()
            return "Scrolling up boss."
        
        # Type text
        elif action == "type_text":
            type_text(target)
            return f"Typed {target} boss."
        
        # Press key
        elif action == "press_key":
            press_key(target)
            return f"Pressed {target} boss."
        
        # Shutdown PC
        elif action == "shutdown_pc":
            response = shutdown_pc()
        
        # Restart PC
        elif action == "restart_pc":
            response = restart_pc()
        
        # Get habits/most used commands
        elif action == "get_habits":
            commands = get_most_used_commands(5)
            if commands:
                habits = ", ".join([cmd["display"] for cmd in commands])
                response = get_response("get_habits", habits=habits)
            else:
                response = get_response("get_habits_none")
        
        # Invalid command (failed validation)
        elif action == "invalid":
            response = get_response("invalid_command")
        
        # Clear memory
        elif action == "clear_memory":
            if clear_memory():
                response = get_response("clear_memory_success")
            else:
                response = get_response("clear_memory_failure")
        
        # Remember fact
        elif action == "remember_fact":
            if remember_fact(target):
                response = get_response("remember_fact_success")
            else:
                response = get_response("remember_fact_failure")
        
        # Recall memory
        elif action == "recall_memory":
            facts = recall_facts()
            if facts:
                facts_str = ", ".join(facts)
                response = get_response("recall_memory_success", facts=facts_str)
            else:
                response = get_response("recall_memory_none")
        
        # What's on screen - with AI analysis
        elif action == "whats_on_screen":
            raw_text = get_current_screen()
            
            # Check if screen text is empty or too short
            if not raw_text or len(raw_text) < 20:
                return "I cannot see anything clearly on your screen boss."
            
            # Clean raw_text: normalize whitespace and limit to 800 chars
            clean = ' '.join(raw_text.split())[:800]
            
            # Send to AI with detailed FRIDAY character prompt for screen analysis
            prompt = f"""You are FRIDAY, Iron Man's AI assistant.
Analyze this screen content carefully.
The user has multiple browser tabs open - focus ONLY on the ACTIVE/CURRENT tab content.
Ignore tab names at the top, focus on the main page content below.
Identify: exact website, specific content like repo names, scores, headlines, video titles.
If GitHub: list actual repository names visible in main content area.
If YouTube: list actual video titles visible.
Be specific and accurate. Do not guess. Only mention what you can clearly see.
Keep response to 2 sentences max.
Screen content: {clean}"""
            response = ask_brain(prompt)
            
            return response
        
        # Is text visible on screen
        elif action == "is_text_visible":
            result = is_text_on_screen(target)
            if result:
                return f"Yes boss, I can see {target} on screen"
            else:
                return f"No boss, I cannot see {target} on screen"
        
        # Start screen monitoring
        elif action == "start_monitoring":
            start_monitoring(interval=2)
            return "Screen monitoring started boss."
        
        # Stop screen monitoring
        elif action == "stop_monitoring":
            stop_monitoring()
            return "Screen monitoring stopped boss."
        
        # Ask brain (default conversation)
        elif action == "ask_brain":
            response = ask_brain(target)
        
        # Default fallback
        else:
            response = ask_brain(target)
        
        # Cache successful command using intent-based key (action:target)
        # This groups different phrasings of the same command together
        if response and original_text:
            cache_command(original_text, action, response, target)
        
        return response
    
    except Exception as e:
        # Log failure
        if original_text:
            log_failure(original_text, command.get("action", "unknown"), str(e))
        print(f"Error executing command: {e}")
        return "Sorry boss, something went wrong."


def main():
    print("Initializing FRIDAY...")
    
    # Check if Ollama is running
    if not is_ollama_running():
        speak_streaming("Ollama is not running. Please start Ollama.")
        return
    
    # Load memory and get greeting
    memory = load_memory()
    greeting = get_greeting()
    hour = datetime.datetime.now().hour
    user_name = memory["user"].get("name", "boss")
    
    # Smart greeting based on time and context
    if hour >= 22 or hour < 5:
        speak_streaming(f"{greeting} boss. You're awake late tonight. What are you up to?")
    elif memory["conversation_count"] > 0:
        speak_streaming(f"{greeting} boss. Welcome back. How can I help you today?")
    else:
        speak_streaming(f"FRIDAY online. {greeting} boss. How can I help you?")
    
    # Start screen monitoring
    start_monitoring(interval=2)
    print("Screen monitoring active")
    
    # Define active mode function
    def active_mode(initial_command=None):
        """Active listening mode for 30 seconds"""
        active_start = time.time()
        
        # Process initial command if provided
        if initial_command is not None:
            print(f"You said: {initial_command}")
            command = parse_command(initial_command)
            print(f"Action: {command['action']}")
            response = execute_command(command, initial_command)
            print(f"FRIDAY: {response}")
            speak_streaming(response)
            active_start = time.time()  # Reset timer after initial command
        
        # Listen for more commands for 30 seconds
        while time.time() - active_start < 30:
            text = listen()
            
            if text is None:
                continue
            
            print(f"You said: {text}")
            
            # Check for sleep/exit commands
            if any(word in text.lower() for word in ["sleep", "goodbye", "stop"]):
                speak_streaming("Going to sleep boss.")
                return
            
            # Remove wake words from text before processing
            clean_text = text.replace("friday", "").replace("edith", "").strip()
            if not clean_text:
                continue
            
            # Correct speech recognition errors
            corrected = correct_command(clean_text)
            if corrected != clean_text:
                print(f"Corrected: {corrected}")
                clean_text = corrected
            
            # Check cache for repeated commands
            cached = get_cached_command(clean_text)
            if cached and cached.get("count", 0) >= 2:
                print(f"Cache hit: {clean_text}")
                command = {"action": cached["action"], "target": cached.get("target", clean_text)}
            else:
                # Parse the command
                command = parse_command(clean_text)
            
            print(f"Action: {command['action']}")
            
            # Execute the command
            response = execute_command(command, clean_text)
            
            # Print and speak response
            print(f"FRIDAY: {response}")
            speak_streaming(response)
            
            # Reset timer after each command
            active_start = time.time()
    
    # Initial 30-second active mode on startup
    active_mode()
    
    # Outer loop: passive mode waiting for wake word
    while True:
        print("FRIDAY passive mode... say 'Friday' to activate")
        
        # Listen for wake word
        wake_detected, heard_text = listen_for_wake_word()
        
        # Wake word detected, activate
        speak_streaming("Yes boss?")
        
        # Remove wake word from heard text
        clean_command = heard_text.replace("friday", "").replace("edith", "").strip()
        
        # Enter active mode with or without initial command
        if clean_command:
            active_mode(initial_command=clean_command)
        else:
            active_mode()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        stop_monitoring()
        speak_streaming("Shutting down.")
        exit()
