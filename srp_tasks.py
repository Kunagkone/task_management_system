from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Iterable
from enum import Enum

# --------------------------
# Abstract Storage Interface
# --------------------------
class TaskStorage(ABC):
    @abstractmethod
    def load_tasks(self) -> List["Task"]:
        """Load tasks from the underlying medium."""
        raise NotImplementedError

    @abstractmethod
    def save_tasks(self, tasks: Iterable["Task"]) -> None:
        """Persist tasks to the underlying medium."""
        raise NotImplementedError


# --------------------------
# Priority Enum
# --------------------------
class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

    @classmethod
    def from_str(cls, value: Optional[str]) -> "Priority":
        if not value:
            return cls.MEDIUM
        v = str(value).strip().lower()
        if v in {"l", "low"}:
            return cls.LOW
        if v in {"m", "med", "medium"}:
            return cls.MEDIUM
        if v in {"h", "hi", "high"}:
            return cls.HIGH
        return cls.MEDIUM


# --------------------------
# File-based Task Storage (CSV-like)
# --------------------------
class FileTaskStorage(TaskStorage):
    def __init__(self, filename: str = "tasks.txt") -> None:
        self.filename = Path(filename)

    def load_tasks(self) -> List["Task"]:
        loaded: List[Task] = []
        if not self.filename.exists():
            print(f"No existing task file '{self.filename}' found. Starting fresh.")
            return loaded

        with self.filename.open("r", encoding="utf-8") as f:
            for line in f:
                parts = line.rstrip("\n").split(",")
                if len(parts) not in (4, 5):
                    continue  # skip malformed lines quietly
                try:
                    task_id = int(parts[0])
                    description = parts[1].replace("\\u002C", ",")
                    due_date = parts[2] or None
                    due_date = None if due_date == "None" else due_date
                    completed = parts[3].strip().lower() == "true"
                    priority = Priority.from_str(parts[4]) if len(parts) == 5 else Priority.MEDIUM
                    loaded.append(Task(task_id, description, due_date, completed, priority))
                except ValueError:
                    continue
        return loaded

    def save_tasks(self, tasks: Iterable["Task"]) -> None:
        with self.filename.open("w", encoding="utf-8") as f:
            for t in tasks:
                desc = (t.description or "").replace(",", "\\u002C")
                f.write(f"{t.id},{desc},{t.due_date},{t.completed},{t.priority.value}\n")
        print(f"Tasks saved to {self.filename}")


# --------------------------
# Domain Model: Task
# --------------------------
@dataclass
class Task:
    id: int
    description: str
    due_date: Optional[str] = None
    completed: bool = False
    priority: Priority = Priority.MEDIUM  # low/medium/high

    def mark_completed(self) -> None:
        self.completed = True
        print(f"Task {self.id} '{self.description}' marked as completed.")

    def __str__(self) -> str:
        status = "/" if self.completed else " "
        due = f" (Due: {self.due_date})" if self.due_date else ""
        return f"[{status}] {self.id}. {self.description}{due} [Priority: {self.priority.value}]"


# --------------------------
# TaskManager (coordinates domain + storage)
# --------------------------
class TaskManager:
    def __init__(self, storage: TaskStorage) -> None:
        self.storage = storage
        self.tasks: List[Task] = self.storage.load_tasks()
        self.next_id: int = (max((t.id for t in self.tasks), default=0) + 1)
        print(f"Loaded {len(self.tasks)} tasks. Next ID: {self.next_id}")

    def add_task(
        self,
        description: str,
        due_date: Optional[str] = None,
        priority: Optional[object] = None,  # can be Priority or str
    ) -> Task:
        pr = priority if isinstance(priority, Priority) else Priority.from_str(priority)
        task = Task(self.next_id, description, due_date, False, pr)
        self.tasks.append(task)
        self.next_id += 1
        self.storage.save_tasks(self.tasks)
        print(f"Task '{description}' added with priority {pr.value}.")
        return task

    def list_tasks(self) -> List[Task]:
        return list(self.tasks)

    def get_task_by_id(self, task_id: int) -> Optional[Task]:
        return next((t for t in self.tasks if t.id == task_id), None)

    def mark_task_completed(self, task_id: int) -> bool:
        task = self.get_task_by_id(task_id)
        if not task:
            print(f"Task {task_id} not found.")
            return False
        task.mark_completed()
        self.storage.save_tasks(self.tasks)
        return True

    def remove_task(self, task_id: int) -> bool:
        before = len(self.tasks)
        self.tasks = [t for t in self.tasks if t.id != task_id]
        if len(self.tasks) == before:
            print(f"Task {task_id} not found.")
            return False
        self.storage.save_tasks(self.tasks)
        print(f"Task {task_id} removed.")
        return True


# --------------------------
# Main Program Logic (demo CLI)
# --------------------------
if __name__ == "__main__":
    storage = FileTaskStorage("my_tasks.txt")
    manager = TaskManager(storage)

    if not manager.list_tasks():
        manager.add_task("Review SOLID Principles", "2024-08-10", priority="high")
        manager.add_task("Prepare for Final Exam", "2024-08-15", priority="medium")
        manager.add_task("Do laundry", priority="low")

    print("\n--- Current Tasks ---")
    for t in manager.list_tasks():
        print(t)
    print("---------------------")

    manager.mark_task_completed(1)

    print("\n--- After Complete(1) ---")
    for t in manager.list_tasks():
        print(t)
    print("-------------------------")
