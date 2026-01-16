# Database Normalization Rules

Detailed guidelines for applying normalization principles to database schema design.

## First Normal Form (1NF)
- Each column contains atomic (indivisible) values
- Each record is unique
- Each column has a unique name
- No repeating groups or arrays in columns

### Implementation in SQLModel:
```python
# Correct - atomic values
title: str = Field(max_length=200)  # Single string value

# Incorrect - would violate 1NF
tags: List[str] = Field(default_factory=list)  # This would require separate table
```

## Second Normal Form (2NF)
- Must satisfy 1NF requirements
- All non-key attributes must be fully functional dependent on the primary key
- Eliminate partial dependencies

### Example:
```python
# Violates 2NF - department_name depends only on department_id, not employee_id
class EmployeeBad(SQLModel, table=True):
    employee_id: int = Field(primary_key=True)
    department_id: int
    department_name: str  # This should be in a separate table
    employee_name: str

# Correct - satisfies 2NF
class Department(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str

class Employee(SQLModel, table=True):
    id: int = Field(primary_key=True)
    department_id: int = Field(foreign_key="department.id")
    name: str
```

## Third Normal Form (3NF)
- Must satisfy 2NF requirements
- Eliminate transitive dependencies (non-key attributes depending on other non-key attributes)
- All attributes must depend only on the primary key

### Example:
```python
# Violates 3NF - city depends on state, not directly on address
class AddressBad(SQLModel, table=True):
    id: int = Field(primary_key=True)
    street: str
    city: str
    state: str
    city_population: int  # City population depends on city, not address

# Correct - satisfies 3NF
class State(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    population: int

class City(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    state_id: int = Field(foreign_key="state.id")
    population: int

class Address(SQLModel, table=True):
    id: int = Field(primary_key=True)
    street: str
    city_id: int = Field(foreign_key="city.id")
```

## Practical Normalization Guidelines

### When to Denormalize
- For read-heavy applications where query performance is critical
- When complex joins significantly impact performance
- For analytical workloads where aggregations are frequent
- Always measure performance impact before denormalizing

### Multi-Tenant Considerations
- User isolation should not violate normalization principles
- Tenant ID fields are legitimate foreign keys
- Avoid duplicating tenant data across multiple tables unnecessarily

### Indexing and Normalization
- Proper normalization often reduces the need for complex indexes
- Normalized schemas typically perform better with standard indexing strategies
- Consider query patterns when designing normalized schemas