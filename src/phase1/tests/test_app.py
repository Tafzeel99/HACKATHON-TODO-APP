"""
Test script to verify the Todo Console Application functionality
"""
from src.phase1.models import Task
from src.phase1.task_manager import TaskManager


def test_task_creation():
    """Test Task model functionality"""
    print("Testing Task creation...")

    # Test basic task creation
    task = Task(1, "Test Task", "This is a test description")
    assert task.id == 1
    assert task.title == "Test Task"
    assert task.description == "This is a test description"
    assert task.completed == False
    print("PASS: Basic task creation works")

    # Test task completion toggle
    task.toggle_completion()
    assert task.completed == True
    print("PASS: Task completion toggle works")

    # Test task update
    task.update(title="Updated Task", description="Updated description")
    assert task.title == "Updated Task"
    assert task.description == "Updated description"
    print("PASS: Task update works")

    # Test validation
    try:
        Task(2, "", "Empty title should fail")
        assert False, "Empty title should raise ValueError"
    except ValueError:
        print("PASS: Title validation works")

    try:
        Task(3, "A" * 201, "Too long title should fail")
        assert False, "Too long title should raise ValueError"
    except ValueError:
        print("PASS: Title length validation works")


def test_task_manager():
    """Test TaskManager functionality"""
    print("\nTesting TaskManager...")

    tm = TaskManager()

    # Test adding tasks
    task1 = tm.add_task("First Task", "Description 1")
    task2 = tm.add_task("Second Task", "Description 2")
    assert len(tm.list_tasks()) == 2
    assert task1.id == 1
    assert task2.id == 2
    print("PASS: Task addition works")

    # Test getting specific task
    retrieved_task = tm.get_task(1)
    assert retrieved_task.title == "First Task"
    print("PASS: Task retrieval works")

    # Test updating task
    updated_task = tm.update_task(1, title="Updated First Task")
    assert updated_task.title == "Updated First Task"
    print("PASS: Task update works")

    # Test marking complete
    completed_task = tm.mark_complete(1, completed=True)
    assert completed_task.completed == True
    print("PASS: Mark complete works")

    # Test toggling completion
    tm.toggle_completion(1)
    assert tm.get_task(1).completed == False
    print("PASS: Toggle completion works")

    # Test deletion
    tm.delete_task(2)
    assert len(tm.list_tasks()) == 1
    print("PASS: Task deletion works")

    # Test error handling
    try:
        tm.get_task(999)  # Non-existent task
        assert False, "Should raise KeyError"
    except KeyError:
        print("PASS: Error handling for non-existent tasks works")


if __name__ == "__main__":
    print("Running tests for Todo Console Application...")

    test_task_creation()
    test_task_manager()

    print("\nAll tests passed! The application is working correctly.")