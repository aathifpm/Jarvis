import pyttsx3
from .nlp import GeminiAssistant
from .task_manager import TaskManager
import random
import threading
from utils.gemini_nlp import generate_response
from .speech import SpeechHandler
from .context_manager import ContextManager
from .proactive_assistant import ProactiveAssistant
from .user_profile import UserProfile
from utils.emotion_detector import detect_emotion
from utils.error_handler import handle_error
from datetime import datetime
from skills.calendar_integration import SimpleCalendar
from skills.weather import handle_weather
import requests

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
        self.context_manager = ContextManager()
        self.proactive_assistant = ProactiveAssistant(self)
        self.user_profile = UserProfile()
        self.calendar = SimpleCalendar()
        self.nlp = GeminiAssistant()

    def speak(self, text):
        self.speech_handler.speak(text)

    def listen(self):
        audio = self.speech_handler.listen()
        return self.speech_handler.recognize_speech(audio)

    @handle_error
    def process_command(self, command):
        response = self.handle_command(command)
        self.speak(response)

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

    def handle_calendar_commands(self, command):
        if "add event" in command.lower():
            # Parse the command to extract event details
            # This is a simple example and might need more robust parsing
            parts = command.split(" ", 3)
            if len(parts) == 4:
                _, _, date_str, title = parts
                try:
                    date_time = datetime.strptime(date_str, "%Y-%m-%d")
                    self.calendar.add_event(title, date_time)
                    return f"Event '{title}' added for {date_str}"
                except ValueError:
                    return "Sorry, I couldn't understand the date format. Please use YYYY-MM-DD."
            else:
                return "Sorry, I couldn't understand the event details."
        
        elif "upcoming events" in command.lower():
            events = self.calendar.get_upcoming_events()
            if events:
                response = "Your upcoming events are:\n"
                for event in events:
                    response += f"- {event['title']} on {event['date_time'].strftime('%Y-%m-%d')}\n"
                return response
            else:
                return "You have no upcoming events."
        
        elif "remove event" in command.lower():
            title = command.split("remove event", 1)[1].strip()
            self.calendar.remove_event(title)
            return f"Event '{title}' has been removed if it existed."
        
        else:
            return "Sorry, I didn't understand that calendar command."

    def run(self):
        self.speak("Hello, I'm Jarvis. How can I assist you?")
        while True:
            command = self.listen()
            if command is None:
                self.speak("I'm having trouble hearing you. Could you please check your microphone?")
                continue
            if command:
                if any(word in command.lower() for word in ["exit", "quit", "goodbye", "bye", "see you"]):
                    farewell_response = self.nlp.process_command(command)
                    self.speak(farewell_response)
                    self.speak("Shutting down. Goodbye!")
                    break
                elif command.lower() == "switch mode":
                    self.speech_handler.toggle_offline_mode()
                elif any(keyword in command.lower() for keyword in ["open", "launch", "start", "close", "exit", "quit", "system", "cpu", "memory", "disk", "process", "screenshot", "volume", "brightness", "wifi", "bluetooth", "airplane", "night light", "settings", "file explorer", "lock", "task view", "dark mode", "notification", "hotspot", "quick link", "run dialog", "game bar", "magnifier", "emoji"]):
                    response = self.handle_system_command(command)
                    self.speak(response)
                else:
                    self.process_command(command)
            else:
                self.speak("I didn't catch that. Could you please repeat?")

    def test_microphone(self):
        return self.speech_handler.test_microphone()

    def start(self):
        self.proactive_assistant.start()

    def set_user_name(self, name):
        self.nlp.user_name = name
        self.speak(f"Alright, I'll call you {name} from now on. I like it! It has a certain je ne sais quoi.")

    def handle_command(self, command):
        # Check for live transcription commands
        if any(phrase in command.lower() for phrase in ["transcribe", "transcription", "dictate"]):
            from skills.live_transcription import handle_live_transcription
            return handle_live_transcription(self, {"tokens": command.split()})
        
        # Check for WhatsApp commands
        if any(phrase in command.lower() for phrase in ["whatsapp", "message", "text"]):
            from skills.whatsapp_control import handle_whatsapp_control
            return handle_whatsapp_control(self, {"tokens": command.split()})
        
        # Existing command handling...
        if "weather" in command.lower():
            response = self.get_weather()
        elif "time" in command.lower():
            response = self.get_time()
        else:
            # Use the NLP model for intent recognition
            intent_data = self.nlp.process_command(command)
            response = intent_data

        return response

    def get_weather(self):
        try:
            # Get the current IP address
            ip_response = requests.get('https://api.ipify.org?format=json')
            ip_address = ip_response.json()['ip']

            # Get location based on IP
            location_response = requests.get(f'https://ipapi.co/{ip_address}/json/')
            location_data = location_response.json()
            city = location_data.get('city', 'Unknown')
            country = location_data.get('country_name', 'Unknown')

            # Get weather data
            base_url = f"https://wttr.in/{city}?format=j1"
            weather_response = requests.get(base_url)
            weather_data = weather_response.json()
            current = weather_data['current_condition'][0]
            temp = current['temp_C']
            description = current['weatherDesc'][0]['value']

            return f"Ah, the eternal battle against the elements! In {city}, {country}, it's currently {description} with a temperature of {temp}°C. Do you need a raincoat, or perhaps a sun umbrella? I'm here to help with all your existential weather woes."
        except Exception as e:
            return f"I'm sorry, I couldn't fetch the weather information. Error: {str(e)}"

    def get_time(self):
        current_time = datetime.now().strftime("%I:%M %p")
        return f"Ah, the age-old question of time! It's currently {current_time}. Time flies when you're having fun with an AI, doesn't it?"
