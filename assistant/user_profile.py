class UserProfile:
    def __init__(self):
        self.preferences = {}
        self.habits = {}

    def set_preference(self, key, value):
        self.preferences[key] = value

    def get_preference(self, key):
        return self.preferences.get(key)

    def update_habit(self, action):
        if action not in self.habits:
            self.habits[action] = 1
        else:
            self.habits[action] += 1

# Usage in core.py
user_profile = UserProfile()
user_profile.set_preference('wake_up_time', '07:00')
user_profile.update_habit('check_weather')