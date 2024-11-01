from utils.gemini_nlp import generate_response

def detect_emotion(text):
    prompt = f"Analyze the emotion in this text and respond with a single word (e.g., happy, sad, angry, neutral): '{text}'"
    return generate_response(prompt).strip().lower()