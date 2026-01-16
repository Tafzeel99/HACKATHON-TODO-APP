# Todo Console Application - Phase I

This is the Phase I implementation of the Evolution of Todo project: a simple, in-memory Python console application for managing todo tasks.

## Features

This application provides the 5 basic todo features:

1. **Add Task** - Create new todo items with title and optional description
2. **View Task List** - Display all tasks with their status
3. **Update Task** - Modify existing task details
4. **Delete Task** - Remove tasks from the list
5. **Mark Task Complete/Incomplete** - Toggle task completion status

## Requirements

- Python 3.13 or higher

## How to Run

1. Clone or download this repository
2. Navigate to the project directory
3. Run the application:

```bash
python -m src.phase1.main
```

## Usage

The application provides a menu-driven interface:

- **Add Task**: Enter a title and optional description for a new task
- **View Tasks**: See all your tasks with their completion status
- **Update Task**: Modify the title or description of an existing task
- **Delete Task**: Remove a task by its ID
- **Mark Task Complete/Incomplete**: Update the status of a task
- **Help**: Get information about using the application
- **Exit**: Close the application

## Important Notes

- All data is stored in memory only and will be lost when the application closes
- This is a single-user application with no persistence beyond runtime
- This is Phase I of the Evolution of Todo project - more advanced features will be added in future phases

## Architecture

The application follows clean architecture principles:

- `src/phase1/models.py`: Defines the Task entity
- `src/phase1/task_manager.py`: Handles business logic and in-memory storage
- `src/phase1/cli.py`: Provides the command-line interface
- `src/phase1/main.py`: Application entry point
- `src/main.py`: Top-level entry point that delegates to phase1



