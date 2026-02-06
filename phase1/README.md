# Phase I - Todo Console Application

A simple, in-memory Python console application for managing todo tasks.

## Features

This application provides the 5 basic todo features:

1. **Add Task** - Create new todo items with title and optional description
2. **View Task List** - Display all tasks with their status
3. **Update Task** - Modify existing task details
4. **Delete Task** - Remove tasks from the list
5. **Mark Task Complete/Incomplete** - Toggle task completion status

## Requirements

- Python 3.13 or higher (or Python 3.8+)

## How to Run

### Option 1: From Phase 1 Directory (Recommended)

```bash
cd phase1
python -m src.main
```

### Option 2: From Project Root

```bash
python -m phase1.src.main
```

### Option 3: Direct Execution

```bash
cd phase1/src
python main.py
```

## Quick Start

```bash
# Navigate to phase1 directory
cd phase1

# Run the application
python -m src.main
```

You'll see the main menu:
```
========================================
         TODO APP - MAIN MENU
========================================
1. Add Task
2. View Tasks
3. Update Task
4. Delete Task
5. Mark Task Complete/Incomplete
6. Help
7. Exit
========================================
```

## Architecture

The application follows clean architecture principles:

- `src/models.py` - Defines the Task entity
- `src/task_manager.py` - Handles business logic and in-memory storage
- `src/cli.py` - Provides the command-line interface
- `src/colors.py` - Terminal color formatting
- `src/main.py` - Application entry point

## Running Tests

To run the tests:

```bash
cd phase1
python src/tests/test_app.py
```

## Important Notes

- All data is stored in memory only and will be lost when the application closes
- This is a single-user application with no persistence beyond runtime
- This is Phase I of the Evolution of Todo project - more advanced features will be added in future phases

## Troubleshooting

**Error: "No module named 'src'"**
- Make sure you're in the `phase1` directory when running `python -m src.main`
- Or use the full path: `python -m phase1.src.main` from project root

**Error: "ModuleNotFoundError: No module named 'colors'"**
- This usually means you're trying to run `python src/main.py` directly
- Use `python -m src.main` instead from the phase1 directory

**Error: Import errors**
- Make sure all files have execute permissions
- Check that Python 3.8+ is installed: `python --version`

## Next Phase

Phase II will add:
- Web interface with Next.js
- FastAPI backend
- PostgreSQL database
- User authentication
- And much more!

---

**Built with Python 3.13 using AI-Native Development principles**
