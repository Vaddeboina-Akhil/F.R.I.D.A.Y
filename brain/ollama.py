import requests
import json
from memory.learning import get_cached_command, cache_command

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
                "num_predict": 80,
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
