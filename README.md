# Jarvis AI Assistant

Jarvis is an intelligent personal assistant with voice interaction capabilities and system control features. It combines natural language processing, speech recognition, and various skills to help automate tasks and provide information.

## Features

- **Voice Interaction**: Natural speech recognition and text-to-speech capabilities
- **System Control**: Manage system settings, applications, and hardware
- **Task Management**: Create and manage to-do lists and reminders  
- **Live Transcription**: Real-time speech-to-text with saving/sharing options
- **Calendar Integration**: Track events and appointments
- **WhatsApp Control**: Send messages and interact with WhatsApp
- **Web Search**: Look up information online
- **Weather Updates**: Get current weather conditions
- **Proactive Assistance**: Smart notifications and reminders

## Requirements

See requirements.txt for full list of dependencies. Key requirements:

- Python 3.8+
- Speech Recognition
- pyttsx3
- PyAutoGUI
- Google Cloud Speech API (optional)
- Various system control libraries

## Installation

1. Clone the repository
2. Install requirements:

```bash
pip install -r requirements.txt
```

3. Set up environment variables:
   - GEMINI_API_KEY: For enhanced NLP capabilities
   - JARVIS_OFFLINE_MODE: Set to "true" for offline operation
   - JARVIS_DEBUG: Set to "true" for debug logging

## Usage

Run the main script to start Jarvis:

```bash
python main.py
```

Basic voice commands:
- "What time is it?" - Get current time
- "What's the weather?" - Get weather update
- "Open [application]" - Launch applications
- "Add task [description]" - Create new task
- "Start transcription" - Begin live transcription
- "Send WhatsApp message" - Control WhatsApp

## Project Structure

- assistant/ - Core assistant functionality
- skills/ - Individual skill modules
- utils/ - Utility functions and helpers
- data/ - Data storage and configurations

## Contributing

Contributions welcome! Please feel free to submit pull requests.

## License

This project is licensed under the MIT License - see LICENSE file for details.