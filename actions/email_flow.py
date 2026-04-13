import time
import os
import pyautogui
import pyperclip
from voice.tts import speak
from voice.stt import listen
from actions.email_automation import open_gmail_personal, open_gmail_college


# Gmail account credentials
PERSONAL_EMAIL = "akhilvaddeboina25@gmail.com"
COLLEGE_EMAIL = "23p61a05m5@vbithyd.ac.in"


def ask(question):
    """
    Ask a question and get voice response from user.
    With retry logic - asks twice if user doesn't respond.
    
    Args:
        question (str): Question to ask
    
    Returns:
        str: User's response (lowercased, stripped) or empty string
    """
    speak(question)
    time.sleep(0.5)
    
    response = listen()
    
    # If no response, retry once
    if not response:
        print(f"[DEBUG] No response to: {question}, retrying...")
        speak("Say that again boss.")
        time.sleep(0.3)
        response = listen()
    
    if response is None:
        return ""
    
    return response.lower().strip()


def is_cancellation(response):
    """
    Check if the response indicates cancellation.
    
    Args:
        response (str): User's response
    
    Returns:
        bool: True if cancellation detected
    """
    cancel_words = ["forget", "cancel", "stop", "never mind", "abort", "quit", "exit"]
    return any(word in response.lower() for word in cancel_words)


def run_email_flow(initial_command=""):
    """
    Run complete conversational email flow with 8-step process.
    
    Args:
        initial_command (str): Initial command that triggered email flow
    
    Returns:
        str: Result message
    """
    try:
        from_account = None
        to_email = None
        subject = None
        body = None
        
        # ===== STEP 1: Determine FROM account and TO email =====
        initial_lower = initial_command.lower()
        
        # Check for "send to personal" - user wants to RECEIVE in personal
        if "send to personal" in initial_lower or "to personal account" in initial_lower or "personal mail" in initial_lower or "personal account" in initial_lower:
            from_account = "college"  # sending FROM college TO personal
            to_email = PERSONAL_EMAIL
            speak("Opening your college Gmail to send to your personal Gmail boss.")
        
        # Check for "send to college" - user wants to RECEIVE in college
        elif "send to college" in initial_lower or "to college account" in initial_lower or "college mail" in initial_lower or "college account" in initial_lower:
            from_account = "personal"  # sending FROM personal TO college
            to_email = COLLEGE_EMAIL
            speak("Opening your personal Gmail to send to your college account boss.")
        
        else:
            # Fallback: ask which account to send from
            ans = ask("Should I send from personal or college account boss?")
            if is_cancellation(ans):
                speak("Email cancelled boss.")
                return "Email cancelled."
            if "college" in ans:
                from_account = "college"
                to_email = PERSONAL_EMAIL
            else:
                from_account = "personal"
                to_email = COLLEGE_EMAIL
        
        # ===== STEP 2: Open Gmail immediately =====
        if from_account == "personal":
            open_gmail_personal()
        else:
            open_gmail_college()
        
        time.sleep(2)
        
        # ===== STEP 3: Type to_email in compose field =====
        pyautogui.click(1100, 368)  # Click To field
        time.sleep(0.5)
        pyperclip.copy(to_email)
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press('tab')
        time.sleep(0.3)
        
        # ===== STEP 4: Ask subject =====
        subject = ask("What's the subject boss?")
        if is_cancellation(subject):
            speak("Email cancelled boss.")
            return "Email cancelled."
        if not subject or len(subject) < 2:
            subject = "Message from FRIDAY"
        pyperclip.copy(subject)
        pyautogui.hotkey('ctrl', 'v')
        pyautogui.press('tab')
        time.sleep(0.3)
        
        # ===== STEP 5: Ask body =====
        body = ask("What should I write boss?")
        if is_cancellation(body):
            speak("Email cancelled boss.")
            return "Email cancelled."
        if not body or len(body) < 2:
            body = "Sent via FRIDAY."
        pyperclip.copy(body)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.3)
        
        # ===== STEP 6: Ask files =====
        ans = ask("Any files to attach boss? Say yes or no.")
        if is_cancellation(ans):
            speak("Email cancelled boss.")
            return "Email cancelled."
        if "yes" in ans:
            file_name = ask("What is the file name boss?")
            if is_cancellation(file_name):
                speak("Email cancelled boss.")
                return "Email cancelled."
            speak(f"I'll look for {file_name} boss.")
            
            for folder in ["Desktop", "Downloads", "Documents"]:
                path = f"C:\\Users\\akhil\\{folder}\\{file_name}"
                if os.path.exists(path):
                    pyautogui.hotkey('ctrl', 'shift', 'a')  # Gmail attach hotkey
                    time.sleep(2)
                    pyperclip.copy(path)
                    pyautogui.hotkey('ctrl', 'v')
                    pyautogui.press('enter')
                    time.sleep(2)
                    break
        
        # ===== STEP 7: Send =====
        speak("Sending now boss.")
        pyautogui.hotkey('ctrl', 'enter')
        time.sleep(1)
        
        return "Email sent boss."
    
    except Exception as e:
        error_msg = f"Email error boss: {str(e)}"
        speak(error_msg)
        return error_msg

