---
name: type-sync-generator
description: |
  Synchronize TypeScript interfaces with Python Pydantic models to ensure type consistency across frontend and backend.
---

# Type Sync Generator

Synchronize TypeScript interfaces with Python Pydantic models to ensure type consistency across frontend and backend.

## When to Use This Skill
- User has Pydantic models and needs matching TypeScript types
- User mentions type mismatches between frontend/backend
- User wants single source of truth for data models
- User needs to keep types in sync during development

## Procedure
1. **Locate Pydantic models**: Find backend data models
2. **Parse field types**: Extract field names, types, optional/required
3. **Convert to TypeScript**: Map Python types to TS equivalents
4. **Handle nested models**: Recursively convert related models
5. **Generate interfaces**: Create .ts file with all types

## Output Format
**Generated TypeScript**:
- Interface definitions matching Pydantic models
- Nested type references
- Optional fields marked with `?`
- Enums converted properly

## Quality Criteria
- Type mapping accuracy: str→string, int→number, datetime→string, etc.
- Optional fields handled: `Optional[str]` → `string | null`
- Lists converted: `List[User]` → `User[]`
- Enums preserved as TypeScript enums or union types
- Comments/descriptions carried over

## Example
**Input**: "Generate TypeScript types from my Pydantic models"

**Pydantic Models (Python)**:
```python
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"
    GUEST = "guest"

class Address(BaseModel):
    street: str
    city: str
    zip_code: str
    country: str = "USA"

class User(BaseModel):
    id: str
    email: str
    name: str
    age: Optional[int] = None
    role: Role
    address: Optional[Address] = None
    created_at: datetime
    tags: List[str] = []
```

**Generated TypeScript**:
```typescript
// types.ts
export enum Role {
  ADMIN = "admin",
  USER = "user",
  GUEST = "guest"
}

export interface Address {
  street: string;
  city: string;
  zip_code: string;
  country: string;
}

export interface User {
  id: string;
  email: string;
  name: string;
  age: number | null;
  role: Role;
  address: Address | null;
  created_at: string; // ISO datetime string
  tags: string[];
}
```

## Type Mapping Reference
```
Python              → TypeScript
str                 → string
int, float          → number
bool                → boolean
datetime, date      → string
List[T]             → T[]
Optional[T]         → T | null
Dict[str, T]        → Record<string, T>
Enum                → enum or union type
Any                 → any (avoid if possible)
```

## CLI Usage
```bash
# Generate types from Pydantic models
claude-code type-sync-generator \
  --models backend/models.py \
  --output frontend/src/types/api.ts

# Watch mode for development
claude-code type-sync-generator \
  --models backend/models.py \
  --output frontend/src/types/api.ts \
  --watch
```

## Automation
**pre-commit hook** (`.git/hooks/pre-commit`):
```bash
#!/bin/sh
# Auto-generate TypeScript types from Pydantic models
if git diff --cached --name-only | grep -qE '\.(py)$'; then
    echo "Checking for Pydantic model changes..."
    claude-code type-sync-generator \
        --models backend/models.py \
        --output frontend/src/types/api.ts
    git add frontend/src/types/api.ts
fi
```

## Python Parser Implementation
```python
# parsers/pydantic_parser.py
import ast
import inspect
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class FieldInfo:
    name: str
    type_hint: str
    optional: bool = False
    default_value: Any = None

@dataclass
class ModelInfo:
    name: str
    fields: List[FieldInfo]
    docstring: Optional[str] = None

def parse_pydantic_models(file_path: str) -> List[ModelInfo]:
    """Parse Pydantic models from Python file"""
    with open(file_path, 'r') as f:
        tree = ast.parse(f.read())

    models = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # Check if it's a Pydantic model
            if is_pydantic_model(node):
                model_info = parse_model_class(node)
                models.append(model_info)

    return models

def is_pydantic_model(class_node: ast.ClassDef) -> bool:
    """Check if class is a Pydantic model"""
    for base in class_node.bases:
        if isinstance(base, ast.Name) and base.id == 'BaseModel':
            return True
        elif isinstance(base, ast.Attribute) and base.attr == 'BaseModel':
            return True
    return False

def parse_model_class(class_node: ast.ClassDef) -> ModelInfo:
    """Parse a single Pydantic model class"""
    fields = []
    docstring = ast.get_docstring(class_node)

    for item in class_node.body:
        if isinstance(item, ast.AnnAssign):
            field_info = parse_field(item)
            fields.append(field_info)

    return ModelInfo(name=class_node.name, fields=fields, docstring=docstring)

def parse_field(assign_node: ast.AnnAssign) -> FieldInfo:
    """Parse a field assignment in Pydantic model"""
    field_name = assign_node.target.id
    type_annotation = ast.unparse(assign_node.annotation)

    # Check if field is optional
    is_optional = 'Optional[' in type_annotation or 'Union[' in type_annotation

    # Get default value if exists
    default_value = None
    if assign_node.value:
        try:
            default_value = ast.literal_eval(assign_node.value)
        except ValueError:
            default_value = ast.unparse(assign_node.value)

    return FieldInfo(
        name=field_name,
        type_hint=type_annotation,
        optional=is_optional,
        default_value=default_value
    )
```

## TypeScript Generator
```python
# generators/ts_generator.py
from typing import List
from parsers.pydantic_parser import ModelInfo, FieldInfo

def generate_typescript_interfaces(models: List[ModelInfo]) -> str:
    """Generate TypeScript interfaces from parsed models"""
    output = "// Auto-generated from Pydantic models\n\n"

    for model in models:
        output += generate_interface(model)

    return output

def generate_interface(model: ModelInfo) -> str:
    """Generate a single TypeScript interface"""
    interface_def = ""

    # Add docstring if available
    if model.docstring:
        interface_def += f"/** {model.docstring} */\n"

    interface_def += f"export interface {model.name} {{\n"

    for field in model.fields:
        ts_type = convert_python_type_to_ts(field.type_hint)
        optional_marker = "?" if field.optional else ""
        interface_def += f"  {field.name}{optional_marker}: {ts_type};\n"

    interface_def += "}\n\n"

    return interface_def

def convert_python_type_to_ts(python_type: str) -> str:
    """Convert Python type annotation to TypeScript type"""
    # Handle Optional[T] -> T | null
    if python_type.startswith('Optional['):
        inner_type = python_type[9:-1]  # Remove 'Optional[' and ']'
        return f"{convert_python_type_to_ts(inner_type)} | null"

    # Handle List[T] -> T[]
    if python_type.startswith('List['):
        inner_type = python_type[5:-1]  # Remove 'List[' and ']'
        return f"{convert_python_type_to_ts(inner_type)}[]"

    # Handle Union types
    if 'Union[' in python_type:
        # Simplified handling - in practice you'd need more sophisticated parsing
        pass

    # Basic type mappings
    type_map = {
        'str': 'string',
        'int': 'number',
        'float': 'number',
        'bool': 'boolean',
        'datetime': 'string',  # ISO date string
        'date': 'string',      # ISO date string
        'Any': 'any'
    }

    return type_map.get(python_type, python_type)
```

## Complete CLI Tool
```python
# cli/type_sync.py
import argparse
import os
from pathlib import Path
from parsers.pydantic_parser import parse_pydantic_models
from generators.ts_generator import generate_typescript_interfaces

def main():
    parser = argparse.ArgumentParser(description='Sync Pydantic models to TypeScript types')
    parser.add_argument('--models', required=True, help='Path to Python models file')
    parser.add_argument('--output', required=True, help='Output TypeScript file path')
    parser.add_argument('--watch', action='store_true', help='Watch mode')

    args = parser.parse_args()

    if not os.path.exists(args.models):
        print(f"Error: Models file {args.models} not found")
        return

    # Parse and generate
    models = parse_pydantic_models(args.models)
    ts_content = generate_typescript_interfaces(models)

    # Write output
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(ts_content)

    print(f"Generated {len(models)} TypeScript interfaces to {args.output}")

if __name__ == "__main__":
    main()
```

## Integration Examples

### With FastAPI
```python
# app/models.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    email: str
    name: str
    password: str

class User(BaseModel):
    id: str
    email: str
    name: str
    created_at: datetime
    is_active: bool = True

# After running type-sync-generator:
# Generated types.ts will contain matching TypeScript interfaces
```

### With React Component
```typescript
// components/UserProfile.tsx
import { User } from '../types/api';

interface UserProfileProps {
  user: User;  // This type comes from generated file
}

export const UserProfile: React.FC<UserProfileProps> = ({ user }) => {
  return (
    <div>
      <h1>{user.name}</h1>
      <p>Email: {user.email}</p>
      <p>Created: {new Date(user.created_at).toLocaleDateString()}</p>
    </div>
  );
};
```

## Advanced Features

### Handling Complex Types
```python
# models/complex.py
from pydantic import BaseModel
from typing import Optional, List, Dict, Union
from enum import Enum

class Status(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

class Metadata(BaseModel):
    tags: List[str]
    properties: Dict[str, str]

class ComplexEntity(BaseModel):
    id: str
    status: Status
    metadata: Optional[Metadata] = None
    scores: List[float]
    attributes: Union[str, Dict[str, str]]  # Union types
```

### Generic Type Support
```python
# generators/ts_generator.py (enhanced)
def convert_python_type_to_ts(python_type: str) -> str:
    """Enhanced type conversion with generic support"""
    # Handle Optional[T]
    if python_type.startswith('Optional['):
        inner_type = python_type[9:-1]
        return f"{convert_python_type_to_ts(inner_type)} | null"

    # Handle List[T]
    if python_type.startswith('List['):
        inner_type = python_type[5:-1]
        return f"{convert_python_type_to_ts(inner_type)}[]"

    # Handle Dict[str, T]
    if python_type.startswith('Dict[str, '):
        inner_type = python_type[9:-1]  # Remove 'Dict[str, ' and ']'
        return f"Record<string, {convert_python_type_to_ts(inner_type)}>"

    # Handle Union types
    if 'Union[' in python_type:
        # Extract types from Union[X, Y, Z]
        inner_types = python_type[6:-1]  # Remove 'Union[' and ']'
        types = [t.strip() for t in inner_types.split(',')]
        converted_types = [convert_python_type_to_ts(t) for t in types]
        return ' | '.join(converted_types)

    # Basic type mappings
    type_map = {
        'str': 'string',
        'int': 'number',
        'float': 'number',
        'bool': 'boolean',
        'datetime': 'string',
        'date': 'string',
        'Any': 'any'
    }

    return type_map.get(python_type, python_type)
```

## Error Handling
```python
# handlers/error_handler.py
class TypeSyncError(Exception):
    """Custom exception for type sync errors"""
    pass

def validate_compatibility(python_model: str, ts_interface: str) -> bool:
    """Validate that generated TypeScript is compatible with Python model"""
    # Implementation would compare field types and structures
    pass
```

## Best Practices
1. **Single source of truth**: Keep Pydantic models as the canonical type definition
2. **Automated generation**: Integrate into CI/CD pipeline
3. **Version compatibility**: Ensure TypeScript versions match Python types
4. **Documentation**: Preserve docstrings in generated interfaces
5. **Testing**: Verify generated types work with API responses
6. **Naming consistency**: Maintain consistent naming conventions

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing Pydantic models, TypeScript setup, project structure |
| **Conversation** | User's specific model structures, naming preferences, integration needs |
| **Skill References** | Pydantic type annotations, TypeScript type system, AST parsing |
| **User Guidelines** | Project-specific type mapping requirements, output location preferences |