"""
Task Manager for the Todo Console Application
Implements business logic for task operations with in-memory storage
"""

from .models import Task


class TaskManager:
    """
    Manages all task operations using in-memory storage
    """

    def __init__(self):
        """Initialize the task manager with empty storage"""
        self._tasks = {}  # Dictionary for O(1) lookup by ID
        self._task_list = []  # List to maintain order of creation
        self._next_id = 1  # Auto-increment ID generator

    def add_task(self, title, description=""):
        """
        Add a new task with the given title and optional description

        Args:
            title (str): Title of the task (1-200 characters)
            description (str, optional): Description of the task (up to 1000 characters)

        Returns:
            Task: The newly created task

        Raises:
            ValueError: If title is invalid
        """
        if not title or len(title.strip()) == 0:
            raise ValueError("Task title cannot be empty")

        # Create new task with auto-generated ID
        task = Task(self._next_id, title, description, completed=False)

        # Store in both data structures
        self._tasks[task.id] = task
        self._task_list.append(task)

        # Increment ID for next task
        self._next_id += 1

        return task

    def list_tasks(self):
        """
        Get all tasks

        Returns:
            list: List of all Task objects
        """
        return self._task_list.copy()

    def get_task(self, task_id):
        """
        Get a specific task by ID

        Args:
            task_id (int): ID of the task to retrieve

        Returns:
            Task: The requested task

        Raises:
            KeyError: If task with given ID doesn't exist
        """
        if task_id not in self._tasks:
            raise KeyError(f"Task with ID {task_id} does not exist")
        return self._tasks[task_id]

    def update_task(self, task_id, title=None, description=None):
        """
        Update an existing task's title or description

        Args:
            task_id (int): ID of the task to update
            title (str, optional): New title for the task
            description (str, optional): New description for the task

        Returns:
            Task: The updated task

        Raises:
            KeyError: If task with given ID doesn't exist
            ValueError: If title is invalid
        """
        task = self.get_task(task_id)

        # Update task properties
        task.update(title=title, description=description)

        return task

    def delete_task(self, task_id):
        """
        Delete a task by ID

        Args:
            task_id (int): ID of the task to delete

        Returns:
            bool: True if task was deleted, False if task didn't exist

        Raises:
            KeyError: If task with given ID doesn't exist
        """
        if task_id not in self._tasks:
            raise KeyError(f"Task with ID {task_id} does not exist")

        # Get the task to delete
        task_to_delete = self._tasks[task_id]

        # Remove from dictionary
        del self._tasks[task_id]

        # Remove from list while preserving order
        self._task_list.remove(task_to_delete)

        return True

    def mark_complete(self, task_id, completed=True):
        """
        Mark a task as complete or incomplete

        Args:
            task_id (int): ID of the task to update
            completed (bool): Whether the task is completed (default: True)

        Returns:
            Task: The updated task

        Raises:
            KeyError: If task with given ID doesn't exist
        """
        task = self.get_task(task_id)
        task.completed = completed
        return task

    def toggle_completion(self, task_id):
        """
        Toggle the completion status of a task

        Args:
            task_id (int): ID of the task to toggle

        Returns:
            Task: The updated task

        Raises:
            KeyError: If task with given ID doesn't exist
        """
        task = self.get_task(task_id)
        task.toggle_completion()
        return task

    def has_tasks(self):
        """
        Check if there are any tasks

        Returns:
            bool: True if there are tasks, False otherwise
        """
        return len(self._task_list) > 0