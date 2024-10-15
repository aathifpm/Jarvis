import os
import speech_recognition as sr
import pyttsx3
from pocketsphinx import LiveSpeech
import gtts
import playsound
import tempfile

class SpeechHandler:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.engine = pyttsx3.init()
        self.offline_mode = False
        self.voices = self.engine.getProperty('voices')
        self.set_voice(1)  # Default to a female voice (index may vary)
        self.set_rate(180)  # Default speech rate
        self.set_volume(0.8)  # Default volume
        self.use_online_tts =False   # Flag to switch between offline and online TTS

    def set_voice(self, voice_index):
        if 0 <= voice_index < len(self.voices):
            self.engine.setProperty('voice', self.voices[voice_index].id)
        else:
            print(f"Invalid voice index. Using default voice.")

    def set_rate(self, rate):
        self.engine.setProperty('rate', rate)

    def set_volume(self, volume):
        self.engine.setProperty('volume', volume)

    def toggle_offline_mode(self):
        self.offline_mode = not self.offline_mode
        mode = "offline" if self.offline_mode else "online"
        print(f"Switched to {mode} mode")
        self.speak(f"Switched to {mode} mode")

    def toggle_tts_mode(self):
        self.use_online_tts = not self.use_online_tts
        mode = "online" if self.use_online_tts else "offline"
        print(f"Switched to {mode} TTS mode")

    def speak(self, text):
        print(f"JARVIS: {text}")
        
        if self.use_online_tts:
            self._speak_online(text)
        else:
            self._speak_offline(text)

    def _speak_offline(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

    def _speak_online(self, text):
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as tf:
            tts = gtts.gTTS(text=text, lang='en')
            tts.save(tf.name)
            playsound.playsound(tf.name)
        os.unlink(tf.name)

    def listen(self):
        with self.microphone as source:
            print("Listening...")
            try:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("Ambient noise adjustment complete.")
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                print("Audio captured successfully.")
                return audio
            except sr.WaitTimeoutError:
                print("Listening timed out. No speech detected.")
                return None

    def recognize_speech(self, audio):
        if audio is None:
            return ""
        try:
            if not self.offline_mode:
                print("Using Google Speech Recognition...")
                text = self.recognizer.recognize_google(audio)
            else:
                print("Using Sphinx (offline) Speech Recognition...")
                text = self.recognizer.recognize_sphinx(audio)
            print(f"Recognition result: {text}")
            return text.lower()
        except sr.UnknownValueError:
            print("Speech recognition could not understand the audio")
            return ""
        except sr.RequestError as e:
            print(f"Could not request results from speech recognition service; {e}")
            return ""

def offline_recognize_continuous():
    for phrase in LiveSpeech():
        yield str(phrase)

def test_microphone():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Testing microphone...")
        try:
            print("Adjusting for ambient noise. Please remain silent.")
            r.adjust_for_ambient_noise(source, duration=2)
            print("Ambient noise adjustment complete.")
            print("Please speak a test phrase...")
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
            print("Audio captured successfully.")
            try:
                text = r.recognize_google(audio)
                print(f"Test successful. Recognized: {text}")
                return True
            except sr.UnknownValueError:
                print("Test failed. Speech was unintelligible.")
                return False
            except sr.RequestError as e:
                print(f"Test failed. Could not request results from Google Speech Recognition service; {e}")
                return False
        except sr.WaitTimeoutError:
            print("Test failed. No speech detected within the timeout period.")
            return False

def test_speech_output():
    speech_handler = SpeechHandler()
    
    print("Testing offline TTS...")
    speech_handler.speak("This is a test of the offline text-to-speech system.")
    
    print("\nTesting online TTS...")
    speech_handler.toggle_tts_mode()
    speech_handler.speak("This is a test of the online text-to-speech system.")
    
    print("\nTesting voice change...")
    speech_handler.set_voice(0)  # Change to a different voice (index may vary)
    speech_handler.speak("The voice has been changed. How does it sound?")
    
    print("\nTesting speech rate change...")
    speech_handler.set_rate(150)  # Slower rate
    speech_handler.speak("The speech rate has been slowed down.")
    
    print("\nTesting volume change...")
    speech_handler.set_volume(0.5)  # Lower volume
    speech_handler.speak("The volume has been lowered.")

if __name__ == "__main__":
    test_speech_output()
