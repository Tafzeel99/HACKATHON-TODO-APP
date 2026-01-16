---
name: seed-data-creator
description: |
  Generates development database seeding scripts for testing and development.
  Creates realistic sample data for SQLModel models including users, tasks, relationships,
  and various data scenarios for comprehensive application testing.
---

# Seed Data Creator

Generates database seeding scripts for development and testing.

## What This Skill Does
- Creates realistic sample data for SQLModel models
- Generates seed scripts for development databases
- Implements data factories for repeatable seeding
- Creates various test scenarios (edge cases, typical usage)
- Seeds relational data with proper foreign keys
- Provides data reset/cleanup functionality
- Supports different data volumes (small, medium, large)

## What This Skill Does NOT Do
- Migrate production data
- Design database schema (use schema-designer)
- Generate migration files (use migration-generator)
- Create production-ready user accounts

## Before Implementation

| Source | Gather |
|--------|--------|
| **Codebase** | SQLModel models, database session setup, existing seed data patterns |
| **Conversation** | Required data scenarios, data volume needs, specific test cases |
| **Skill References** | Realistic data generation patterns, faker library usage |
| **User Guidelines** | Development/testing requirements, data privacy considerations |

## Required Clarifications

Ask about USER'S requirements:

1. **Data Volume**: "How many records do you need for each entity (users, tasks, etc.)?"
2. **Scenarios**: "What specific scenarios do you want to test (edge cases, typical usage)?"
3. **Relationships**: "Should seed data include related entities (tasks with projects, tags)?"

## Implementation Workflow

1. **Analyze Models**
   - Identify all SQLModel entities
   - Map relationships and foreign keys
   - List required vs optional fields

2. **Design Seed Data**
   - Plan realistic sample data
   - Define data scenarios (small, medium, large datasets)
   - Create edge cases for testing

3. **Implement Seed Script**
   - Create data factory functions
   - Generate sample records
   - Handle relationships and foreign keys
   - Add data cleanup function

4. **Test Seed Script**
   - Run on fresh database
   - Verify data integrity
   - Check relationship correctness

## Basic Seed Script Template
```python
# seed.py
from sqlmodel import Session, create_engine, select
from models import User, Task, Project, Tag, TaskTagLink
from datetime import datetime, timedelta
import random

# Database connection
DATABASE_URL = "postgresql://localhost/todo_dev"
engine = create_engine(DATABASE_URL)


def clear_database(session: Session):
    """Clear all existing data"""
    print("🧹 Clearing database...")

    # Delete in order (respect foreign keys)
    session.exec(select(TaskTagLink)).delete()
    session.exec(select(Task)).delete()
    session.exec(select(Tag)).delete()
    session.exec(select(Project)).delete()
    session.exec(select(User)).delete()

    session.commit()
    print("✓ Database cleared")


def seed_users(session: Session, count: int = 3) -> list[User]:
    """Create sample users"""
    print(f"👤 Creating {count} users...")

    users = [
        User(id="user_1", email="alice@example.com", name="Alice Johnson"),
        User(id="user_2", email="bob@example.com", name="Bob Smith"),
        User(id="user_3", email="charlie@example.com", name="Charlie Brown"),
    ][:count]

    for user in users:
        session.add(user)

    session.commit()
    print(f"✓ Created {len(users)} users")
    return users


def seed_projects(session: Session, users: list[User]) -> list[Project]:
    """Create sample projects for users"""
    print("📁 Creating projects...")

    project_names = [
        ("Work", "Professional tasks and projects"),
        ("Personal", "Personal life and hobbies"),
        ("Learning", "Study and skill development"),
        ("Home", "House maintenance and chores"),
    ]

    projects = []
    for user in users:
        for name, description in project_names[:2]:  # 2 projects per user
            project = Project(
                user_id=user.id,
                name=name,
                description=description,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
            )
            session.add(project)
            projects.append(project)

    session.commit()
    print(f"✓ Created {len(projects)} projects")
    return projects


def seed_tasks(session: Session, users: list[User], projects: list[Project]) -> list[Task]:
    """Create sample tasks for users"""
    print("📝 Creating tasks...")
    task_templates = [
        ("Buy groceries", "Milk, eggs, bread, vegetables"),
        ("Finish project report", "Complete quarterly analysis"),
        ("Call dentist", "Schedule checkup appointment"),
        ("Read book", "Finish 'Clean Code' chapter 5"),
        ("Exercise", "30 minutes cardio"),
        ("Review pull requests", "Check team's code submissions"),
        ("Plan vacation", "Research destinations and book flights"),
        ("Pay bills", "Utilities and credit card"),
        ("Clean garage", "Organize tools and equipment"),
        ("Learn Python", "Complete tutorial on async/await"),
    ]

    tasks = []
    for user in users:
        user_projects = [p for p in projects if p.user_id == user.id]

        for i, (title, description) in enumerate(task_templates):
            task = Task(
                user_id=user.id,
                project_id=random.choice(user_projects).id if user_projects and random.random() > 0.3 else None,
                title=title,
                description=description if random.random() > 0.3 else None,
                completed=random.random() < 0.4,  # 40% completed
                priority=random.choice(["low", "medium", "high"]),
                due_date=datetime.utcnow() + timedelta(days=random.randint(-5, 30)),
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 60)),
                updated_at=datetime.utcnow() - timedelta(days=random.randint(0, 10))
            )
            session.add(task)
            tasks.append(task)

    session.commit()
    print(f"✓ Created {len(tasks)} tasks")
    return tasks


def seed_tags(session: Session) -> list[Tag]:
    """Create sample tags"""
    print("🏷️  Creating tags...")
    tag_names = ["urgent", "important", "work", "personal", "shopping", "health", "learning"]

    tags = []
    for name in tag_names:
        tag = Tag(name=name)
        session.add(tag)
        tags.append(tag)

    session.commit()
    print(f"✓ Created {len(tags)} tags")
    return tags


def seed_task_tags(session: Session, tasks: list[Task], tags: list[Tag]):
    """Link tasks with tags"""
    print("🔗 Linking tasks with tags...")
    links_created = 0
    for task in tasks:
        # Assign 0-3 random tags to each task
        num_tags = random.randint(0, 3)
        task_tags = random.sample(tags, num_tags)

        for tag in task_tags:
            link = TaskTagLink(task_id=task.id, tag_id=tag.id)
            session.add(link)
            links_created += 1

    session.commit()
    print(f"✓ Created {links_created} task-tag links")


def main():
    """Main seeding function"""
    print("🌱 Starting database seeding...\n")
    with Session(engine) as session:
        # Clear existing data
        clear_database(session)

        # Seed data in order
        users = seed_users(session, count=3)
        projects = seed_projects(session, users)
        tasks = seed_tasks(session, users, projects)
        tags = seed_tags(session)
        seed_task_tags(session, tasks, tags)

    print("\n✅ Database seeding complete!")
    print(f"   Users: {len(users)}")
    print(f"   Projects: {len(projects)}")
    print(f"   Tasks: {len(tasks)}")
    print(f"   Tags: {len(tags)}")


if __name__ == "__main__":
    main()
```

## Using Faker for Realistic Data
```python
from faker import Faker

fake = Faker()

def seed_realistic_users(session: Session, count: int = 10) -> list[User]:
    """Create realistic users with Faker"""
    users = []

    for _ in range(count):
        user = User(
            id=f"user_{fake.uuid4()}",
            email=fake.email(),
            name=fake.name(),
            created_at=fake.date_time_between(start_date="-1y", end_date="now")
        )
        session.add(user)
        users.append(user)

    session.commit()
    return users


def seed_realistic_tasks(session: Session, users: list[User], count: int = 50) -> list[Task]:
    """Create realistic tasks with Faker"""
    tasks = []

    task_verbs = ["Complete", "Review", "Update", "Fix", "Implement", "Research", "Plan"]
    task_objects = ["report", "documentation", "bug", "feature", "design", "strategy"]

    for _ in range(count):
        task = Task(
            user_id=random.choice(users).id,
            title=f"{random.choice(task_verbs)} {random.choice(task_objects)}",
            description=fake.paragraph(),
            completed=fake.boolean(chance_of_getting_true=30),
            priority=random.choice(["low", "medium", "high"]),
            due_date=fake.date_time_between(start_date="-7d", end_date="+30d"),
            created_at=fake.date_time_between(start_date="-60d", end_date="now"),
            updated_at=fake.date_time_between(start_date="-10d", end_date="now")
        )
        session.add(task)
        tasks.append(task)

    session.commit()
    return tasks
```

## Test Scenarios

### Edge Cases Seed Data
```python
def seed_edge_cases(session: Session, user: User):
    """Create edge case scenarios for testing"""

    # Very long title (near max length)
    long_task = Task(
        user_id=user.id,
        title="A" * 190 + " test task",
        description="Testing max title length",
        completed=False
    )

    # Task with no description
    minimal_task = Task(
        user_id=user.id,
        title="Minimal task",
        description=None,
        completed=False
    )

    # Overdue task
    overdue_task = Task(
        user_id=user.id,
        title="Overdue task",
        description="This is past due date",
        completed=False,
        due_date=datetime.utcnow() - timedelta(days=10)
    )

    # Task due today
    today_task = Task(
        user_id=user.id,
        title="Due today",
        description="Should complete today",
        completed=False,
        due_date=datetime.utcnow()
    )

    # Completed task with old date
    old_completed = Task(
        user_id=user.id,
        title="Old completed task",
        description="Completed 6 months ago",
        completed=True,
        created_at=datetime.utcnow() - timedelta(days=180),
        updated_at=datetime.utcnow() - timedelta(days=180)
    )

    session.add_all([long_task, minimal_task, overdue_task, today_task, old_completed])
    session.commit()
```

## CLI Seed Script
```python
# seed_cli.py
import typer
from rich.console import Console

app = typer.Typer()
console = Console()


@app.command()
def seed(
    users: int = typer.Option(3, help="Number of users to create"),
    tasks_per_user: int = typer.Option(10, help="Tasks per user"),
    clear: bool = typer.Option(True, help="Clear database before seeding")
):
    """Seed the database with sample data"""
    with Session(engine) as session:
        if clear:
            clear_database(session)

        users = seed_users(session, count=users)
        projects = seed_projects(session, users)
        # ... continue seeding

        console.print("[green]✓ Database seeded successfully![/green]")


@app.command()
def clear():
    """Clear all data from database"""
    with Session(engine) as session:
        clear_database(session)
        console.print("[yellow]⚠ Database cleared[/yellow]")


if __name__ == "__main__":
    app()
```

**Usage:**
```bash
# Seed with defaults
python seed_cli.py seed

# Custom counts
python seed_cli.py seed --users 5 --tasks-per-user 20

# Clear only
python seed_cli.py clear
```

## Output Checklist

Before delivering seed script:
- [ ] Seed script creates realistic sample data
- [ ] Foreign keys properly linked
- [ ] Different data volumes supported (small/medium/large)
- [ ] Edge cases included for testing
- [ ] Clear/reset function implemented
- [ ] Script is idempotent (can run multiple times)
- [ ] Progress logging included
- [ ] CLI interface provided (optional)
- [ ] Documentation includes usage examples

## Python Implementation

```python
import random
from datetime import datetime, timedelta
from typing import List, Optional
from sqlmodel import Session, select
from faker import Faker

class SeedDataCreator:
    def __init__(self, session: Session, models_module=None):
        self.session = session
        self.fake = Faker()
        self.models = models_module or {}
        self.created_entities = {}

    def clear_database(self, ordered_models: List = None):
        """Clear all existing data in proper order to respect foreign keys"""
        print("🧹 Clearing database...")

        if ordered_models:
            # Clear in specified order
            for model in reversed(ordered_models):
                self.session.exec(select(model)).delete()
        else:
            # If no order specified, just clear all models we know about
            for model_name, model in self.models.items():
                try:
                    self.session.exec(select(model)).delete()
                except Exception:
                    # Skip if model doesn't exist in DB yet
                    continue

        self.session.commit()
        print("✓ Database cleared")

    def create_users(self, count: int = 5) -> List:
        """Create sample users"""
        if 'User' not in self.models:
            print("⚠ User model not found, skipping user creation")
            return []

        User = self.models['User']
        users = []

        for i in range(count):
            user = User(
                id=f"user_{self.fake.uuid4()}",
                email=self.fake.email(),
                name=self.fake.name(),
                created_at=self.fake.date_time_between(start_date="-1y", end_date="now")
            )
            self.session.add(user)
            users.append(user)

        self.session.commit()
        self.created_entities['users'] = users
        print(f"✓ Created {len(users)} users")
        return users

    def create_tasks(self, users: List, count_per_user: int = 10) -> List:
        """Create sample tasks for users"""
        if 'Task' not in self.models:
            print("⚠ Task model not found, skipping task creation")
            return []

        Task = self.models['Task']
        tasks = []

        task_verbs = ["Complete", "Review", "Update", "Fix", "Implement", "Research", "Plan", "Test", "Deploy", "Document"]
        task_objects = ["report", "documentation", "bug", "feature", "design", "strategy", "analysis", "test", "integration", "refactor"]

        for user in users:
            for _ in range(count_per_user):
                task = Task(
                    user_id=getattr(user, 'id', getattr(user, 'user_id', None)),
                    title=f"{random.choice(task_verbs)} {random.choice(task_objects)}",
                    description=self.fake.paragraph() if random.random() > 0.3 else None,
                    completed=self.fake.boolean(chance_of_getting_true=30),
                    priority=random.choice(["low", "medium", "high"]),
                    due_date=self.fake.date_time_between(start_date="-7d", end_date="+30d") if random.random() > 0.2 else None,
                    created_at=self.fake.date_time_between(start_date="-60d", end_date="now"),
                    updated_at=self.fake.date_time_between(start_date="-10d", end_date="now")
                )

                if hasattr(task, 'project_id'):
                    # If task has project relationship, assign randomly
                    projects = self.created_entities.get('projects', [])
                    if projects and random.random() > 0.5:
                        task.project_id = random.choice(projects).id

                self.session.add(task)
                tasks.append(task)

        self.session.commit()
        self.created_entities['tasks'] = tasks
        print(f"✓ Created {len(tasks)} tasks")
        return tasks

    def create_projects(self, users: List, projects_per_user: int = 2) -> List:
        """Create sample projects for users"""
        if 'Project' not in self.models:
            print("⚠ Project model not found, skipping project creation")
            return []

        Project = self.models['Project']
        projects = []

        project_names = [
            ("Work", "Professional tasks and projects"),
            ("Personal", "Personal life and hobbies"),
            ("Learning", "Study and skill development"),
            ("Health", "Fitness and wellness goals"),
            ("Finance", "Budget and financial planning"),
            ("Home", "House maintenance and chores"),
        ]

        for user in users:
            for i in range(projects_per_user):
                name, description = project_names[i % len(project_names)]
                project = Project(
                    user_id=getattr(user, 'id', getattr(user, 'user_id', None)),
                    name=f"{name}_{i+1}",
                    description=description,
                    created_at=self.fake.date_time_between(start_date="-1y", end_date="now")
                )
                self.session.add(project)
                projects.append(project)

        self.session.commit()
        self.created_entities['projects'] = projects
        print(f"✓ Created {len(projects)} projects")
        return projects

    def create_tags(self, count: int = 7) -> List:
        """Create sample tags"""
        if 'Tag' not in self.models:
            print("⚠ Tag model not found, skipping tag creation")
            return []

        Tag = self.models['Tag']
        tag_names = ["urgent", "important", "work", "personal", "shopping", "health", "learning", "meeting", "deadline", "follow-up"]

        tags = []
        for i in range(min(count, len(tag_names))):
            tag = Tag(name=tag_names[i])
            self.session.add(tag)
            tags.append(tag)

        self.session.commit()
        self.created_entities['tags'] = tags
        print(f"✓ Created {len(tags)} tags")
        return tags

    def create_relationships(self):
        """Create relationships between entities if they exist"""
        tasks = self.created_entities.get('tasks', [])
        tags = self.created_entities.get('tags', [])

        if 'TaskTagLink' in self.models and tasks and tags:
            TaskTagLink = self.models['TaskTagLink']
            links_created = 0

            for task in tasks:
                # Assign 0-2 random tags to each task
                num_tags = random.randint(0, min(2, len(tags)))
                task_tags = random.sample(tags, num_tags)

                for tag in task_tags:
                    link = TaskTagLink(task_id=task.id, tag_id=tag.id)
                    self.session.add(link)
                    links_created += 1

            self.session.commit()
            print(f"✓ Created {links_created} task-tag relationships")

    def generate_seed_data(
        self,
        user_count: int = 3,
        tasks_per_user: int = 10,
        projects_per_user: int = 2,
        tag_count: int = 7,
        clear_first: bool = True
    ) -> dict:
        """Generate complete seed data"""
        print("🌱 Starting database seeding...\n")

        if clear_first:
            self.clear_database()

        # Create entities in order
        users = self.create_users(user_count)
        projects = self.create_projects(users, projects_per_user) if users else []
        tasks = self.create_tasks(users, tasks_per_user) if users else []
        tags = self.create_tags(tag_count)

        # Create relationships
        self.create_relationships()

        summary = {
            'users': len(users),
            'projects': len(projects),
            'tasks': len(tasks),
            'tags': len(tags)
        }

        print(f"\n✅ Database seeding complete!")
        for entity, count in summary.items():
            print(f"   {entity.capitalize()}: {count}")

        return summary


def create_seed_script(
    user_count: int = 3,
    tasks_per_user: int = 10,
    projects_per_user: int = 2,
    tag_count: int = 7,
    clear_first: bool = True,
    model_imports: str = "from models import User, Task, Project, Tag"
) -> str:
    """
    Generate a complete seed script as a string

    Args:
        user_count: Number of users to create
        tasks_per_user: Number of tasks per user
        projects_per_user: Number of projects per user
        tag_count: Number of tags to create
        clear_first: Whether to clear database before seeding
        model_imports: Import statements for models
    """
    script_content = f'''#!/usr/bin/env python3
"""
Database Seeding Script
Automatically generated seed data for development and testing.
"""

{model_imports}
from sqlmodel import Session, create_engine, select
from datetime import datetime, timedelta
import random
from faker import Faker

fake = Faker()

DATABASE_URL = "sqlite:///./test.db"  # Change to your database URL
engine = create_engine(DATABASE_URL)


def clear_database(session: Session):
    """Clear all existing data respecting foreign key constraints"""
    print("🧹 Clearing database...")

    # Delete in reverse order of dependencies
    session.exec(select(TaskTagLink)).delete() if "TaskTagLink" in globals() else None
    session.exec(select(Task)).delete()
    session.exec(select(Tag)).delete()
    session.exec(select(Project)).delete()
    session.exec(select(User)).delete()

    session.commit()
    print("✓ Database cleared")


def seed_users(session: Session, count: int = {user_count}) -> list:
    """Create sample users"""
    print(f"👤 Creating {{count}} users...")

    users = []
    for i in range(count):
        user = User(
            id=f"user_{{fake.uuid4()}}",
            email=fake.email(),
            name=fake.name(),
            created_at=fake.date_time_between(start_date="-1y", end_date="now")
        )
        session.add(user)
        users.append(user)

    session.commit()
    print(f"✓ Created {{len(users)}} users")
    return users


def seed_projects(session: Session, users: list, projects_per_user: int = {projects_per_user}) -> list:
    """Create sample projects for users"""
    print("📁 Creating projects...")

    project_names = [
        ("Work", "Professional tasks and projects"),
        ("Personal", "Personal life and hobbies"),
        ("Learning", "Study and skill development"),
        ("Health", "Fitness and wellness goals"),
        ("Finance", "Budget and financial planning"),
        ("Home", "House maintenance and chores"),
    ]

    projects = []
    for user in users:
        for i in range(projects_per_user):
            name, description = project_names[i % len(project_names)]
            project = Project(
                user_id=getattr(user, 'id', getattr(user, 'user_id', None)),
                name=f"{{name}}_{{i+1}}",
                description=description,
                created_at=fake.date_time_between(start_date="-1y", end_date="now")
            )
            session.add(project)
            projects.append(project)

    session.commit()
    print(f"✓ Created {{len(projects)}} projects")
    return projects


def seed_tasks(session: Session, users: list, tasks_per_user: int = {tasks_per_user}) -> list:
    """Create sample tasks for users"""
    print("📝 Creating tasks...")

    task_verbs = ["Complete", "Review", "Update", "Fix", "Implement", "Research", "Plan", "Test", "Deploy", "Document"]
    task_objects = ["report", "documentation", "bug", "feature", "design", "strategy", "analysis", "test", "integration", "refactor"]

    tasks = []
    for user in users:
        for _ in range(tasks_per_user):
            task = Task(
                user_id=getattr(user, 'id', getattr(user, 'user_id', None)),
                title=f"{{random.choice(task_verbs)}} {{random.choice(task_objects)}}",
                description=fake.paragraph() if random.random() > 0.3 else None,
                completed=fake.boolean(chance_of_getting_true=30),
                priority=random.choice(["low", "medium", "high"]),
                due_date=fake.date_time_between(start_date="-7d", end_date="+30d") if random.random() > 0.2 else None,
                created_at=fake.date_time_between(start_date="-60d", end_date="now"),
                updated_at=fake.date_time_between(start_date="-10d", end_date="now")
            )

            # If task has project relationship, assign randomly
            if hasattr(task, 'project_id') and "projects" in locals():
                if projects and random.random() > 0.5:
                    task.project_id = random.choice(projects).id

            session.add(task)
            tasks.append(task)

    session.commit()
    print(f"✓ Created {{len(tasks)}} tasks")
    return tasks


def seed_tags(session: Session, count: int = {tag_count}) -> list:
    """Create sample tags"""
    print("🏷️  Creating tags...")
    tag_names = ["urgent", "important", "work", "personal", "shopping", "health", "learning", "meeting", "deadline", "follow-up"]

    tags = []
    for i in range(min(count, len(tag_names))):
        tag = Tag(name=tag_names[i])
        session.add(tag)
        tags.append(tag)

    session.commit()
    print(f"✓ Created {{len(tags)}} tags")
    return tags


def main():
    """Main seeding function"""
    print("🌱 Starting database seeding...")

    with Session(engine) as session:
        {"clear_database(session)" if clear_first else "# Clear database skipped"}

        users = seed_users(session, count={user_count})
        projects = seed_projects(session, users, projects_per_user={projects_per_user}) if users else []
        tasks = seed_tasks(session, users, tasks_per_user={tasks_per_user}) if users else []
        tags = seed_tags(session, count={tag_count})

    print("\\n✅ Database seeding complete!")


if __name__ == "__main__":
    main()
'''

    return script_content


def create_seed_data_skill(
    user_count: int = 3,
    tasks_per_user: int = 10,
    projects_per_user: int = 2,
    tag_count: int = 7,
    clear_first: bool = True,
    model_imports: str = "from models import User, Task, Project, Tag"
) -> str:
    """
    Main function to create seed data script.

    Args:
        user_count: Number of users to create
        tasks_per_user: Number of tasks per user
        projects_per_user: Number of projects per user
        tag_count: Number of tags to create
        clear_first: Whether to clear database before seeding
        model_imports: Import statements for models
    """
    script = create_seed_script(
        user_count=user_count,
        tasks_per_user=tasks_per_user,
        projects_per_user=projects_per_user,
        tag_count=tag_count,
        clear_first=clear_first,
        model_imports=model_imports
    )

    print(f"Seed script generated with:")
    print(f"- {user_count} users")
    print(f"- {tasks_per_user} tasks per user")
    print(f"- {projects_per_user} projects per user")
    print(f"- {tag_count} tags")
    print(f"- Clear database first: {clear_first}")

    return script


# Example usage:
# seed_script = create_seed_data_skill(
#     user_count=5,
#     tasks_per_user=15,
#     projects_per_user=3,
#     tag_count=10
# )
```

## Usage Examples

### Basic Seed Generation
```python
seed_script = create_seed_data_skill(
    user_count=3,
    tasks_per_user=10,
    projects_per_user=2,
    tag_count=7
)
```

### Large Dataset for Testing
```python
seed_script = create_seed_data_skill(
    user_count=50,
    tasks_per_user=20,
    projects_per_user=5,
    tag_count=15
)
```

### Minimal Dataset
```python
seed_script = create_seed_data_skill(
    user_count=1,
    tasks_per_user=5,
    projects_per_user=1,
    tag_count=3
)
```

## Best Practices

- Always clear database before seeding in development
- Use realistic data that reflects actual usage patterns
- Include edge cases in your seed data for thorough testing
- Make seed scripts idempotent (safe to run multiple times)
- Document the data volume and scenarios covered by your seeds