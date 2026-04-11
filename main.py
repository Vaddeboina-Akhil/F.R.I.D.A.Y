import time
from voice.tts import speak_streaming
from voice.stt import listen
from voice.wake_word import listen_for_wake_word, is_wake_word
from brain.ollama import ask_brain, is_ollama_running
from brain.command_parser import parse_command
from actions.apps import open_app
from actions.web import (open_url, search_google, search_youtube, 
                         open_world_monitor, open_claude, open_chatgpt)
from actions.system import (get_time, get_date, get_battery, take_screenshot, 
                            shutdown_pc, restart_pc)


def execute_command(command):
    """Execute a parsed command and return response"""
    try:
        action = command.get("action")
        target = command.get("target")
        
        # Open apps
        if action == "open_app":
            result = open_app(target)
            if result:
                return f"Opening {target} boss."
            else:
                return f"I couldn't find {target} on your system boss."
        
        # Open URLs
        elif action == "open_url":
            if target == "youtube":
                open_url("https://youtube.com")
            elif target == "claude":
                open_claude()
            elif target == "chatgpt":
                open_chatgpt()
            return f"Opening {target} boss."
        
        # Search Google
        elif action == "search_google":
            search_google(target)
            return f"Searching for {target} boss."
        
        # Search YouTube
        elif action == "search_youtube":
            search_youtube(target)
            return f"Searching YouTube for {target} boss."
        
        # Open World Monitor
        elif action == "open_world_monitor":
            open_world_monitor()
            return "Opening World Monitor boss. You can see live conflicts, hotspots, sanctions, weather and outages globally."
        
        # Get time
        elif action == "get_time":
            return get_time()
        
        # Get date
        elif action == "get_date":
            return get_date()
        
        # Get battery
        elif action == "get_battery":
            return get_battery()
        
        # Take screenshot
        elif action == "take_screenshot":
            return take_screenshot()
        
        # Shutdown PC
        elif action == "shutdown_pc":
            return shutdown_pc()
        
        # Restart PC
        elif action == "restart_pc":
            return restart_pc()
        
        # Ask brain (default conversation)
        elif action == "ask_brain":
            return ask_brain(target)
        
        # Default fallback
        else:
            return ask_brain(target)
    
    except Exception as e:
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
            response = execute_command(command)
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
            response = execute_command(command)
            
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
