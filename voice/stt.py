import sounddevice
import scipy.io.wavfile
import speech_recognition as sr
import numpy
import tempfile
import os
import re

# ===== Audio Input Configuration =====
DEVICE_INDEX = 1
SAMPLE_RATE = 16000
DURATION = 7  # seconds


def listen():
    """
    Listen for voice input and recognize speech using noise-cancelling audio input.
    
    Uses ASUS AI Noise-cancelling Input (device 3) for better audio quality.
    Records 7 seconds of audio at 16kHz, processes with Google STT api,
    and applies regex-based fixes for common speech recognition errors.
    
    Returns:
        String containing recognized text, or None if recognition failed
    """
    try:
        print("Listening...")
        
        # STEP 1: Record audio from noise-cancelling device
        # duration=7s, 16kHz mono, 16-bit signed integer
        audio = sounddevice.rec(
            int(DURATION * SAMPLE_RATE),
            samplerate=SAMPLE_RATE,
            channels=1,
            dtype='int16',
            device=DEVICE_INDEX
        )
        sounddevice.wait()
        
        # STEP 2: Save to temporary WAV file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        scipy.io.wavfile.write(tmp_path, SAMPLE_RATE, audio)
        
        # STEP 3: Configure recognizer with noise filtering
        r = sr.Recognizer()
        r.energy_threshold = 200  # Noise threshold (lower = more sensitive)
        r.dynamic_energy_threshold = True  # Adapt to ambient noise
        
        # STEP 4: Load audio from file and record
        with sr.AudioFile(tmp_path) as source:
            audio_data = r.record(source)
        
        # STEP 5: Recognize using Google Speech-to-Text API
        text = r.recognize_google(audio_data)
        
        # STEP 6: Clean and prepare text
        os.remove(tmp_path)
        text = text.lower().strip()
        
        # STEP 7: Apply text replacements for common speech recognition errors
        text = text.replace("se rch", "search")
        text = text.replace("tutori ls", "tutorials")
        text = text.replace("tutori al", "tutorial")
        text = text.replace("you tube", "youtube")
        text = text.replace("fri day", "friday")
        text = text.replace("mr be st", "mrbeast")
        text = text.replace("mr beast", "mrbeast")
        text = text.replace("py thon", "python")
        text = text.replace("  ", " ").strip()
        
        print(f"Recognizing... {text}")
        return text
    
    except sr.UnknownValueError:
        # Google STT couldn't understand the audio
        return None
    
    except Exception as e:
        print(f"STT error: {e}")
        return None
