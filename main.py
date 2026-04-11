import time
import random
from voice.tts import speak_streaming
from voice.stt import listen
from voice.wake_word import listen_for_wake_word, is_wake_word
from brain.ollama import ask_brain, is_ollama_running
from brain.command_parser import parse_command
from memory.learning import cache_command, log_failure, get_most_used_commands, remember_fact, recall_facts, clear_memory
from actions.apps import open_app
from actions.web import (open_url, search_google, search_youtube, 
                         open_world_monitor, open_claude, open_chatgpt)
from actions.system import (get_time, get_date, get_battery, take_screenshot, 
                            shutdown_pc, restart_pc, click_text, find_text_on_screen)


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
            search_google(target)
            response = get_response("search_google", target=target)
        
        # Search YouTube
        elif action == "search_youtube":
            search_youtube(target)
            response = get_response("search_youtube", target=target)
        
        # Open World Monitor
        elif action == "open_world_monitor":
            open_world_monitor()
            response = get_response("open_world_monitor")
        
        # Get time
        elif action == "get_time":
            response = get_time()
        
        # Get date
        elif action == "get_date":
            response = get_date()
        
        # Get battery
        elif action == "get_battery":
            response = get_battery()
        
        # Take screenshot
        elif action == "take_screenshot":
            response = take_screenshot()
        
        # Click text on screen using OCR
        elif action == "click_text":
            response = click_text(target)
        
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
    
    # Greeting
    speak_streaming("FRIDAY online. How can I help you boss?")
    
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
        speak_streaming("Shutting down.")
        exit()
