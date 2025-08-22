import pyautogui
import time
import cv2
import numpy as np
import pyperclip
from PIL import Image
import os
import webbrowser
import subprocess
import glob
import urllib.parse

class WhatsAppController:
    def __init__(self):
        self.is_open = False
        self.coordinates = {}
        self.calibrated = False
        
    def ensure_whatsapp_open(self):
        """Ensure WhatsApp is open before performing actions"""
        if not self.is_open:
            try:
                # Use only the desktop app method
                whatsapp_path = os.path.join(os.getenv('LOCALAPPDATA'), 'WhatsApp', 'WhatsApp.exe')
                if os.path.exists(whatsapp_path):
                    subprocess.Popen(whatsapp_path)
                    time.sleep(5)  # Wait for WhatsApp to open
                    self.is_open = True
                    return True
                else:
                    print("WhatsApp Desktop not found")
                    return False
            except Exception as e:
                print(f"Error opening WhatsApp: {str(e)}")
                return False
        return True

    def send_message(self, contact, message):
        """Send a message using WhatsApp Web"""
        if not self.ensure_whatsapp_open():
            return "Failed to open WhatsApp"
            
        try:
            # Use WhatsApp Web URL scheme for sending messages
            encoded_message = urllib.parse.quote(message)
            url = f'https://web.whatsapp.com/send?phone={contact}&text={encoded_message}'
            webbrowser.open(url)
            
            # Wait for page to load and auto-send
            time.sleep(10)  # Increased wait time for loading
            pyautogui.press('enter')
            
            return f"Message sent to {contact}"
        except Exception as e:
            return f"Error sending message: {str(e)}"

def handle_whatsapp_control(assistant, entities):
    """Handler function for WhatsApp commands"""
    controller = WhatsAppController()
    command = " ".join(entities.get("tokens", []))
    
    # Handle just open command
    if any(word in command for word in ["open", "launch", "start"]):
        if controller.ensure_whatsapp_open():
            return "Opening WhatsApp"
        return "Failed to open WhatsApp"
    
    # Handle message commands
    elif any(word in command for word in ["message", "send", "text"]):
        try:
            # Extract contact and message using various patterns
            if "saying" in command:
                parts = command.split("to", 1)[1].strip().split("saying", 1)
            elif "tell" in command:
                parts = command.split("tell", 1)[1].strip().split("whatsapp", 1)
            else:
                parts = command.split("message", 1)[1].strip().split(" ", 1)

            if len(parts) == 2:
                contact, message = parts
                return controller.send_message(contact.strip(), message.strip())
            return "Please specify both contact and message"
        except Exception as e:
            return f"Error parsing message command: {str(e)}"
    
    return "Unsupported WhatsApp command"
    