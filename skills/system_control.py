import os
import subprocess
import psutil
import platform
from datetime import datetime
import pyautogui
import wmi
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import winreg
import time
import pyperclip
import webbrowser
import json
from pathlib import Path
from skills.live_transcription import handle_live_transcription
from skills.whatsapp_control import handle_whatsapp_control

def handle_system_control(assistant, entities):
    tokens = entities.get("tokens", [])
    command = " ".join(tokens).lower()

    # Check for transcription command first
    if any(word in command for word in ["transcribe", "transcription", "record"]):
        return handle_live_transcription(assistant, entities)

    # Add WhatsApp control handling
    if "whatsapp" in command:
        return handle_whatsapp_control(assistant, entities)

    # Rest of quick commands
    quick_commands = {
        'screenshot': take_screenshot,
        'wifi': toggle_wifi,
        'bluetooth': toggle_bluetooth,
        'lock': lambda: os.system('rundll32.exe user32.dll,LockWorkStation'),
        'sleep': lambda: os.system('rundll32.exe powrprof.dll,SetSuspendState 0,1,0'),
        'shutdown': lambda: os.system('shutdown /s /t 0'),
        'restart': lambda: os.system('shutdown /r /t 0'),
        'settings': lambda: os.system('start ms-settings:'),
        'explorer': lambda: os.system('explorer'),
        'task': lambda: pyautogui.hotkey('win', 'tab')
    }

    # Check quick commands first
    for key, func in quick_commands.items():
        if key in command:
            return func()

    # Handle other commands
    if any(word in command for word in ["open", "launch", "start"]):
        return open_application(command)
    elif any(word in command for word in ["close", "exit", "quit"]):
        return close_application(command)
    elif any(word in command for word in ["volume", "sound"]):
        return adjust_volume(command)

    return "Command not recognized"

def get_installed_apps():
    """Get a list of installed Windows Store apps and their execution commands"""
    installed_apps = {}
    try:
        # Check Windows Store apps
        powershell_command = 'Get-AppxPackage | ConvertTo-Json'
        result = subprocess.run(['powershell', '-Command', powershell_command], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            apps = json.loads(result.stdout)
            for app in apps:
                if isinstance(app, dict) and 'Name' in app:
                    app_name = app['Name'].lower()
                    installed_apps[app_name] = app
    except Exception as e:
        print(f"Error getting installed apps: {e}")
    return installed_apps

def get_common_paths():
    """Return dictionary of common application paths"""
    return {
        'whatsapp': {
            'web': 'https://web.whatsapp.com',
            'store': 'WhatsApp',
            'desktop': str(Path(os.getenv('LOCALAPPDATA')) / 'WhatsApp' / 'WhatsApp.exe')
        },
        'youtube': {
            'web': 'https://youtube.com',
            'store': 'YouTube'
        },
        'spotify': {
            'web': 'https://open.spotify.com',
            'store': 'Spotify',
            'desktop': str(Path(os.getenv('APPDATA')) / 'Spotify' / 'Spotify.exe')
        },
        'netflix': {
            'web': 'https://netflix.com',
            'store': 'Netflix'
        },
        'chrome': {
            'desktop': str(Path(os.getenv('PROGRAMFILES')) / 'Google' / 'Chrome' / 'Application' / 'chrome.exe')
        },
        'firefox': {
            'desktop': str(Path(os.getenv('PROGRAMFILES')) / 'Mozilla Firefox' / 'firefox.exe')
        },
        'edge': {
            'desktop': str(Path(os.getenv('PROGRAMFILES(X86)')) / 'Microsoft' / 'Edge' / 'Application' / 'msedge.exe')
        }
        # Add more applications as needed
    }

def open_application(command):
    """
    Optimized function to open applications quickly
    """
    app_name = command.split("open", 1)[-1].strip().lower()
    if not app_name:
        return "Please specify an application to open."

    try:
        # Get common paths dictionary
        common_paths = get_common_paths()
        
        # Special handling for WhatsApp
        if "whatsapp" in app_name:
            # Try multiple methods in order of preference
            try:
                # Try UWP/Store app first
                os.system("start whatsapp:")
                return "Opening WhatsApp"
            except:
                try:
                    # Try desktop app path
                    whatsapp_path = common_paths['whatsapp']['desktop']
                    if os.path.exists(whatsapp_path):
                        os.startfile(whatsapp_path)
                        return "Opening WhatsApp Desktop"
                except:
                    # Fallback to web version
                    webbrowser.open('https://web.whatsapp.com')
                    return "Opening WhatsApp Web"

        # Quick check for web URLs first
        if any(tld in app_name for tld in ['.com', '.org', '.net', '.edu']):
            if not app_name.startswith(('http://', 'https://')):
                app_name = 'https://' + app_name
            webbrowser.open(app_name)
            return f"Opening {app_name}"

        # Common apps dictionary with direct commands
        quick_apps = {
            'whatsapp': {
                'cmd': 'WhatsApp:///',
                'web': 'https://web.whatsapp.com'
            },
            'youtube': 'https://youtube.com',
            'spotify': 'spotify:/',
            'netflix': 'https://netflix.com',
            'chrome': 'chrome',
            'firefox': 'firefox',
            'edge': 'msedge',
            'notepad': 'notepad',
            'calculator': 'calc',
            'word': 'winword',
            'excel': 'excel',
            'powerpoint': 'powerpnt',
            'teams': 'teams',
            'code': 'code',
            'terminal': 'wt',
            'cmd': 'cmd',
            'paint': 'mspaint'
        }

        # Check quick apps first
        if app_name in quick_apps:
            app_info = quick_apps[app_name]
            if isinstance(app_info, dict):
                try:
                    os.startfile(app_info['cmd'])
                except:
                    webbrowser.open(app_info['web'])
            else:
                os.system(f"start {app_info}")
            return f"Opening {app_name}"

        # Try direct start command (fastest method)
        os.system(f"start {app_name}")
        return f"Opening {app_name}"

    except Exception as e:
        return f"Error opening {app_name}: {str(e)}"

def close_application(command):
    """
    Optimized function to close applications quickly
    """
    app = next((token for token in command.split() if token not in ["close", "exit", "quit"]), None)
    if not app:
        return "Please specify an application to close."

    try:
        # Quick terminate using taskkill (faster than psutil)
        os.system(f"taskkill /im {app}.exe /f >nul 2>&1")
        return f"Closed {app}"
    except Exception as e:
        return f"Error closing {app}: {str(e)}"

def get_system_info():
    system = platform.system()
    release = platform.release()
    machine = platform.machine()
    return f"System: {system}, Release: {release}, Machine: {machine}"

def get_cpu_usage():
    cpu_percent = psutil.cpu_percent(interval=1)
    return f"Current CPU usage is {cpu_percent}%"

def get_memory_usage():
    memory = psutil.virtual_memory()
    return f"Total memory: {memory.total / (1024**3):.2f} GB, Used: {memory.percent}%"

def get_disk_space():
    disk = psutil.disk_usage('/')
    return f"Total disk space: {disk.total / (1024**3):.2f} GB, Used: {disk.percent}%"

def list_processes():
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'status']):
        processes.append(f"{proc.info['pid']}: {proc.info['name']} ({proc.info['status']})")
    return "\n".join(processes[:10])  # Return top 10 processes

def kill_process(command):
    process_name = command.split("kill", 1)[-1].strip()
    for proc in psutil.process_iter(['name']):
        if proc.info['name'].lower() == process_name.lower():
            proc.terminate()
            return f"Terminated process: {process_name}"
    return f"Process {process_name} not found."

def take_screenshot():
    """
    Takes a full screenshot and saves it automatically
    """
    try:
        # Create screenshots directory if it doesn't exist
        screenshots_dir = os.path.join(os.path.expanduser("~"), "Pictures", "Screenshots")
        os.makedirs(screenshots_dir, exist_ok=True)

        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(screenshots_dir, f"screenshot_{timestamp}.png")

        # Take full screenshot
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        
        # Open the screenshots folder
        os.startfile(screenshots_dir)
        
        return f"Screenshot saved to {filename}"
    except Exception as e:
        return f"Error taking screenshot: {str(e)}"

def adjust_brightness(command):
    try:
        # Extract the brightness percentage from the command
        brightness = int(command.split('%')[0].split()[-1])
        if 0 <= brightness <= 100:
            c = wmi.WMI(namespace='wmi')
            methods = c.WmiMonitorBrightnessMethods()[0]
            methods.WmiSetBrightness(brightness, 0)
            return f"Brightness set to {brightness}%"
        else:
            return "Please specify a brightness level between 0 and 100%"
    except Exception as e:
        return f"Failed to adjust brightness: {str(e)}"

def adjust_volume(command):
    """
    Optimized volume control function
    """
    try:
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        
        if "up" in command or "increase" in command:
            current = volume.GetMasterVolumeLevelScalar()
            volume.SetMasterVolumeLevelScalar(min(1.0, current + 0.1), None)
            return "Volume increased"
            
        elif "down" in command or "decrease" in command:
            current = volume.GetMasterVolumeLevelScalar()
            volume.SetMasterVolumeLevelScalar(max(0.0, current - 0.1), None)
            return "Volume decreased"
            
        elif "mute" in command:
            volume.SetMute(1, None)
            return "Muted"
            
        elif "unmute" in command:
            volume.SetMute(0, None)
            return "Unmuted"
            
        # Quick percentage parsing
        try:
            vol = int(''.join(filter(str.isdigit, command)))
            if 0 <= vol <= 100:
                volume.SetMasterVolumeLevelScalar(vol/100, None)
                return f"Volume set to {vol}%"
        except ValueError:
            pass
            
        return "Invalid volume command"
        
    except Exception as e:
        return f"Volume control error: {str(e)}"

def toggle_wifi():
    """
    Optimized WiFi toggle using direct command
    """
    os.system("netsh interface set interface Wi-Fi toggle >nul 2>&1")
    return "WiFi toggled"

def toggle_bluetooth():
    """
    Optimized Bluetooth toggle using direct command
    """
    os.system("start ms-settings:bluetooth")
    return "Bluetooth settings opened"

def toggle_airplane_mode():
    pyautogui.hotkey('win', 'a')  # Open Action Center
    time.sleep(0.5)
    pyautogui.click(x=200, y=100)  # Click on Airplane mode icon (adjust coordinates as needed)
    pyautogui.hotkey('win', 'a')  # Close Action Center
    return "Airplane mode toggled"

def toggle_night_light():
    pyautogui.hotkey('win', 'a')  # Open Action Center
    time.sleep(0.5)
    pyautogui.click(x=250, y=100)  # Click on Night light icon (adjust coordinates as needed)
    pyautogui.hotkey('win', 'a')  # Close Action Center
    return "Night light toggled"

def open_settings():
    pyautogui.hotkey('win', 'i')
    return "Settings opened"

def open_file_explorer():
    pyautogui.hotkey('win', 'e')
    return "File Explorer opened"

def lock_screen():
    pyautogui.hotkey('win', 'l')
    return "Screen locked"

def open_task_view():
    pyautogui.hotkey('win', 'tab')
    return "Task view opened"

def toggle_dark_mode():
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", 0, winreg.KEY_ALL_ACCESS)
        current_value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        new_value = 0 if current_value == 1 else 1
        winreg.SetValueEx(key, "AppsUseLightTheme", 0, winreg.REG_DWORD, new_value)
        winreg.SetValueEx(key, "SystemUsesLightTheme", 0, winreg.REG_DWORD, new_value)
        winreg.CloseKey(key)
        return "Dark mode toggled"
    except WindowsError:
        return "Failed to toggle dark mode"

def open_notification_center():
    pyautogui.hotkey('win', 'n')
    return "Notification center opened"

def toggle_focus_assist():
    pyautogui.hotkey('win', 'a')  # Open Action Center
    time.sleep(0.5)
    pyautogui.click(x=300, y=100)  # Click on Focus assist icon (adjust coordinates as needed)
    pyautogui.hotkey('win', 'a')  # Close Action Center
    return "Focus assist toggled"

def open_quick_link_menu():
    pyautogui.hotkey('win', 'x')
    return "Quick Link menu opened"

def open_run_dialog():
    pyautogui.hotkey('win', 'r')
    return "Run dialog opened"

def open_game_bar():
    pyautogui.hotkey('win', 'g')
    return "Game bar opened"

def toggle_magnifier():
    pyautogui.hotkey('win', '+')
    return "Magnifier toggled"

def open_emoji_panel():
    pyautogui.hotkey('win', '.')
    return "Emoji panel opened"

def copy_to_clipboard(command):
    try:
        text = command.split("copy", 1)[1].strip()
        pyperclip.copy(text)
        return f"Copied text to clipboard"
    except Exception as e:
        return f"Failed to copy: {str(e)}"

def paste_from_clipboard():
    try:
        text = pyperclip.paste()
        return f"Clipboard contains: {text}"
    except Exception as e:
        return f"Failed to paste: {str(e)}"

def shutdown_system():
    try:
        os.system("shutdown /s /t 1")
        return "Shutting down system..."
    except Exception as e:
        return f"Failed to shutdown: {str(e)}"

def restart_system():
    try:
        os.system("shutdown /r /t 1")
        return "Restarting system..."
    except Exception as e:
        return f"Failed to restart: {str(e)}"

def sleep_system():
    try:
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
        return "Putting system to sleep..."
    except Exception as e:
        return f"Failed to sleep: {str(e)}"
