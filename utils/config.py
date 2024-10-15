import os

# Speech recognition settings
OFFLINE_MODE = os.environ.get('JARVIS_OFFLINE_MODE', 'False').lower() == 'true'
LANGUAGE = os.environ.get('JARVIS_LANGUAGE', 'en-US')

# API keys
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

# Paths
MODEL_PATH = os.path.join('data', 'intent_model.pkl')
TASKS_FILE = os.path.join('data', 'tasks.json')

# System settings
DEBUG_MODE = os.environ.get('JARVIS_DEBUG', 'False').lower() == 'true'

