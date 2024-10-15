from assistant.core import JarvisAssistant
from utils.config import DEBUG_MODE
import sys

def main():
    try:
        assistant = JarvisAssistant()
        
        # Optionally test the microphone if the function is available
        if hasattr(assistant.speech_handler, 'test_microphone'):
            if not assistant.speech_handler.test_microphone():
                print("Microphone test failed. Please check your microphone settings and try again.")
                return
        
        assistant.run()
    except KeyboardInterrupt:
        print("\nJarvis shutting down. Goodbye!")
    except PermissionError:
        print("Error: Insufficient permissions. Try running the program as an administrator.")
    except Exception as e:
        if DEBUG_MODE:
            raise
        else:
            print(f"An error occurred: {str(e)}")
            print("Please check your configuration and try again.")

if __name__ == "__main__":
    if sys.platform.startswith('win'):
        import ctypes
        if not ctypes.windll.shell32.IsUserAnAdmin():
            print("Warning: Some system control features may require administrator privileges.")
    main()
