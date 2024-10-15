import datetime
import time
import threading
import json
import os
from playsound import playsound
import re

ALARMS_FILE = os.path.join("data", "alarms.json")

class AlarmManager:
    def __init__(self):
        self.alarms = self.load_alarms()
        self.alarm_thread = None

    def load_alarms(self):
        if os.path.exists(ALARMS_FILE):
            with open(ALARMS_FILE, "r") as f:
                return json.load(f)
        return []

    def save_alarms(self):
        with open(ALARMS_FILE, "w") as f:
            json.dump(self.alarms, f)

    def add_alarm(self, time_str, label=""):
        try:
            # Remove any dots and convert to lowercase
            time_str = time_str.replace(".", "").lower().strip()
            
            # Use regex to extract hour, minute, and period
            match = re.match(r'(\d{1,2}):(\d{2})\s*(am|pm)?', time_str)
            if not match:
                raise ValueError("Invalid time format")
            
            hour, minute, period = match.groups()
            hour = int(hour)
            minute = int(minute)
            
            # Adjust hour based on period
            if period == 'pm' and hour != 12:
                hour += 12
            elif period == 'am' and hour == 12:
                hour = 0
            
            alarm_time = time(hour, minute)
            
            alarm = {
                "time": alarm_time.strftime("%H:%M"),
                "label": label,
                "active": True
            }
            self.alarms.append(alarm)
            self.save_alarms()
            return f"Alarm set for {alarm_time.strftime('%I:%M %p')}" + (f" with label: {label}" if label else "")
        except ValueError as e:
            return f"Sorry, I couldn't understand that time format. {str(e)}"

    def remove_alarm(self, index):
        if 0 <= index < len(self.alarms):
            removed_alarm = self.alarms.pop(index)
            self.save_alarms()
            return f"Removed alarm for {removed_alarm['time']}" + (f" with label: {removed_alarm['label']}" if removed_alarm['label'] else "")
        return "Invalid alarm index."

    def list_alarms(self):
        if not self.alarms:
            return "You have no alarms set."
        alarm_list = []
        for i, alarm in enumerate(self.alarms):
            status = "Active" if alarm['active'] else "Inactive"
            label_info = f" - {alarm['label']}" if alarm['label'] else ""
            alarm_list.append(f"{i+1}. {alarm['time']} {status}{label_info}")
        return "Your alarms:\n" + "\n".join(alarm_list)

    def toggle_alarm(self, index):
        if 0 <= index < len(self.alarms):
            self.alarms[index]['active'] = not self.alarms[index]['active']
            self.save_alarms()
            status = "activated" if self.alarms[index]['active'] else "deactivated"
            return f"Alarm for {self.alarms[index]['time']} {status}."
        return "Invalid alarm index."

    def check_alarms(self):
        while True:
            now = datetime.datetime.now().time()
            current_time = now.strftime("%H:%M")
            for alarm in self.alarms:
                if alarm['active'] and alarm['time'] == current_time:
                    self.trigger_alarm(alarm)
            time.sleep(30)

    def trigger_alarm(self, alarm):
        print(f"ALARM! {alarm['time']} - {alarm['label']}")
        try:
            playsound("path/to/alarm_sound.mp3")
        except Exception as e:
            print(f"Error playing alarm sound: {e}")

    def start_alarm_thread(self):
        if self.alarm_thread is None or not self.alarm_thread.is_alive():
            self.alarm_thread = threading.Thread(target=self.check_alarms)
            self.alarm_thread.daemon = True
            self.alarm_thread.start()

def handle_alarm(assistant, entities):
    global alarm_manager
    if not hasattr(handle_alarm, 'alarm_manager'):
        handle_alarm.alarm_manager = AlarmManager()
        handle_alarm.alarm_manager.start_alarm_thread()

    command = " ".join(entities.get("tokens", []))
    
    if "set" in command and "alarm" in command:
        # Extract time and label more flexibly
        time_label_part = command.split("alarm", 1)[1].strip()
        time_str = time_label_part
        label = ""
        if "for" in time_label_part:
            time_str, label = time_label_part.split("for", 1)
        return handle_alarm.alarm_manager.add_alarm(time_str, label.strip())
    elif "remove" in command and "alarm" in command:
        try:
            index = int(command.split("alarm")[1].strip().split()[0]) - 1
            return handle_alarm.alarm_manager.remove_alarm(index)
        except (ValueError, IndexError):
            return "Please specify the alarm number to remove."
    elif "list" in command and "alarms" in command:
        return handle_alarm.alarm_manager.list_alarms()
    elif "toggle" in command and "alarm" in command:
        try:
            index = int(command.split("alarm")[1].strip().split()[0]) - 1
            return handle_alarm.alarm_manager.toggle_alarm(index)
        except (ValueError, IndexError):
            return "Please specify the alarm number to toggle."
    else:
        return "I'm sorry, I couldn't understand the alarm command. You can set, remove, list, or toggle alarms."

# Initialize the alarm manager when the module is imported
alarm_manager = AlarmManager()
alarm_manager.start_alarm_thread()
