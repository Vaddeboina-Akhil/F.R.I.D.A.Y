"""
FRIDAY Autonomous Coding Agent
Generates complete projects using ChatGPT research + VS Code Copilot implementation.
"""

import subprocess
import time
import pyautogui
import pyperclip
import os
import webbrowser

from voice.tts import speak
from voice.stt import listen

# Constants
VSCODE_PATH = "C:\\Users\\akhil\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe"
CHATGPT_URL = "https://chatgpt.com"
CHROME_PATH = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"


def open_chatgpt_and_ask(prompt_text):
    """
    Open ChatGPT in Chrome, send prompt, and retrieve response.
    
    Args:
        prompt_text (str): The prompt to send to ChatGPT
        
    Returns:
        str: The response text from ChatGPT
    """
    # Open ChatGPT in Chrome with default profile
    subprocess.Popen([CHROME_PATH, "--profile-directory=Default", CHATGPT_URL])
    time.sleep(6)
    
    # Click on message input area (bottom center of ChatGPT)
    pyautogui.click(756, 650)
    time.sleep(1)
    
    # Type prompt using clipboard
    pyperclip.copy(prompt_text)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(0.5)
    
    # Send prompt
    pyautogui.press('enter')
    time.sleep(20)  # Wait for ChatGPT response
    
    # Copy response text
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.3)
    pyautogui.hotkey('ctrl', 'c')
    time.sleep(0.3)
    
    # Paste from clipboard
    response = pyperclip.paste()
    
    return response


def open_vscode_new_window():
    """
    Open a new VS Code window.
    
    Returns:
        bool: True if opened successfully
    """
    try:
        subprocess.Popen([VSCODE_PATH, "--new-window"])
        time.sleep(4)
        return True
    except Exception as e:
        print(f"Error opening VS Code: {e}")
        return False


def paste_to_copilot(prompt_text):
    """
    Open VS Code Copilot chat and paste prompt.
    
    Args:
        prompt_text (str): The prompt to send to Copilot
        
    Returns:
        bool: True if pasted successfully
    """
    try:
        # Try to open Copilot chat with Ctrl+Shift+I
        pyautogui.hotkey('ctrl', 'shift', 'i')
        time.sleep(2)
        
        # If that doesn't work, try Ctrl+I
        if not pyautogui.locateOnScreen:  # Simple fallback
            pyautogui.hotkey('ctrl', 'i')
            time.sleep(2)
        
        # Click on Copilot input area
        pyautogui.click(756, 650)
        time.sleep(1)
        
        # Type prompt
        pyperclip.copy(prompt_text)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.5)
        
        # Send prompt
        pyautogui.press('enter')
        
        return True
    except Exception as e:
        print(f"Error pasting to Copilot: {e}")
        return False


def run_coding_agent(idea):
    """
    Main coding agent: research with ChatGPT, implement with VS Code Copilot.
    
    Args:
        idea (str): The project idea to implement
        
    Returns:
        str: Completion message
    """
    speak("Interesting idea boss. Let me research this for you.")
    time.sleep(0.5)
    
    # Build research prompt for ChatGPT
    research_prompt = f"""I want to build: {idea}
    
Please provide:
1. Best approach and tech stack
2. Complete file structure
3. Full working code for each file
4. Step by step implementation

Make it production quality and complete."""
    
    speak("Opening ChatGPT to research your project boss.")
    response = open_chatgpt_and_ask(research_prompt)
    
    speak("Got the solution boss. Opening VS Code now.")
    open_vscode_new_window()
    
    speak("Pasting to Copilot to build your project boss.")
    
    # Build Copilot prompt with research findings
    copilot_prompt = f"""Build this complete project for me:

Project: {idea}

Research and solution:
{response[:2000] if response else 'Build a complete working ' + idea}

Create all necessary files with complete working code."""
    
    paste_to_copilot(copilot_prompt)
    
    return f"Project {idea} is being built in VS Code boss."


def coding_agent_flow(initial_command=""):
    """
    Main voice-triggered flow for the coding agent.
    
    Args:
        initial_command (str): The initial command from voice input
        
    Returns:
        str: Status message
    """
    # Extract project idea from command
    idea = initial_command
    
    # Remove common trigger words
    for word in ["build me", "create", "make", "develop", "build a", "build an"]:
        idea = idea.replace(word, "").strip()
    
    # If no idea extracted, ask for it
    if len(idea) < 3:
        speak("What do you want to build boss?")
        idea = listen()
        
        if not idea:
            return "Couldn't hear your idea boss."
    
    # Build the project
    speak(f"Building {idea} for you boss.")
    result = run_coding_agent(idea)
    
    return result
