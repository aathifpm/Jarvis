import speech_recognition as sr
import threading
import time
import os
import pyperclip
import webbrowser
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext
import pyautogui

class LiveTranscription:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.is_running = False
        self.transcribed_text = ""
        self.window = None
        self.text_area = None
        self.setup_gui()

    def setup_gui(self):
        """Setup the GUI window for live transcription"""
        self.window = tk.Tk()
        self.window.title("Live Transcription")
        self.window.geometry("600x400")
        
        # Make window appear on top
        self.window.lift()
        self.window.attributes('-topmost', True)

        # Create buttons frame
        button_frame = tk.Frame(self.window)
        button_frame.pack(pady=5)

        # Add control buttons with better styling
        button_style = {'padx': 10, 'pady': 5, 'width': 12}
        
        tk.Button(button_frame, text="Start", command=self.start_transcription, 
                 bg='green', fg='white', **button_style).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Stop", command=self.stop_transcription,
                 bg='red', fg='white', **button_style).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Save", command=self.save_to_file,
                 bg='blue', fg='white', **button_style).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Copy", command=self.copy_to_clipboard,
                 bg='purple', fg='white', **button_style).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Share WhatsApp", command=self.share_whatsapp,
                 bg='#25D366', fg='white', **button_style).pack(side=tk.LEFT, padx=5)
        
        tk.Button(button_frame, text="Clear", command=self.clear_text,
                 bg='gray', fg='white', **button_style).pack(side=tk.LEFT, padx=5)

        # Add text area with better styling
        self.text_area = scrolledtext.ScrolledText(
            self.window, 
            wrap=tk.WORD, 
            width=60, 
            height=20,
            font=('Arial', 11),
            bg='white',
            fg='black'
        )
        self.text_area.pack(padx=10, pady=10, expand=True, fill='both')

    def start_transcription(self):
        """Start the live transcription"""
        if not self.is_running:
            self.is_running = True
            self.transcription_thread = threading.Thread(target=self.transcribe_audio)
            self.transcription_thread.daemon = True
            self.transcription_thread.start()
            self.text_area.insert(tk.END, "Transcription started...\n")
            self.text_area.see(tk.END)

    def stop_transcription(self):
        """Stop the live transcription"""
        self.is_running = False
        self.text_area.insert(tk.END, "\nTranscription stopped.\n")
        self.text_area.see(tk.END)

    def transcribe_audio(self):
        """Main transcription loop"""
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            
            while self.is_running:
                try:
                    audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=None)
                    text = self.recognizer.recognize_google(audio)
                    self.transcribed_text += text + " "
                    
                    # Update GUI
                    self.window.after(0, self.update_text_area, text)
                    
                except sr.WaitTimeoutError:
                    continue
                except sr.UnknownValueError:
                    continue
                except sr.RequestError as e:
                    self.window.after(0, self.update_text_area, f"\nError: {str(e)}\n")
                except Exception as e:
                    self.window.after(0, self.update_text_area, f"\nError: {str(e)}\n")

    def update_text_area(self, text):
        """Update the text area with new transcribed text"""
        self.text_area.insert(tk.END, text + " ")
        self.text_area.see(tk.END)

    def save_to_file(self):
        """Save transcribed text to a file"""
        try:
            # Create documents directory if it doesn't exist
            docs_dir = os.path.join(os.path.expanduser("~"), "Documents", "Transcriptions")
            os.makedirs(docs_dir, exist_ok=True)

            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(docs_dir, f"transcription_{timestamp}.txt")

            # Save the text
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.text_area.get("1.0", tk.END))

            # Open the file in notepad
            os.system(f'notepad "{filename}"')
            
            self.text_area.insert(tk.END, f"\nTranscription saved to {filename}\n")
            self.text_area.see(tk.END)
        except Exception as e:
            self.text_area.insert(tk.END, f"\nError saving file: {str(e)}\n")
            self.text_area.see(tk.END)

    def copy_to_clipboard(self):
        """Copy transcribed text to clipboard"""
        text = self.text_area.get("1.0", tk.END)
        pyperclip.copy(text)
        self.text_area.insert(tk.END, "\nText copied to clipboard\n")
        self.text_area.see(tk.END)

    def share_whatsapp(self):
        """Share transcribed text via WhatsApp"""
        text = self.text_area.get("1.0", tk.END).strip()
        encoded_text = text.replace('\n', '%0A')
        webbrowser.open(f'https://wa.me/?text={encoded_text}')
        self.text_area.insert(tk.END, "\nOpening WhatsApp to share text\n")
        self.text_area.see(tk.END)

    def clear_text(self):
        """Clear the text area"""
        self.text_area.delete("1.0", tk.END)
        self.transcribed_text = ""

    def run(self):
        """Start the GUI application"""
        self.window.mainloop()

def handle_live_transcription(assistant, entities):
    """Handler function to start live transcription"""
    transcriber = LiveTranscription()
    transcriber.run()
    return "Live transcription started" 