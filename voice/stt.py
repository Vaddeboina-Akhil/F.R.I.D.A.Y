import sounddevice
import scipy.io.wavfile
import speech_recognition as sr
import tempfile
import os


def listen():
    """Listen for voice input and recognize speech using sounddevice"""
    try:
        print("Listening...")
        
        # Record audio directly as int16
        audio_data = sounddevice.rec(int(5 * 16000), samplerate=16000, channels=1, dtype='int16')
        sounddevice.wait()
        
        # Save to temporary WAV file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
            tmp_path = tmp_file.name
        
        scipy.io.wavfile.write(tmp_path, 16000, audio_data)
        
        print("Recognizing...")
        
        # Read the WAV file and recognize
        recognizer = sr.Recognizer()
        with sr.AudioFile(tmp_path) as source:
            audio = recognizer.record(source)
        
        # Delete temporary file
        os.remove(tmp_path)
        
        # Recognize using Google
        text = recognizer.recognize_google(audio)
        return text.lower()
    
    except Exception:
        return None
