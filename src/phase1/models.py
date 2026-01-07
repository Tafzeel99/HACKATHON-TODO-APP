"""
Task model for the Todo Console Application
Implements the Task class with required attributes and validation
"""
from .colors import Colors, colored



class Task:
    """
    Represents a single todo item with ID, title, description, and completion status
    """

    def __init__(self, task_id, title, description="", completed=False):
        """
        Initialize a new Task

        Args:
            task_id (int): Unique identifier for the task
            title (str): Title of the task (1-200 characters)
            description (str, optional): Description of the task (up to 1000 characters)
            completed (bool): Completion status of the task (default: False)
        """
        self.id = task_id
        self.title = self._validate_title(title)
        self.description = self._validate_description(description)
        self.completed = completed

    def _validate_title(self, title):
        """Validate the task title (1-200 characters)"""
        if not isinstance(title, str):
            raise ValueError("Title must be a string")
        if not title or len(title.strip()) == 0:
            raise ValueError("Title cannot be empty")
        if len(title) > 200:
            raise ValueError("Title cannot exceed 200 characters")
        return title.strip()

    def _validate_description(self, description):
        """Validate the task description (up to 1000 characters)"""
        if not isinstance(description, str):
            raise ValueError("Description must be a string")
        if len(description) > 1000:
            raise ValueError("Description cannot exceed 1000 characters")
        return description

    def update(self, title=None, description=None):
        """
        Update task properties

        Args:
            title (str, optional): New title for the task
            description (str, optional): New description for the task
        """
        if title is not None:
            self.title = self._validate_title(title)
        if description is not None:
            self.description = self._validate_description(description)

    def toggle_completion(self):
        """Toggle the completion status of the task"""
        self.completed = not self.completed

    def __str__(self):
        """String representation of the task for display"""
        if self.completed:
            status = colored("[DONE]", Colors.GREEN)
            title_display = f"[{self.title}]"  # Bracket around completed tasks
        else:
            status = colored("[TODO]", Colors.YELLOW)
            title_display = self.title
        return f"{status} {self.id}. {title_display}"

    def detailed_str(self):
        """Detailed string representation of the task"""
        status = colored("Completed", Colors.GREEN) if self.completed else colored("Pending", Colors.YELLOW)
        result = f"ID: {self.id}\n"
        result += f"Title: {self.title}\n"
        result += f"Description: {self.description if self.description else '(No description)'}\n"
        result += f"Status: {status}\n"
        return result