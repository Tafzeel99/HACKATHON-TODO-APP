# Phase I - Todo Console Application

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

1. Navigate to the project root directory
2. Run the application:

```bash
python -m src.main
```

Or run the Phase 1 application directly:

```bash
python -m src.phase1.main
```

## Architecture

The application follows clean architecture principles:

- `src/phase1/models.py`: Defines the Task entity
- `src/phase1/task_manager.py`: Handles business logic and in-memory storage
- `src/phase1/cli.py`: Provides the command-line interface
- `src/phase1/main.py`: Application entry point

## Running Tests

To run the tests for Phase I:

```bash
python src/phase1/tests/test_app.py
```

## Important Notes

- All data is stored in memory only and will be lost when the application closes
- This is a single-user application with no persistence beyond runtime
- This is Phase I of the Evolution of Todo project - more advanced features will be added in future phases