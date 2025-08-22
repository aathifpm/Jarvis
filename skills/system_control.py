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

    # Quick settings commands
    quick_settings = {
        'wifi': toggle_wifi,
        'bluetooth': toggle_bluetooth,
        'airplane': toggle_airplane_mode,
        'night light': toggle_night_light,
        'hotspot': toggle_focus_assist,
        'volume': adjust_volume,
        'brightness': adjust_brightness,
    }

    # Check quick settings commands first
    for key, func in quick_settings.items():
        if key in command:
            return func(command) if key in ['volume', 'brightness'] else func()

    # System commands
    system_commands = {
        'screenshot': take_screenshot,
        'lock': lambda: os.system('rundll32.exe user32.dll,LockWorkStation'),
        'sleep': lambda: os.system('rundll32.exe powrprof.dll,SetSuspendState 0,1,0'),
        'shutdown': lambda: os.system('shutdown /s /t 0'),
        'restart': lambda: os.system('shutdown /r /t 0'),
        'task manager': lambda: os.system('taskmgr'),
        'settings': lambda: os.system('start ms-settings:'),
        'explorer': lambda: os.system('explorer'),
        'processes': list_processes,
        'cpu': get_cpu_usage,
        'memory': get_memory_usage,
        'disk': get_disk_space,
        'system info': get_system_info,
        'whatsapp': lambda: handle_whatsapp_control(assistant, entities)
    }

    # Check system commands
    for key, func in system_commands.items():
        if key in command:
            return func()

    # Handle open/close commands
    if any(word in command for word in ["open", "launch", "start"]):
        return open_application(command)
    elif any(word in command for word in ["close", "exit", "quit"]):
        return close_application(command)

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
            'desktop': str(Path(os.getenv('LOCALAPPDATA')) / 'Programs' / 'WhatsApp' / 'WhatsApp.exe')
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
        },
        'brave': {
            'desktop': str(Path(os.getenv('PROGRAMFILES')) / 'BraveSoftware' / 'Brave-Browser' / 'Application' / 'brave.exe'),
            'store': 'Brave'
        },
        'vscode': {
            'desktop': str(Path(os.getenv('LOCALAPPDATA')) / 'Programs' / 'Microsoft VS Code' / 'Code.exe'),
            'store': 'VSCode'
        },
        'notepad': {
            'desktop': str(Path(os.getenv('WINDIR')) / 'notepad.exe')
        },
        'calculator': {
            'desktop': str(Path(os.getenv('WINDIR')) / 'System32' / 'calc.exe')
        },
        'paint': {
            'desktop': str(Path(os.getenv('WINDIR')) / 'System32' / 'mspaint.exe')
        },
        'word': {
            'desktop': str(Path(os.getenv('PROGRAMFILES')) / 'Microsoft Office' / 'root' / 'Office16' / 'WINWORD.EXE')
        },
        'excel': {
            'desktop': str(Path(os.getenv('PROGRAMFILES')) / 'Microsoft Office' / 'root' / 'Office16' / 'EXCEL.EXE')
        },
        'powerpoint': {
            'desktop': str(Path(os.getenv('PROGRAMFILES')) / 'Microsoft Office' / 'root' / 'Office16' / 'POWERPNT.EXE')
        },
        'teams': {
            'desktop': str(Path(os.getenv('LOCALAPPDATA')) / 'Microsoft' / 'Teams' / 'current' / 'Teams.exe'),
            'store': 'Teams'
        },
        'discord': {
            'web': 'https://discord.com/app',
            'desktop': str(Path(os.getenv('LOCALAPPDATA')) / 'Discord' / 'Update.exe'),
            'store': 'Discord'
        },
        'steam': {
            'desktop': str(Path(os.getenv('PROGRAMFILES(X86)')) / 'Steam' / 'Steam.exe')
        }
    }

def open_application(command):
    """
    Dynamic function to open any application without predefined names
    """
    app_name = command.split("open", 1)[-1].strip().lower()
    if not app_name:
        return "Please specify an application to open."

    try:
        # 1. Try Windows Search/Run (Most universal method)
        try:
            os.system(f"start {app_name}")
            return f"Opening {app_name}"
        except:
            pass

        # 2. Search in common installation directories
        program_dirs = [
            os.getenv('PROGRAMFILES'),
            os.getenv('PROGRAMFILES(X86)'),
            os.getenv('LOCALAPPDATA'),
            os.getenv('APPDATA'),
            os.getenv('WINDIR'),
            os.path.join(os.getenv('LOCALAPPDATA'), 'Programs'),
            os.path.join(os.getenv('APPDATA'), 'Microsoft', 'Windows', 'Start Menu', 'Programs')
        ]

        possible_extensions = ['.exe', '.msi', '.bat', '.cmd', '.lnk']
        
        for program_dir in program_dirs:
            if not program_dir:
                continue
                
            # Search recursively with a depth limit
            for root, dirs, files in os.walk(program_dir):
                # Skip certain system directories to improve performance
                if any(skip in root.lower() for skip in ['windows.old', '$recycle.bin', 'temp', 'tmp']):
                    continue
                    
                # Check current depth to limit recursive search
                depth = root[len(program_dir):].count(os.sep)
                if depth > 4:  # Limit depth to improve performance
                    continue

                for file in files:
                    file_lower = file.lower()
                    if any(file_lower.endswith(ext) for ext in possible_extensions):
                        # Check if filename contains the app name
                        if app_name in file_lower.replace('.exe', '').replace('.lnk', ''):
                            full_path = os.path.join(root, file)
                            try:
                                os.startfile(full_path)
                                return f"Opening {file}"
                            except:
                                continue

        # 3. Try Windows Store apps
        try:
            # Use PowerShell to get installed apps
            powershell_command = 'Get-AppxPackage | ConvertTo-Json'
            result = subprocess.run(['powershell', '-Command', powershell_command], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                apps = json.loads(result.stdout)
                for app_info in apps:
                    if isinstance(app_info, dict) and 'Name' in app_info:
                        store_app_name = app_info['Name'].lower()
                        if app_name in store_app_name:
                            os.system(f"start shell:AppsFolder\\{app_info['Name']}")
                            return f"Opening {app_info['Name']}"
        except:
            pass

        # 4. Check if it's a URL
        if '.' in app_name and not any(ext in app_name for ext in possible_extensions):
            if not app_name.startswith(('http://', 'https://')):
                app_name = 'https://' + app_name
            webbrowser.open(app_name)
            return f"Opening {app_name}"

        # 5. Try Windows Run dialog with .exe extension
        try:
            os.system(f"start {app_name}.exe")
            return f"Opening {app_name}"
        except:
            pass

        return f"Could not find application: {app_name}"

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
    """Adjust brightness using WMI"""
    try:
        brightness = int(''.join(filter(str.isdigit, command)))
        if 0 <= brightness <= 100:
            c = wmi.WMI(namespace='wmi')
            methods = c.WmiMonitorBrightnessMethods()[0]
            methods.WmiSetBrightness(brightness, 0)
            return f"Brightness set to {brightness}%"
        return "Please specify a brightness level between 0 and 100%"
    except Exception as e:
        return f"Failed to adjust brightness: {str(e)}"

def adjust_volume(command):
    """Optimized volume control using direct API"""
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
            
        # Set specific volume percentage
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
    """Toggle WiFi using Windows Action Center"""
    try:
        # Open Action Center
        pyautogui.hotkey('win', 'a')
        time.sleep(0.8)
        pyautogui.press('space')
        time.sleep(0.2)
        
        # Close Action Center
        pyautogui.hotkey('win', 'a')
        return "WiFi toggled"
    except Exception as e:
        return f"Failed to toggle WiFi: {str(e)}"

def toggle_bluetooth():
    """Toggle Bluetooth using Windows Action Center"""
    try:
        # Open Action Center
        pyautogui.hotkey('win', 'a')
        time.sleep(0.8)
            
        # Move right to reach Bluetooth
        pyautogui.press('right')
        time.sleep(0.1)
        
        # Toggle Bluetooth
        pyautogui.press('space')
        time.sleep(0.2)
        
        # Close Action Center
        pyautogui.hotkey('win', 'a')
        return "Bluetooth toggled"
    except Exception as e:
        return f"Failed to toggle Bluetooth: {str(e)}"

def toggle_airplane_mode():
    """Toggle airplane mode using Windows Action Center"""
    try:
        # Open Action Center
        pyautogui.hotkey('win', 'a')
        time.sleep(0.5)
            
        # Move right twice to reach airplane mode
        for _ in range(2):
            pyautogui.press('right')
            time.sleep(0.1)
        
        # Toggle airplane mode
        pyautogui.press('space')
        time.sleep(0.2)
        
        # Close Action Center
        pyautogui.hotkey('win', 'a')
        return "Airplane mode toggled"
    except Exception as e:
        return f"Failed to toggle airplane mode: {str(e)}"

def toggle_night_light():
    """Toggle night light using Windows Action Center"""
    try:
        # Open Action Center
        pyautogui.hotkey('win', 'a')
        time.sleep(0.5)
        # Move right three times to reach night light
        for _ in range(4):
            pyautogui.press('right')
            time.sleep(0.1)
        
        # Toggle night light
        pyautogui.press('space')
        time.sleep(0.2)
        
        # Close Action Center
        pyautogui.hotkey('win', 'a')
        return "Night light toggled"
    except Exception as e:
        return f"Failed to toggle night light: {str(e)}"

def toggle_focus_assist():
    """Toggle focus assist using Windows Action Center"""
    try:
        # Open Action Center
        pyautogui.hotkey('win', 'a')
        time.sleep(0.5)
        
        
            
        # Move right four times to reach focus assist
        for _ in range(5):
            pyautogui.press('right')
            time.sleep(0.1)
        
        # Toggle focus assist
        pyautogui.press('space')
        time.sleep(0.2)
        
        # Close Action Center
        pyautogui.hotkey('win', 'a')
        return "Focus assist toggled"
    except Exception as e:
        return f"Failed to toggle focus assist: {str(e)}"

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
    """Toggle system dark mode"""
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", 
                            0, winreg.KEY_ALL_ACCESS)
        current_value, _ = winreg.QueryValueEx(key, "AppsUseLightTheme")
        new_value = 0 if current_value == 1 else 1
        winreg.SetValueEx(key, "AppsUseLightTheme", 0, winreg.REG_DWORD, new_value)
        winreg.SetValueEx(key, "SystemUsesLightTheme", 0, winreg.REG_DWORD, new_value)
        winreg.CloseKey(key)
        return "Dark mode toggled"
    except WindowsError:
        return "Failed to toggle dark mode"

def open_notification_center():
    """Open notification center"""
    pyautogui.hotkey('win', 'n')
    return "Notification center opened"

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
