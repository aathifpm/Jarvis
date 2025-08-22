import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent'

def generate_response(prompt, max_retries=3):
    headers = {
        'Content-Type': 'application/json'
    }
    
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "topK": 40,
            "topP": 0.95,
            "maxOutputTokens": 1024,
        }
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.post(
                f'{GEMINI_API_URL}?key={GEMINI_API_KEY}',
                headers=headers,
                data=json.dumps(data),
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                generated_text = result['candidates'][0]['content']['parts'][0]['text']
                return generated_text.strip()
            else:
                print(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {str(e)}")
        
    return "I'm sorry, I couldn't generate a response at this time."

def get_intent_and_entities(command):
    prompt = f"""
    Analyze the following command and provide the intent and entities in JSON format.
    Command: "{command}"
    
    Respond with a JSON object containing:
    1. "intent": The primary intent of the command (e.g., "time_date", "weather", "web_search", "task_management", "alarm", "system_control")
    2. "entities": A dictionary of relevant entities extracted from the command

    Example response:
    {{
        "intent": "weather",
        "entities": {{
            "location": "New York",
            "time": "tomorrow"
        }}
    }}
    """
    
    response = generate_response(prompt)
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        return {"intent": None, "entities": {}}

if __name__ == "__main__":
    # Test the function
    test_prompt = "Explain how AI works in one sentence."
    print(generate_response(test_prompt))
