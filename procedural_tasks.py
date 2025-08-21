# procedural_tasks.py

tasks = []  # Global list to store tasks

def add_task(description, due_date=None):
    task = {"id": len(tasks) + 1, "description": description, "due_date": due_date, "completed": False}
    tasks.append(task)
    print(f"Task '{description}' added.")
    return task

def list_tasks():
    print("\n--- Current Tasks ---")
    if not tasks:
        print("No tasks available.")
        return
    for task in tasks:
        status = "/" if task["completed"] else " "
        due = f" (Due: {task['due_date']})" if task["due_date"] else ""
        print(f"[{status}] {task['id']}. {task['description']}{due}")
    print("---------------------")

def mark_task_completed(task_id):
    for task in tasks:
        if task["id"] == task_id:
            task["completed"] = True
            print(f"Task {task_id} marked as completed.")
            return True
    print(f"Task {task_id} not found.")
    return False

def save_tasks_to_file(filename="tasks.txt"):
    with open(filename, "w") as f:
        for task in tasks:
            f.write(f"{task['id']},{task['description']},{task['due_date']},{task['completed']}\n")
    print(f"Tasks saved to {filename}")

# --- Main Program Logic ---
if __name__ == "__main__":
    add_task("Learn Git", "2024-08-01")
    add_task("Practice OOP", "2024-08-05")
    list_tasks()
    mark_task_completed(1)
    list_tasks()
    save_tasks_to_file()

