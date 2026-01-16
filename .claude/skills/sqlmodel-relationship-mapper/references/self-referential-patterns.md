# Self-Referential Relationship Patterns

Implementation patterns for hierarchical and recursive relationships in SQLModel.

## Basic Self-Referential Relationships

### Parent-Child Structure
```python
from sqlmodel import SQLModel, Field, Relationship
from typing import List, Optional

class Category(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    parent_id: Optional[int] = Field(foreign_key="category.id", index=True)

    # Children categories
    children: List["Category"] = Relationship(
        back_populates="parent",
        sa_relationship_kwargs={
            "remote_side": "Category.id"  # Indicates this is a self-referential relationship
        }
    )

    # Parent category
    parent: Optional["Category"] = Relationship(back_populates="children")
```

### Tree Navigation
```python
# Example usage
def get_category_hierarchy(category: Category, session) -> dict:
    """Get full hierarchy of a category and its children"""
    result = {
        "id": category.id,
        "name": category.name,
        "children": []
    }

    for child in category.children:
        result["children"].append(get_category_hierarchy(child, session))

    return result

def get_root_categories(session) -> List[Category]:
    """Get all root categories (those without parents)"""
    statement = select(Category).where(Category.parent_id.is_(None))
    return session.exec(statement).all()
```

## Advanced Self-Referential Patterns

### Adjacency List Model
```python
class TreeNode(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    parent_id: Optional[int] = Field(foreign_key="treenode.id", index=True)
    level: int = Field(default=0)  # Track depth in the tree

    # Children nodes
    children: List["TreeNode"] = Relationship(
        back_populates="parent",
        sa_relationship_kwargs={
            "remote_side": "TreeNode.id"
        }
    )

    # Parent node
    parent: Optional["TreeNode"] = Relationship(back_populates="children")

    def get_path(self, session) -> List[str]:
        """Get the path from root to this node"""
        path = [self.name]
        current = self

        while current.parent:
            current = current.parent
            path.insert(0, current.name)

        return path
```

### Materialized Path Model
```python
class Node(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    path: str = Field(index=True)  # Store full path like "/root/sub1/sub2/"
    level: int = Field(default=0)

    @classmethod
    def create_node(cls, name: str, parent_path: Optional[str] = None):
        """Create a node with proper path"""
        path = parent_path or "/"
        path += f"{name}/"

        # Calculate level based on path depth
        level = path.count("/") - 1

        return cls(name=name, path=path, level=level)

    def get_children(self, session) -> List["Node"]:
        """Get direct children of this node"""
        child_path = f"{self.path}{self.name}/"
        statement = select(Node).where(
            Node.path.like(f"{child_path}%"),
            Node.level == self.level + 1
        )
        return session.exec(statement).all()
```

### Nested Set Model (Alternative Approach)
```python
class NestedCategory(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    left_bound: int = Field(index=True)   # Left boundary
    right_bound: int = Field(index=True)  # Right boundary
    level: int = Field(default=0)

    def is_descendant_of(self, other: "NestedCategory") -> bool:
        """Check if this node is a descendant of another"""
        return (self.left_bound > other.left_bound and
                self.right_bound < other.right_bound)

    def get_descendants(self, session) -> List["NestedCategory"]:
        """Get all descendants of this node"""
        statement = select(NestedCategory).where(
            NestedCategory.left_bound > self.left_bound,
            NestedCategory.right_bound < self.right_bound
        )
        return session.exec(statement).all()
```

## Complex Self-Referential Examples

### Organizational Hierarchy
```python
class Employee(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    position: str
    manager_id: Optional[int] = Field(foreign_key="employee.id", index=True)

    # Employees who report to this manager
    subordinates: List["Employee"] = Relationship(
        back_populates="manager",
        sa_relationship_kwargs={
            "remote_side": "Employee.id"
        }
    )

    # Manager of this employee
    manager: Optional["Employee"] = Relationship(back_populates="subordinates")

    def get_management_chain(self, session) -> List["Employee"]:
        """Get the management chain from CEO to this employee"""
        chain = [self]
        current = self

        while current.manager:
            current = current.manager
            chain.insert(0, current)

        return chain

    def get_all_subordinates(self, session) -> List["Employee"]:
        """Get all subordinates including indirect reports"""
        all_subs = []
        direct_subs = self.subordinates

        for sub in direct_subs:
            all_subs.append(sub)
            all_subs.extend(sub.get_all_subordinates(session))

        return all_subs
```

### Task Hierarchy (Like in Project Management)
```python
class Task(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    description: Optional[str] = None
    parent_task_id: Optional[int] = Field(foreign_key="task.id", index=True)
    priority: int = Field(default=1, ge=1, le=5)
    completed: bool = Field(default=False)

    # Subtasks of this task
    subtasks: List["Task"] = Relationship(
        back_populates="parent_task",
        sa_relationship_kwargs={
            "remote_side": "Task.id"
        }
    )

    # Parent task of this task
    parent_task: Optional["Task"] = Relationship(back_populates="subtasks")

    def get_full_path(self, session) -> List[str]:
        """Get the full task path from root task"""
        path = [self.title]
        current = self

        while current.parent_task:
            current = current.parent_task
            path.insert(0, current.title)

        return path

    def get_depth(self) -> int:
        """Calculate the depth of this task in the hierarchy"""
        depth = 0
        current = self

        while current.parent_task:
            depth += 1
            current = current.parent_task

        return depth

    def is_leaf_task(self) -> bool:
        """Check if this task has no subtasks"""
        return len(self.subtasks) == 0

    def calculate_completion_percentage(self, session) -> float:
        """Calculate completion percentage including subtasks"""
        all_tasks = [self]
        all_tasks.extend(self.get_all_subtasks(session))

        if not all_tasks:
            return 0.0

        completed_tasks = sum(1 for task in all_tasks if task.completed)
        return (completed_tasks / len(all_tasks)) * 100

    def get_all_subtasks(self, session) -> List["Task"]:
        """Get all subtasks recursively"""
        all_subtasks = []

        for subtask in self.subtasks:
            all_subtasks.append(subtask)
            all_subtasks.extend(subtask.get_all_subtasks(session))

        return all_subtasks
```

## Multi-Tenant Self-Referential Models

### Tenant-Isolated Hierarchical Data
```python
class TenantScopedModel(SQLModel, table=True):
    __abstract__ = True
    id: int = Field(default=None, primary_key=True)
    user_id: str = Field(index=True)

class Folder(TenantScopedModel, table=True):
    user_id: str = Field(foreign_key="user.id", index=True)
    name: str
    parent_folder_id: Optional[int] = Field(foreign_key="folder.id", index=True)

    # Subfolders
    subfolders: List["Folder"] = Relationship(
        back_populates="parent_folder",
        sa_relationship_kwargs={
            "remote_side": "Folder.id"
        }
    )

    # Parent folder
    parent_folder: Optional["Folder"] = Relationship(back_populates="subfolders")

    # Files in this folder
    files: List["File"] = Relationship(back_populates="folder")

    def get_full_path(self, session) -> str:
        """Get the full folder path for this user"""
        path_parts = [self.name]
        current = self

        while current.parent_folder:
            current = current.parent_folder
            path_parts.insert(0, current.name)

        return "/" + "/".join(path_parts)

class File(TenantScopedModel, table=True):
    user_id: str = Field(foreign_key="user.id", index=True)
    name: str
    folder_id: int = Field(foreign_key="folder.id", index=True)

    folder: Optional[Folder] = Relationship(back_populates="files")
```

## Querying Self-Referential Models

### Recursive Queries
```python
from sqlalchemy import text

def get_full_tree_recursive(root_id: int, session) -> List[dict]:
    """Get full tree structure using recursive CTE (PostgreSQL)"""
    query = text("""
        WITH RECURSIVE category_tree AS (
            -- Base case: start with the root category
            SELECT id, name, parent_id, 0 as level
            FROM category
            WHERE id = :root_id

            UNION ALL

            -- Recursive case: find children
            SELECT c.id, c.name, c.parent_id, ct.level + 1
            FROM category c
            JOIN category_tree ct ON c.parent_id = ct.id
        )
        SELECT * FROM category_tree
        ORDER BY level, name
    """)

    result = session.exec(query, {"root_id": root_id})
    return result.fetchall()

def get_all_descendants_iterative(node: TreeNode, session) -> List[TreeNode]:
    """Get all descendants using iterative approach"""
    descendants = []
    queue = [node]

    while queue:
        current = queue.pop(0)
        descendants.extend(current.children)
        queue.extend(current.children)

    return descendants
```

## Best Practices for Self-Referential Models

### Validation and Constraints
```python
from pydantic import model_validator

class ValidatedNode(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    parent_id: Optional[int] = Field(foreign_key="validatednode.id", index=True)

    children: List["ValidatedNode"] = Relationship(
        back_populates="parent",
        sa_relationship_kwargs={
            "remote_side": "ValidatedNode.id"
        }
    )
    parent: Optional["ValidatedNode"] = Relationship(back_populates="children")

    @model_validator(mode='after')
    def validate_no_circular_reference(self):
        """Prevent circular references during validation"""
        # This is a simplified check - full cycle detection would be more complex
        # and typically handled at the database level with triggers or application logic
        if self.id and self.parent_id and self.id == self.parent_id:
            raise ValueError("A node cannot be its own parent")
        return self
```

### Performance Considerations
```python
# For large trees, consider caching or limiting depth
def get_limited_tree(node_id: int, session, max_depth: int = 3) -> dict:
    """Get tree structure limited to a specific depth"""
    node = session.get(TreeNode, node_id)

    def _build_tree(current_node: TreeNode, current_depth: int) -> dict:
        result = {
            "id": current_node.id,
            "name": current_node.name,
            "level": current_node.level,
            "children": []
        }

        if current_depth < max_depth:
            for child in current_node.children:
                result["children"].append(_build_tree(child, current_depth + 1))

        return result

    return _build_tree(node, 0)
```

These patterns provide comprehensive approaches to implementing self-referential relationships in SQLModel, from basic parent-child structures to complex hierarchical models with proper validation and performance considerations.