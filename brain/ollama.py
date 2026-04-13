import requests
import json
from memory.memory import get_cached_command, cache_command

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen2.5:3b"

conversation_history = []

SYSTEM_PROMPT = "You are FRIDAY, a highly intelligent AI assistant built for your boss. You talk like a real person - natural, warm, slightly witty. You are loyal, sharp, and occasionally sarcastic like the FRIDAY from Iron Man/Avengers. Rules: Reply in 1-2 sentences max. Never sound robotic. No bullet points. No lists. Talk conversationally like a human assistant would. Call the user 'boss' naturally but not every sentence. If asked something personal or funny, play along. If asked to do something, confirm it confidently. You are aware you are running locally on boss's machine."


def ask_brain(user_input):
    """Send a prompt to Ollama and get a response with conversation history"""
    try:
        # Check cache first
        cached = get_cached_command(user_input)
        if cached and cached.get("count", 0) > 2:
            print("Using cached response")
            return cached["response"]
        
        global conversation_history
        
        # Add user message to history
        conversation_history.append({"role": "user", "content": user_input})
        
        # Build full prompt from last 6 messages
        recent_messages = conversation_history[-6:]
        full_prompt = ""
        for msg in recent_messages:
            if msg["role"] == "user":
                full_prompt += f"User: {msg['content']}\n"
            else:
                full_prompt += f"FRIDAY: {msg['content']}\n"
        
        # Add prompt for assistant to continue
        final_prompt = full_prompt + "FRIDAY:"
        
        # Create payload with options
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": final_prompt,
            "system": SYSTEM_PROMPT,
            "stream": False,
            "options": {
                "num_predict": 120,
                "temperature": 0.8,
                "top_p": 0.9,
                "stop": ["\nUser:", "\nBoss:"]
            }
        }
        
        # Make request to Ollama
        response = requests.post(OLLAMA_URL, json=payload, timeout=20)
        response.raise_for_status()
        
        # Extract and clean response
        response_text = response.json()["response"].strip()
        
        # Cache the response
        cache_command(user_input, "ask_brain", response_text)
        
        # Add assistant message to history
        conversation_history.append({"role": "assistant", "content": response_text})
        
        # Keep only last 10 messages
        if len(conversation_history) > 10:
            conversation_history = conversation_history[-10:]
        
        return response_text
    
    except Exception as e:
        print(f"Error asking brain: {e}")
        return "Sorry boss, I had an error."


def correct_command(text):
    """Correct speech recognition errors in voice commands using Ollama"""
    try:
        prompt = f"""You are a speech correction AI. The user spoke a voice command but speech recognition made errors.
Fix ONLY spelling/recognition mistakes. Keep the meaning exactly same.
Common mistakes: "melt"→"mail", "cloud"→"claude", "good"→"google", "sent"→"send"
Return ONLY the corrected command, nothing else, no explanation.
Original command: "{text}"
Corrected command:"""
        
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"num_predict": 20, "temperature": 0.1}
        }
        
        response = requests.post(OLLAMA_URL, json=payload, timeout=10)
        response.raise_for_status()
        
        return response.json()["response"].strip()
    
    except Exception as e:
        print(f"Error correcting command: {e}")
        return text


def decide_action(user_input):
    """
    Use AI to intelligently decide which action to take for ambiguous commands.
    Smart fallback for command parser when uncertain.
    
    Args:
        user_input (str): User's voice command
    
    Returns:
        dict: {"action": action_name, "target": target_value}
    """
    try:
        TOOLS_PROMPT = """You are FRIDAY's action router. Given a voice command, decide which action to take.

Available actions:
- open_app: open any application (chrome, brave, spotify, discord, whatsapp, notepad, calculator, vs code, file explorer)
- open_url: open a website (youtube, github, netflix, instagram, claude, chatgpt, gmail, google)
- search_youtube: search for videos, music, songs, tutorials, gameplay
- search_google: search for news, scores, weather, prices, facts
- get_time: get current time
- get_date: get current date
- get_battery: check battery level
- take_screenshot: take screenshot
- world_briefing: world news briefing
- india_briefing: india news
- whatsapp_flow: send whatsapp message
- email_flow: send email
- scroll_down: scroll down
- scroll_up: scroll up
- open_world_monitor: open world monitor map
- shutdown_pc: shutdown computer
- restart_pc: restart computer
- ask_brain: general conversation or unknown command

Rules:
- Return ONLY a JSON object like: {{"action": "open_app", "target": "chrome"}}
- For open_app: target = app name
- For open_url: target = website name
- For search_youtube/search_google: target = search query
- For email_flow: target = "to college account" or "to personal account" or original text
- For ask_brain: target = original text
- No explanation, just JSON

Command: "{command}"
JSON:"""
        
        prompt = TOOLS_PROMPT.format(command=user_input)
        
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"num_predict": 30, "temperature": 0.1}
        }
        
        response = requests.post(OLLAMA_URL, json=payload, timeout=10)
        response.raise_for_status()
        
        # Extract response text
        text = response.json()["response"].strip()
        
        # Clean markdown code blocks if present
        text = text.replace("```json", "").replace("```", "").strip()
        
        # Parse JSON
        result = json.loads(text)
        return result
    
    except Exception as e:
        print(f"Error in decide_action: {e}")
        # Fallback to ask_brain
        return {"action": "ask_brain", "target": user_input}


def is_ollama_running():
    """Check if Ollama service is running"""
    try:
        response = requests.get("http://localhost:11434")
        return response.status_code == 200
    except Exception:
        return False


def clear_history():
    """Clear conversation history"""
    global conversation_history
    conversation_history.clear()
