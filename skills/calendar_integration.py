from datetime import datetime, timedelta

class SimpleCalendar:
    def __init__(self):
        self.events = []

    def add_event(self, title, date_time):
        self.events.append({"title": title, "date_time": date_time})
        self.events.sort(key=lambda x: x["date_time"])

    def get_upcoming_events(self, max_results=10):
        now = datetime.now()
        upcoming = [event for event in self.events if event["date_time"] > now]
        return upcoming[:max_results]

    def remove_event(self, title):
        self.events = [event for event in self.events if event["title"] != title]

# Usage example
calendar = SimpleCalendar()

# Add some sample events
calendar.add_event("Team Meeting", datetime.now() + timedelta(days=1))
calendar.add_event("Dentist Appointment", datetime.now() + timedelta(days=3))
calendar.add_event("Birthday Party", datetime.now() + timedelta(days=5))

# Get upcoming events
upcoming_events = calendar.get_upcoming_events()
for event in upcoming_events:
    print(f"{event['title']} on {event['date_time']}")

# Remove an event
calendar.remove_event("Dentist Appointment")
