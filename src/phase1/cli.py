"""
CLI Interface for the Todo Console Application
Implements the menu-driven interface and user input handling
"""

from .task_manager import TaskManager
from .colors import Colors, Styles, colored, bold, clear_screen


class TodoCLI:
    """
    Command-line interface for the Todo application
    """

    def __init__(self, task_manager):
        """
        Initialize the CLI interface

        Args:
            task_manager (TaskManager): The task manager instance to use
        """
        self.task_manager = task_manager

    def display_menu(self):
        """Display the main menu options with colors"""
        print(f"\n{Styles.HEADER}{'=' * 40}{Colors.RESET}")
        print(f"{Styles.HEADER}         TODO APP - MAIN MENU{Colors.RESET}")
        print(f"{Styles.HEADER}{'=' * 40}{Colors.RESET}")
        print(f"{Styles.MENU}1. Add Task{Colors.RESET}")
        print(f"{Styles.MENU}2. View Tasks{Colors.RESET}")
        print(f"{Styles.MENU}3. Update Task{Colors.RESET}")
        print(f"{Styles.MENU}4. Delete Task{Colors.RESET}")
        print(f"{Styles.MENU}5. Mark Task Complete/Incomplete{Colors.RESET}")
        print(f"{Styles.MENU}6. Help{Colors.RESET}")
        print(f"{Styles.MENU}7. Exit{Colors.RESET}")
        print(f"{Styles.HEADER}{'=' * 40}{Colors.RESET}")

    def get_user_choice(self):
        """
        Get and validate user menu choice

        Returns:
            str: The user's menu choice
        """
        try:
            choice = input(colored("Enter your choice (1-7): ", Colors.CYAN)).strip()
            if choice in ['1', '2', '3', '4', '5', '6', '7']:
                return choice
            else:
                print(colored("Invalid choice. Please enter a number between 1 and 7.", Colors.RED))
                return None
        except (EOFError, KeyboardInterrupt):
            print(colored("\nOperation cancelled.", Colors.YELLOW))
            return '7'  # Treat as exit

    def add_task(self):
        """Handle adding a new task with enhanced UI"""
        print(f"\n{Styles.SUBHEADER}{'─' * 30}{Colors.RESET}")
        print(f"{Styles.SUBHEADER}ADD NEW TASK{Colors.RESET}")
        print(f"{Styles.SUBHEADER}{'─' * 30}{Colors.RESET}")

        try:
            title = input(colored("Enter task title: ", Colors.YELLOW)).strip()
            if not title:
                print(colored("Error: Task title cannot be empty.", Colors.RED))
                return

            description = input(colored("Enter task description (optional, press Enter to skip): ", Colors.YELLOW)).strip()

            task = self.task_manager.add_task(title, description)
            print(colored(f"Task added successfully! ID: {task.id}", Colors.GREEN))

        except ValueError as e:
            print(colored(f"Error: {e}", Colors.RED))
        except Exception as e:
            print(colored(f"Unexpected error: {e}", Colors.RED))

    def view_tasks(self):
        """Handle viewing all tasks with enhanced UI"""
        print(f"\n{Styles.SUBHEADER}{'=' * 40}{Colors.RESET}")
        print(f"{Styles.SUBHEADER}{'TODO LIST':^40}{Colors.RESET}")
        print(f"{Styles.SUBHEADER}{'=' * 40}{Colors.RESET}")

        if not self.task_manager.has_tasks():
            print(colored("No tasks found. Your todo list is empty.", Colors.YELLOW))
            return

        tasks = self.task_manager.list_tasks()
        print(colored(f"Total tasks: {len(tasks)}", Colors.CYAN))
        print(colored("-" * 50, Colors.DIM))

        for i, task in enumerate(tasks, 1):
            # Show status indicator and task details
            status_indicator = "X" if task.completed else "O"
            status_color = Colors.GREEN if task.completed else Colors.RED
            id_text = f"[{task.id}]"

            # Print task with status indicator, ID and title
            task_line = f"{colored(status_indicator, status_color)} {colored(id_text, Colors.CYAN)} {task.title}"
            print(task_line)

            # Print description if it exists
            if task.description:
                print(colored(f"    {task.description}", Colors.DIM))

            # Print separator line between tasks (except for the last one)
            if i < len(tasks):
                print(colored("-" * 40, Colors.DIM))

    def update_task(self):
        """Handle updating an existing task with enhanced UI"""
        print(f"\n{Styles.SUBHEADER}{'-' * 30}{Colors.RESET}")
        print(f"{Styles.SUBHEADER}UPDATE TASK{Colors.RESET}")
        print(f"{Styles.SUBHEADER}{'-' * 30}{Colors.RESET}")

        if not self.task_manager.has_tasks():
            print(colored("No tasks found. Cannot update tasks.", Colors.YELLOW))
            return

        self.view_tasks()  # Show tasks first

        try:
            task_id = int(input(colored("Enter the ID of the task to update: ", Colors.YELLOW)))

            # Check if task exists
            try:
                current_task = self.task_manager.get_task(task_id)
                print(f"\n{colored('[VIEW] Current task:', Colors.CYAN)}")
                print(colored(current_task.detailed_str(), Colors.BRIGHT_WHITE))
            except KeyError:
                print(colored(f"❌ Error: Task with ID {task_id} does not exist.", Colors.RED))
                return

            title_input = input(colored(f"Enter new title (current: '{current_task.title}', press Enter to keep current): ", Colors.YELLOW)).strip()
            description_input = input(colored(f"Enter new description (current: '{current_task.description}', press Enter to keep current): ", Colors.YELLOW)).strip()

            # Prepare update parameters
            update_params = {}
            if title_input:
                update_params['title'] = title_input
            if description_input:
                update_params['description'] = description_input

            if not update_params:
                print(colored("No changes made.", Colors.BLUE))
                return

            # Update the task
            updated_task = self.task_manager.update_task(task_id, **update_params)
            print(colored(f"Task updated successfully!", Colors.GREEN))
            print(colored(f"Updated task: {updated_task}", Colors.BRIGHT_WHITE))

        except ValueError:
            print(colored("Error: Please enter a valid task ID (number).", Colors.RED))
        except KeyError as e:
            print(colored(f"Error: {e}", Colors.RED))
        except Exception as e:
            print(colored(f"Unexpected error: {e}", Colors.RED))

    def delete_task(self):
        """Handle deleting a task with enhanced UI"""
        print(f"\n{Styles.SUBHEADER}{'-' * 30}{Colors.RESET}")
        print(f"{Styles.SUBHEADER}DELETE TASK{Colors.RESET}")
        print(f"{Styles.SUBHEADER}{'-' * 30}{Colors.RESET}")

        if not self.task_manager.has_tasks():
            print(colored("No tasks found. Cannot delete tasks.", Colors.YELLOW))
            return

        self.view_tasks()  # Show tasks first

        try:
            task_id = int(input(colored("Enter the ID of the task to delete: ", Colors.YELLOW)))

            try:
                task = self.task_manager.get_task(task_id)
                print(f"\n{colored('You are about to delete:', Colors.RED)}")
                print(colored(f"{task}", Colors.BRIGHT_WHITE))

                confirm = input(colored("Are you sure? (y/N): ", Colors.RED)).strip().lower()
                if confirm in ['y', 'yes']:
                    self.task_manager.delete_task(task_id)
                    print(colored(f"Task with ID {task_id} deleted successfully!", Colors.GREEN))
                else:
                    print(colored("Task deletion cancelled.", Colors.BLUE))

            except KeyError:
                print(colored(f"❌ Error: Task with ID {task_id} does not exist.", Colors.RED))

        except ValueError:
            print(colored("❌ Error: Please enter a valid task ID (number).", Colors.RED))
        except Exception as e:
            print(colored(f"❌ Unexpected error: {e}", Colors.RED))

    def mark_task_completion(self):
        """Handle marking a task as complete/incomplete with enhanced UI"""
        print(f"\n{Styles.SUBHEADER}{'─' * 30}{Colors.RESET}")
        print(f"{Styles.SUBHEADER}MARK TASK COMPLETE/INCOMPLETE{Colors.RESET}")
        print(f"{Styles.SUBHEADER}{'─' * 30}{Colors.RESET}")

        if not self.task_manager.has_tasks():
            print(colored("No tasks found. Cannot mark tasks.", Colors.YELLOW))
            return

        self.view_tasks()  # Show tasks first

        try:
            task_id = int(input(colored("Enter the ID of the task to update: ", Colors.YELLOW)))

            try:
                current_task = self.task_manager.get_task(task_id)
                print(f"\n{colored('Current task:', Colors.CYAN)}")
                print(colored(f"{current_task}", Colors.BRIGHT_WHITE))

                status_choice = input(colored("Mark as (1) Complete or (2) Incomplete? Enter 1 or 2: ", Colors.YELLOW)).strip()

                if status_choice == '1':
                    self.task_manager.mark_complete(task_id, completed=True)
                    print(colored(f"Task marked as complete!", Colors.GREEN))
                elif status_choice == '2':
                    self.task_manager.mark_complete(task_id, completed=False)
                    print(colored(f"Task marked as incomplete!", Colors.BLUE))
                else:
                    print(colored("❌ Invalid choice. Please enter 1 for Complete or 2 for Incomplete.", Colors.RED))

            except KeyError:
                print(colored(f"❌ Error: Task with ID {task_id} does not exist.", Colors.RED))

        except ValueError:
            print(colored("❌ Error: Please enter a valid task ID (number).", Colors.RED))
        except Exception as e:
            print(colored(f"❌ Unexpected error: {e}", Colors.RED))

    def show_help(self):
        """Display help information with enhanced UI"""
        print(f"\n{Styles.SUBHEADER}{'─' * 30}{Colors.RESET}")
        print(f"{Styles.SUBHEADER}HELP & INFORMATION{Colors.RESET}")
        print(f"{Styles.SUBHEADER}{'─' * 30}{Colors.RESET}")
        print(colored("This is a simple todo application with the following features:", Colors.BRIGHT_WHITE))
        print()
        print(colored("1. Add Task:", Colors.CYAN) + colored(" Create a new task with a title and optional description", Colors.WHITE))
        print(colored("2. View Tasks:", Colors.CYAN) + colored(" Display all tasks with their ID, title, and status", Colors.WHITE))
        print(colored("3. Update Task:", Colors.CYAN) + colored(" Modify the title or description of an existing task", Colors.WHITE))
        print(colored("4. Delete Task:", Colors.CYAN) + colored(" Remove a task from your list", Colors.WHITE))
        print(colored("5. Mark Task Complete/Incomplete:", Colors.CYAN) + colored(" Update the completion status of a task", Colors.WHITE))
        print(colored("6. Help:", Colors.CYAN) + colored(" Show this help message", Colors.WHITE))
        print(colored("7. Exit:", Colors.CYAN) + colored(" Close the application", Colors.WHITE))
        print()
        print(colored("Tips:", Colors.YELLOW))
        print(colored("- Each task has a unique ID that's assigned automatically", Colors.WHITE))
        print(colored("- Tasks are stored in memory only and will be lost when the application closes", Colors.WHITE))
        print(colored("- You can mark tasks as complete to track your progress", Colors.WHITE))

    def run(self):
        """Run the main application loop with enhanced UI"""
        print(colored("Welcome to the Enhanced Todo Console Application!", Colors.BOLD + Colors.BRIGHT_GREEN))
        print(colored("Your productivity companion awaits...", Colors.BRIGHT_BLUE))

        while True:
            self.display_menu()
            choice = self.get_user_choice()

            if choice is None:
                continue  # Invalid choice, show menu again

            if choice == '1':
                self.add_task()
            elif choice == '2':
                self.view_tasks()
            elif choice == '3':
                self.update_task()
            elif choice == '4':
                self.delete_task()
            elif choice == '5':
                self.mark_task_completion()
            elif choice == '6':
                self.show_help()
            elif choice == '7':
                print(f"\n{colored('Thank you for using the Todo Console Application!', Colors.BRIGHT_GREEN)}")
                print(colored("Have a productive day!", Colors.BRIGHT_BLUE))
                break

            # Pause to let user see the result before showing menu again
            input(colored("\nPress Enter to continue...", Colors.CYAN))