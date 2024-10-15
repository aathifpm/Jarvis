import pyttsx3
from .nlp import process_command
from .task_manager import TaskManager
import random
import threading
from utils.gemini_nlp import generate_response
from .speech import SpeechHandler

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    print("Speech recognition is not available. Running in text-only mode.")
    SPEECH_RECOGNITION_AVAILABLE = False

class JarvisAssistant:
    def __init__(self):
        self.speech_handler = SpeechHandler()
        self.task_manager = TaskManager()
        if SPEECH_RECOGNITION_AVAILABLE:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()

    def speak(self, text):
        self.speech_handler.speak(text)

    def listen(self):
        audio = self.speech_handler.listen()
        return self.speech_handler.recognize_speech(audio)

    def execute_command(self, command):
        intent, entities = process_command(command)
        if intent:
            response = intent(self, entities)
            self.speak(response)
        else:
            # Use Gemini API as a fallback
            prompt = f"""
            You are JARVIS, an AI assistant. Respond to the following user query in a helpful and concise manner:
            User: {command}
            JARVIS:
            """
            ai_response = generate_response(prompt)
            self.speak(f"I don't have a specific action for that, but here's what I can tell you: {ai_response}")

    def greet(self):
        greetings = [
            "Hey there! I'm Jarvis, ready to assist you.",
            "Hello! Jarvis at your service.",
            "Hi buddy! Jarvis here, what can I do for you?",
            "Greetings! Jarvis online and ready to help.",
            "Hey! Jarvis activated and awaiting your command."
        ]
        self.speak(random.choice(greetings))

    def handle_system_command(self, command):
        from skills.system_control import handle_system_control
        response = handle_system_control(self, {"tokens": command.split()})
        self.speak(response)

    def run(self):
        self.speak("Hello, I'm Jarvis. How can I assist you?")
        while True:
            command = self.listen()
            if command is None:
                self.speak("I'm having trouble hearing you. Could you please check your microphone?")
                continue
            if command:
                if command.lower() in ["exit", "quit", "goodbye"]:
                    self.speak("Goodbye!")
                    break
                elif command.lower() == "switch mode":
                    self.speech_handler.toggle_offline_mode()
                elif any(keyword in command.lower() for keyword in ["open", "launch", "close", "exit", "system", "cpu", "memory", "disk"]):
                    self.handle_system_command(command)
                else:
                    self.execute_command(command)
            else:
                self.speak("I didn't catch that. Could you please repeat?")

    def test_microphone(self):
        return self.speech_handler.test_microphone()
