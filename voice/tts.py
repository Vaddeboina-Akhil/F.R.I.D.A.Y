import edge_tts
import asyncio
import tempfile
import os
import threading
from playsound import playsound


async def _speak_async(text):
    """Async function to generate and play speech using edge-tts and playsound"""
    try:
        # Create temp mp3 file
        tmp_file = tempfile.NamedTemporaryFile(suffix='.mp3', delete=False)
        tmp_path = tmp_file.name
        tmp_file.close()
        
        # Create Communicate object with British female voice and faster speech
        communicate = edge_tts.Communicate(text, voice="en-GB-SoniaNeural", rate="+15%")
        
        # Save the audio to the temp file
        await communicate.save(tmp_path)
        
        # Play the audio file
        playsound(tmp_path)
        
        # Delete temporary file
        try:
            os.remove(tmp_path)
        except Exception:
            pass
    
    except Exception:
        pass


def speak(text):
    """Speak the given text using FRIDAY voice synchronously"""
    try:
        asyncio.run(_speak_async(text))
    except Exception:
        pass


def speak_background(text):
    """Speak the given text using FRIDAY voice in a background thread"""
    try:
        def run_async():
            asyncio.run(_speak_async(text))
        
        thread = threading.Thread(target=run_async, daemon=True)
        thread.start()
    except Exception:
        pass


def speak_streaming(text):
    """Speak the full text without any character limit"""
    try:
        asyncio.run(_speak_async(text))
    except Exception:
        pass
