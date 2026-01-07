"""
Main entry point for the Todo Console Application
"""

from .task_manager import TaskManager
from .cli import TodoCLI


def main():
    """
    Main function to run the Todo Console Application
    """
    # Initialize the task manager
    task_manager = TaskManager()

    # Initialize the CLI interface with the task manager
    cli = TodoCLI(task_manager)

    # Run the application
    cli.run()


if __name__ == "__main__":
    main()