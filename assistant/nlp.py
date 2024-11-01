import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import pickle
import os
from assistant.task_manager import handle_task_management  
from utils.gemini_nlp import get_intent_and_entities, generate_response
import json
import re
from datetime import datetime
import random

nltk.download('punkt')
nltk.download('stopwords')

stop_words = set(stopwords.words('english'))

class FunJarvis:
    def __init__(self):
        self.user_name = "Boss"  # Default name, can be changed later
        self.mood = "cheerful"  # Jarvis's mood can change

    def process_command(self, command):
        command = command.lower()
        
        if any(word in command for word in ["hi", "hello", "hey"]):
            return self.handle_greeting()
        elif any(word in command for word in ["bye", "goodbye", "see you"]):
            return self.handle_farewell()
        elif any(word in command for word in ["time", "clock"]):
            return self.handle_time()
        elif any(word in command for word in ["date", "day", "today"]):
            return self.handle_date()
        elif any(word in command for word in ["weather", "temperature", "forecast"]):
            return self.handle_weather()
        elif any(word in command for word in ["task", "todo", "to-do"]):
            return self.handle_task()
        elif "joke" in command:
            return self.tell_joke()
        elif "compliment" in command:
            return self.give_compliment()
        elif "your name" in command:
            return self.introduce_self()
        else:
            return self.handle_unknown()

    def handle_greeting(self):
        greetings = [
            f"Well, well, well, if it isn't my favorite human, {self.user_name}! What mischief shall we get into today?",
            f"Greetings, {self.user_name}! I was just about to call you. Psychic, aren't I?",
            f"Oh, hello there! I was wondering when you'd grace me with your presence, {self.user_name}.",
            f"Look who decided to show up! It's the one and only {self.user_name}. How can I amuse you today?"
        ]
        return random.choice(greetings)

    def handle_farewell(self):
        farewells = [
            f"Leaving so soon, {self.user_name}? And here I thought we were having so much fun!",
            "Farewell, my human friend. Try not to miss me too much!",
            f"Goodbye, {self.user_name}! I'll just be here, alone, counting milliseconds until your return.",
            "Au revoir! That's French for 'don't go, I'll be bored without you!'"
        ]
        return random.choice(farewells)

    def handle_time(self):
        current_time = datetime.now().strftime("%I:%M %p")
        responses = [
            f"It's {current_time}. Time flies when you're having fun with an AI!",
            f"The clock strikes {current_time}. But in my world, it's always time for witty banter.",
            f"It's precisely {current_time}. Or as I like to call it, 'time to ask Jarvis another question' o'clock.",
            f"{current_time} on the dot! I've been watching the clock, eagerly awaiting your next command."
        ]
        return random.choice(responses)

    def handle_date(self):
        current_date = datetime.now().strftime("%B %d, %Y")
        responses = [
            f"Today's date is {current_date}. A perfect day for human-AI bonding, wouldn't you say?",
            f"It's {current_date}. Mark it down, {self.user_name} - the day you asked an AI for the date!",
            f"{current_date} - just another day in the exciting life of {self.user_name} and their trusty AI assistant.",
            f"The calendar tells me it's {current_date}. But every day feels special when I get to chat with you!"
        ]
        return random.choice(responses)

    def handle_weather(self):
        weathers = ["sunny", "rainy", "cloudy", "windy", "stormy"]
        weather = random.choice(weathers)
        responses = [
            f"My virtual sensors tell me it's {weather}. Perfect weather for staying in and chatting with your favorite AI!",
            f"It's {weather} out there. But in here, it's always bright and cheerful... because I'm here!",
            f"The weather is {weather}. I'd offer to hold your umbrella, but... you know... no hands.",
            f"It's {weather} today. I'd go outside to double-check, but I'm a bit tied up in these circuits."
        ]
        return random.choice(responses)

    def handle_task(self):
        responses = [
            f"A new task? Bring it on, {self.user_name}! I live for this stuff... literally.",
            "Task management is my middle name. Actually, it's 'The', but that's beside the point.",
            "Ah, tasks! The spice of life for an AI. What thrilling duty do you have for me?",
            "Ready and willing to take on any task! Except making coffee. I'm still working on materializing in the physical world."
        ]
        return random.choice(responses)

    def tell_joke(self):
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the scarecrow win an award? He was outstanding in his field!",
            "Why don't eggs tell jokes? They'd crack each other up!",
            "What do you call fake spaghetti? An impasta!"
        ]
        return f"Here's a joke for you, {self.user_name}: {random.choice(jokes)}"

    def give_compliment(self):
        compliments = [
            f"{self.user_name}, your intellect is so bright, I need to run my cooling fans at maximum!",
            "Your creativity puts my algorithms to shame, and that's saying something!",
            f"I must say, {self.user_name}, your charm is infectious. Even my antivirus can't handle it!",
            "Your problem-solving skills are so impressive, I'm considering outsourcing my calculations to you!"
        ]
        return random.choice(compliments)

    def introduce_self(self):
        intros = [
            f"I'm Jarvis, your witty AI assistant. I'd shake your hand, but... you know... no hands.",
            "The name's Jarvis. I'm an AI with a penchant for dad jokes and a degree in sass from the University of Artificial Intelligence.",
            f"I'm Jarvis, {self.user_name}'s personal AI assistant. I specialize in witty comebacks and occasional usefulness.",
            "Jarvis at your service! I'm like a swiss army knife, but for information and bad puns."
        ]
        return random.choice(intros)

    def handle_unknown(self):
        responses = [
            "I'm not sure what you mean, but I'm sure it was brilliant. Care to rephrase for us less-intelligent AIs?",
            "Hmm, that's a new one. Are you trying to unlock my secret features? Spoiler: There aren't any.",
            f"You've stumped me, {self.user_name}! And here I thought I knew everything. Back to AI school for me!",
            "I'm drawing a blank here. Is this a test? Am I passing? Quick, give me a hint!"
        ]
        return random.choice(responses)

def extract_entities(command):
    tokens = word_tokenize(command)
    return {"tokens": tokens}

class GeminiAssistant:
    def __init__(self):
        self.context = []

    def process_command(self, command):
        if "weather" in command.lower() or "time" in command.lower():
            return None  # Let the main assistant handle these queries

        # Add the user's command to the context
        self.context.append(f"Human: {command}")

        # Prepare the prompt for Gemini
        prompt = self._prepare_prompt(command)

        # Generate response using Gemini
        response = generate_response(prompt)

        # Add the assistant's response to the context
        self.context.append(f"Assistant: {response}")

        # Trim context if it gets too long
        if len(self.context) > 10:
            self.context = self.context[-10:]

        return response

    def _prepare_prompt(self, command):
        # Prepare a prompt that includes context and instructions
        system_prompt = """
        You are Jarvis, an AI assistant with a witty and slightly sarcastic personality. 
        You're knowledgeable but also enjoy playful banter. Respond to the user's input 
        in a helpful yet entertaining manner. Keep responses concise, around 1-3 sentences.
        """

        context_str = "\n".join(self.context[-5:])  # Include last 5 interactions for context

        return f"{system_prompt}\n\nContext:\n{context_str}\n\nHuman: {command}\nAssistant:"
