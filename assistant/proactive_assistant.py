import schedule
import time
from threading import Thread

class ProactiveAssistant:
    def __init__(self, jarvis):
        self.jarvis = jarvis

    def check_schedule(self):
        # Check user's schedule and offer relevant assistance
        # This is a placeholder implementation
        self.jarvis.speak("You have a meeting in 30 minutes. Would you like me to prepare a summary?")

    def run_schedule(self):
        schedule.every(30).minutes.do(self.check_schedule)
        while True:
            schedule.run_pending()
            time.sleep(1)

    def start(self):
        Thread(target=self.run_schedule, daemon=True).start()