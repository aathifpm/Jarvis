import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import pickle
import os
from assistant.task_manager import handle_task_management  # Add this import
from utils.gemini_nlp import generate_response, get_intent_and_entities
import json

nltk.download('punkt')
nltk.download('stopwords')

stop_words = set(stopwords.words('english'))

class IntentClassifier:
    def __init__(self):
        self.intents = ['time_date', 'system_control', 'weather', 'web_search', 'task_management', 'alarm']
        self.fallback_classifier = MultinomialNB()
        self.vectorizer = CountVectorizer()
        self.model_file = 'data/intent_model.pkl'
        
        if os.path.exists(self.model_file):
            with open(self.model_file, 'rb') as f:
                self.vectorizer, self.fallback_classifier = pickle.load(f)
        else:
            self.train_fallback_model()

    def train_fallback_model(self):
        training_data = [
            ("what time is it", "time_date"),
            ("tell me the date", "time_date"),
            ("open notepad", "system_control"),
            ("launch brave", "system_control"),
            ("close chrome", "system_control"),
            ("exit firefox", "system_control"),
            ("show system info", "system_control"),
            ("what's the cpu usage", "system_control"),
            ("tell me the memory usage", "system_control"),
            ("how much disk space is left", "system_control"),
            ("what's the weather like", "weather"),
            ("is it going to rain today", "weather"),
            ("search for restaurants nearby", "web_search"),
            ("google artificial intelligence", "web_search"),
            ("add a new task", "task_management"),
            ("show me my to-do list", "task_management"),
            ("set an alarm for 7 AM", "alarm"),
            ("wake me up at 6:30 PM", "alarm"),
            ("set alarm for 7 AM", "alarm"),
            ("set alarm for 3:30 PM for meeting", "alarm"),
            ("remove alarm 2", "alarm"),
            ("list alarms", "alarm"),
            ("toggle alarm 1", "alarm"),
        ]
        
        X = [self.preprocess(x[0]) for x in training_data]
        y = [x[1] for x in training_data]
        
        X = self.vectorizer.fit_transform(X)
        self.fallback_classifier.fit(X, y)
        
        with open(self.model_file, 'wb') as f:
            pickle.dump((self.vectorizer, self.fallback_classifier), f)

    def predict(self, text):
        # Use Gemini API for intent classification
        prompt = f"Classify the following text into one of these intents: {', '.join(self.intents)}. Only respond with the intent name.\n\nText: {text}"
        gemini_intent = generate_response(prompt).strip().lower()
        
        if gemini_intent in self.intents:
            return gemini_intent
        else:
            # Fallback to the existing method if Gemini API fails or returns an unknown intent
            return self.fallback_predict(text)

    def fallback_predict(self, text):
        text = self.preprocess(text)
        X = self.vectorizer.transform([text])
        intent = self.fallback_classifier.predict(X)[0]
        return intent

    def preprocess(self, text):
        tokens = word_tokenize(text.lower())
        return ' '.join([t for t in tokens if t not in stop_words])

intent_classifier = IntentClassifier()

def process_command(command):
    intent = intent_classifier.predict(command)
    entities = extract_entities(command)
    
    if intent == 'time_date':
        from skills.time_date import handle_time_date
        return handle_time_date, entities
    elif intent == 'system_control':
        from skills.system_control import handle_system_control
        return handle_system_control, entities
    elif intent == 'weather':
        from skills.weather import handle_weather
        return handle_weather, entities
    elif intent == 'web_search':
        from skills.web_search import handle_web_search
        return handle_web_search, entities
    elif intent == 'task_management':
        return handle_task_management, entities
    elif intent == 'alarm':
        from skills.alarm import handle_alarm
        return handle_alarm, entities
    else:
        return None, {}

def extract_entities(command):
    tokens = word_tokenize(command)
    return {"tokens": tokens}
