import os
import subprocess
import psutil
import platform

def handle_system_control(assistant, entities):
    tokens = entities.get("tokens", [])
    
    if "open" in tokens or "launch" in tokens:
        return open_application(tokens)
    elif "close" in tokens or "exit" in tokens:
        return close_application(tokens)
    elif "system" in tokens and "info" in tokens:
        return get_system_info()
    elif "cpu" in tokens and "usage" in tokens:
        return get_cpu_usage()
    elif "memory" in tokens and "usage" in tokens:
        return get_memory_usage()
    elif "disk" in tokens and "space" in tokens:
        return get_disk_space()
    else:
        return "I'm sorry, I couldn't understand the system control command."

def open_application(tokens):
    app = next((token for token in tokens if token not in ["open", "launch"]), None)
    if app:
        try:
            if platform.system() == "Windows":
                if app == "notepad":
                    subprocess.Popen(["notepad.exe"])
                elif app == "calculator":
                    subprocess.Popen(["calc.exe"])
                elif app == "brave":
                    subprocess.Popen(["C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"])
                else:
                    return f"I'm sorry, I don't know how to open {app}."
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", "-a", app])
            elif platform.system() == "Linux":
                subprocess.Popen([app])
            return f"Opening {app}."
        except Exception as e:
            return f"I'm sorry, I couldn't open {app}. Error: {str(e)}"
    return "Please specify an application to open."

def close_application(tokens):
    app = next((token for token in tokens if token not in ["close", "exit"]), None)
    if app:
        for proc in psutil.process_iter(['name']):
            if app.lower() in proc.info['name'].lower():
                proc.terminate()
                return f"Closing {app}."
        return f"I couldn't find {app} running."
    return "Please specify an application to close."

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
