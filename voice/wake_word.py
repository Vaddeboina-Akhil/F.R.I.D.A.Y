import sounddevice
import numpy as np
import speech_recognition as sr
import tempfile
import os
from scipy.io import wavfile


WAKE_WORDS = ["friday", "edith", "hey friday", "hi friday", "okay friday", "ok friday"]


def listen_for_wake_word():
    """Listen for wake word in passive mode"""
    print("Listening for wake word...")
    
    while True:
        try:
            print("Recording 3 seconds...")
            
            # Record 3 seconds of audio
            audio = sounddevice.rec(int(3 * 16000), samplerate=16000, channels=1, dtype='int16')
            sounddevice.wait()
            
            # Create temp file
            temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            temp_path = temp_file.name
            temp_file.close()
            
            # Write audio to temp file
            wavfile.write(temp_path, 16000, audio)
            
            # Transcribe using Google Speech Recognition
            r = sr.Recognizer()
            with sr.AudioFile(temp_path) as source:
                audio_data = r.record(source)
            
            text = r.recognize_google(audio_data).lower()
            print(f"Heard: {text}")
            
            # Clean up temp file
            os.remove(temp_path)
            
            # Check for wake word
            if is_wake_word(text):
                return (True, text)
        
        except sr.UnknownValueError:
            print(".", end="", flush=True)
        
        except Exception as e:
            print(f"Wake word error: {e}")


def is_wake_word(text):
    """Check if text contains a wake word"""
    text = text.lower()
    return any(word in text for word in WAKE_WORDS)
