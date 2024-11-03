import pyautogui
import time
import cv2
import numpy as np
import pyperclip
from PIL import Image
import os
import webbrowser

class WhatsAppController:
    def __init__(self):
        self.is_open = False
        self.coordinates = {}
        self.calibrated = False
        
        # Load reference images for UI elements
        self.ref_images = self.load_reference_images()

    def load_reference_images(self):
        """Load reference images for UI elements"""
        ref_dir = os.path.join(os.path.dirname(__file__), 'whatsapp_refs')
        if not os.path.exists(ref_dir):
            os.makedirs(ref_dir)
            
        # You'll need to save these reference images in the whatsapp_refs directory
        ref_images = {
            'search_box': 'search_icon.png',
            'attach_button': 'attach_icon.png',
            'message_box': 'message_box.png',
            'send_button': 'send_button.png'
        }
        
        loaded_refs = {}
        for key, filename in ref_images.items():
            path = os.path.join(ref_dir, filename)
            if os.path.exists(path):
                loaded_refs[key] = cv2.imread(path)
        
        return loaded_refs

    def find_element_on_screen(self, template_name, confidence=0.8):
        """Find UI element on screen using template matching"""
        if template_name not in self.ref_images:
            return None

        # Take screenshot
        screenshot = pyautogui.screenshot()
        screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        
        # Get template
        template = self.ref_images[template_name]
        
        # Template matching
        result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= confidence:
            return (max_loc[0] + template.shape[1]//2, 
                   max_loc[1] + template.shape[0]//2)
        return None

    def calibrate(self):
        """Auto-calibrate by finding UI elements"""
        print("Starting WhatsApp calibration...")
        
        # Ensure WhatsApp is open
        self.ensure_whatsapp_open()
        time.sleep(2)
        
        # Find each UI element
        elements_to_find = ['search_box', 'attach_button', 'message_box', 'send_button']
        
        for element in elements_to_find:
            print(f"Looking for {element}...")
            coords = self.find_element_on_screen(element)
            if coords:
                self.coordinates[element] = coords
                print(f"Found {element} at {coords}")
            else:
                print(f"Could not find {element}")
        
        # Derive other coordinates based on found elements
        if 'message_box' in self.coordinates:
            msg_box = self.coordinates['message_box']
            self.coordinates['last_message'] = (msg_box[0], msg_box[1] - 100)
        
        self.calibrated = bool(self.coordinates)
        return self.calibrated

    def ensure_calibrated(self):
        """Ensure WhatsApp is calibrated"""
        if not self.calibrated:
            return self.calibrate()
        return True

    def click_element(self, element_name, offset_x=0, offset_y=0):
        """Click a UI element with optional offset"""
        if not self.ensure_calibrated():
            return False
            
        if element_name in self.coordinates:
            coords = self.coordinates[element_name]
            pyautogui.click(coords[0] + offset_x, coords[1] + offset_y)
            return True
        return False

    def send_message(self, contact_name, message):
        """Send a message with auto-calibration"""
        if not self.ensure_calibrated():
            return "Calibration failed"

        try:
            # Search contact
            self.click_element('search_box')
            time.sleep(0.5)
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.press('backspace')
            pyautogui.write(contact_name)
            time.sleep(1)

            # Click first contact (offset from search box)
            self.click_element('search_box', offset_y=60)
            time.sleep(1)

            # Type and send message
            self.click_element('message_box')
            time.sleep(0.5)
            pyautogui.write(message)
            pyautogui.press('enter')
            
            return f"Message sent to {contact_name}"
            
        except Exception as e:
            return f"Error sending message: {str(e)}"

    def read_last_messages(self, count=5):
        """Read messages with auto-calibration"""
        if not self.ensure_calibrated():
            return "Calibration failed"

        try:
            # Click message area
            self.click_element('last_message')
            time.sleep(0.5)
            
            # Select and copy text
            pyautogui.hotkey('ctrl', 'a')
            time.sleep(0.5)
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(0.5)
            
            # Process messages
            messages = pyperclip.paste()
            message_lines = [line.strip() for line in messages.split('\n') if line.strip()]
            
            # Deselect
            pyautogui.press('esc')
            
            return "\n".join(message_lines[-count:])
            
        except Exception as e:
            return f"Error reading messages: {str(e)}"

    def ensure_whatsapp_open(self):
        """Ensure WhatsApp is open before performing actions"""
        if not self.is_open:
            try:
                # Try UWP/Store app first
                os.system("start whatsapp:")
                time.sleep(2)  # Wait for WhatsApp to open
                self.is_open = True
                return True
            except:
                try:
                    # Try desktop app path
                    whatsapp_path = os.path.join(os.getenv('LOCALAPPDATA'), 'WhatsApp', 'WhatsApp.exe')
                    if os.path.exists(whatsapp_path):
                        os.startfile(whatsapp_path)
                        time.sleep(2)
                        self.is_open = True
                        return True
                except:
                    try:
                        # Fallback to web version
                        webbrowser.open('https://web.whatsapp.com')
                        time.sleep(5)  # Give more time for web version to load
                        self.is_open = True
                        return True
                    except:
                        return False
        return True

def create_reference_images():
    """Utility function to create reference images"""
    print("This will help create reference images for WhatsApp elements.")
    print("Please open WhatsApp and make sure it's visible.")
    
    elements = [
        'search_box',
        'attach_button',
        'message_box',
        'send_button'
    ]
    
    ref_dir = os.path.join(os.path.dirname(__file__), 'whatsapp_refs')
    if not os.path.exists(ref_dir):
        os.makedirs(ref_dir)
    
    for element in elements:
        input(f"\nPress Enter when ready to capture {element}...")
        print("Capturing in 3 seconds...")
        time.sleep(3)
        
        # Capture small region around mouse
        x, y = pyautogui.position()
        screenshot = pyautogui.screenshot(region=(x-25, y-25, 50, 50))
        
        # Save reference image
        filename = os.path.join(ref_dir, f"{element}.png")
        screenshot.save(filename)
        print(f"Saved {filename}")
        # Run this once to create reference images
controller = WhatsAppController()

# It will auto-calibrate on first use
controller.send_message("arjun", "Hello!")
controller.read_last_messages()