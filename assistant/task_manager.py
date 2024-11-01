import json
import os
from datetime import datetime

class Task:
    def __init__(self, description, priority=0, due_date=None, category=None):
        self.description = description
        self.priority = priority
        self.due_date = due_date
        self.category = category
        self.created_at = datetime.now()

class TaskManager:
    def __init__(self):
        self.tasks_file = os.path.join("data", "tasks.json")
        self.tasks = self.load_tasks()

    def load_tasks(self):
        if os.path.exists(self.tasks_file):
            try:
                with open(self.tasks_file, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print("Error reading tasks file. Starting with an empty task list.")
                return []
        else:
            # If the file doesn't exist, create the directory and an empty file
            os.makedirs(os.path.dirname(self.tasks_file), exist_ok=True)
            with open(self.tasks_file, "w") as f:
                json.dump([], f)
            return []

    def save_tasks(self):
        with open(self.tasks_file, "w") as f:
            json.dump(self.tasks, f)

    def add_task(self, description, priority=0, due_date=None, category=None):
        task = Task(description, priority, due_date, category)
        self.tasks.append(task)
        self.tasks.sort(key=lambda x: (x.priority, x.due_date or datetime.max))
        self.save_tasks()

    def list_tasks(self, category=None):
        if category:
            return [task for task in self.tasks if task.category == category]
        return self.tasks

    def clear_tasks(self):
        self.tasks = []
        self.save_tasks()

def handle_task_management(assistant, entities):
    tokens = entities.get("tokens", [])
    
    if "add" in tokens or "create" in tokens:
        task = " ".join(tokens[tokens.index("task")+1:] if "task" in tokens else tokens[2:])
        assistant.task_manager.add_task(task)
        return f"Task added: {task}"
    elif "list" in tokens or "show" in tokens:
        tasks = assistant.task_manager.list_tasks()
        if tasks:
            task_list = "\n".join([f"- {task.description}" for task in tasks])
            return f"Here are your tasks:\n{task_list}"
        else:
            return "You have no tasks."
    elif "clear" in tokens or "delete" in tokens:
        assistant.task_manager.clear_tasks()
        return "All tasks have been cleared."
    else:
        return "I'm sorry, I couldn't understand the task management command. You can add, list, or clear tasks."
