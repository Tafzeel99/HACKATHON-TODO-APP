---
name: test-coverage-analyzer
description: |
  Identify untested code paths and generate coverage reports. Use when users need to improve test coverage.
---

# Test Coverage Analyzer

Identify untested code paths and generate coverage reports.

## When to Use
- User asks about "test coverage" or "untested code"
- User needs coverage report
- User wants to identify missing tests

## Procedure
1. **Run coverage**: Execute tests with coverage tool
2. **Generate report**: HTML, terminal, or XML format
3. **Identify gaps**: Find untested functions/lines
4. **Prioritize**: Focus on critical paths first
5. **Write tests**: Cover identified gaps

## Coverage Tools

### Pytest with Coverage
```bash
# Install
pip install pytest-cov

# Run tests with coverage
pytest --cov=app --cov-report=html --cov-report=term

# Coverage for specific module
pytest --cov=app.services --cov-report=term-missing

# Fail if coverage below threshold
pytest --cov=app --cov-fail-under=80

# Generate XML for CI/CD
pytest --cov=app --cov-report=xml
```

### Coverage Configuration
```ini
# setup.cfg or pyproject.toml
[tool:pytest]
addopts =
    --cov=app
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80

[coverage:run]
source = app
omit =
    */tests/*
    */migrations/*
    */__pycache__/*
    */venv/*

[coverage:report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
    if TYPE_CHECKING:
    @abstractmethod
```

## Coverage Reports

### Terminal Report
```bash
$ pytest --cov=app --cov-report=term-missing

----------- coverage: platform linux, python 3.11.2 -----------
Name                    Stmts   Miss  Cover   Missing
-----------------------------------------------------
app/__init__.py             2      0   100%
app/api/users.py           45      5    89%   23-27, 34
app/api/auth.py            32      0   100%
app/models/user.py         28      3    89%   45-47
app/services/email.py      18      8    56%   12-19
app/utils/validation.py    15      0   100%
-----------------------------------------------------
TOTAL                     140     16    89%
```

### HTML Report Analysis
```python
# Generate HTML report
pytest --cov=app --cov-report=html

# Open htmlcov/index.html
# Red lines: Not covered
# Green lines: Covered
# Yellow lines: Partially covered (branches)
```

## Finding Untested Code

### Identify Critical Gaps
```python
# coverage_analysis.py
import coverage
import ast

def analyze_coverage():
    """Find critical untested code"""
    cov = coverage.Coverage()
    cov.load()

    # Get analysis
    analysis = cov.analysis2('app/api/users.py')
    executed = set(analysis[1])
    missing = set(analysis[2])

    # Find critical functions without coverage
    with open('app/api/users.py') as f:
        tree = ast.parse(f.read())

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if node.lineno in missing:
                print(f"⚠️  Untested function: {node.name} (line {node.lineno})")

# Output:
# ⚠️  Untested function: delete_user (line 67)
# ⚠️  Untested function: reset_password (line 89)
```

### Branch Coverage
```python
# Check both if/else paths are tested
def process_payment(amount):
    if amount > 0:
        return charge_card(amount)  # Covered ✓
    else:
        return refund(amount)        # Not covered ✗

# Need test for negative amount
def test_refund_negative_amount():
    result = process_payment(-50)
    assert result.type == "refund"
```

## Coverage-Driven Test Generation

### Auto-Generate Test Stubs
```python
# generate_tests.py
import ast
import inspect

def generate_test_stubs(module_path):
    """Generate test stubs for untested functions"""

    with open(module_path) as f:
        tree = ast.parse(f.read())

    test_stubs = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            # Skip private functions
            if node.name.startswith('_'):
                continue

            # Generate test stub
            stub = f"""
def test_{node.name}():
    '''Test {node.name} function'''
    # TODO: Implement test
    # Arrange

    # Act
    result = {node.name}()

    # Assert
    assert result is not None
"""
            test_stubs.append(stub)

    return "\n".join(test_stubs)

# Usage
stubs = generate_test_stubs('app/services/user_service.py')
with open('tests/test_user_service_generated.py', 'w') as f:
    f.write(stubs)
```

### Priority Matrix
```python
# prioritize_testing.py

def calculate_test_priority(function_name, metrics):
    """Calculate testing priority based on metrics"""
    score = 0

    # Complexity (higher = more important)
    score += metrics['cyclomatic_complexity'] * 2

    # Called frequency
    score += metrics['call_count']

    # Critical path
    if metrics['is_critical']:
        score += 10

    # Has external dependencies
    if metrics['has_dependencies']:
        score += 5

    return score

# Example output:
"""
Priority Queue:
1. process_payment (score: 23) - CRITICAL
2. create_user (score: 18)
3. send_email (score: 12)
4. format_date (score: 3)
"""
```

## CI/CD Integration

### GitHub Actions
```yaml
# .github/workflows/coverage.yml
name: Test Coverage

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install pytest pytest-cov

    - name: Run tests with coverage
      run: |
        pytest --cov=app --cov-report=xml --cov-report=term

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        fail_ci_if_error: true

    - name: Check coverage threshold
      run: |
        pytest --cov=app --cov-fail-under=80
```

### Coverage Badge
```markdown
# README.md
[![Coverage](https://codecov.io/gh/username/repo/branch/main/graph/badge.svg)](https://codecov.io/gh/username/repo)
```

## Missing Test Patterns

### Untested Error Paths
```python
# Current: Only happy path tested
def create_user(email, password):
    user = User(email=email)
    user.set_password(password)
    db.add(user)
    db.commit()
    return user

# Missing tests:
def test_create_user_duplicate_email():
    """Test duplicate email handling"""
    pass

def test_create_user_invalid_password():
    """Test password validation"""
    pass

def test_create_user_database_error():
    """Test database failure handling"""
    pass
```

### Untested Edge Cases
```python
# Function with untested boundaries
def calculate_discount(total, customer_tier):
    if total > 1000:
        return 0.2  # Tested ✓
    elif total > 500:
        return 0.1  # Not tested ✗
    return 0        # Not tested ✗

# Add tests:
def test_discount_boundary_500():
    assert calculate_discount(500, "basic") == 0
    assert calculate_discount(501, "basic") == 0.1

def test_discount_boundary_1000():
    assert calculate_discount(1000, "basic") == 0.1
    assert calculate_discount(1001, "basic") == 0.2
```

## Coverage Improvement Plan

### Step-by-Step Process
```markdown
## Coverage Improvement Plan

### Current State
- Overall coverage: 68%
- Critical paths: 45% coverage
- API endpoints: 85% coverage
- Business logic: 52% coverage

### Goals
- Target: 80% overall coverage
- Critical paths: 95%
- Timeline: 2 weeks

### Week 1: Critical Paths
- [ ] Payment processing (priority: CRITICAL)
- [ ] User authentication (priority: HIGH)
- [ ] Data validation (priority: HIGH)

### Week 2: General Coverage
- [ ] Utility functions
- [ ] Helper methods
- [ ] Edge cases

### Execution
1. Run coverage: `pytest --cov=app --cov-report=html`
2. Review htmlcov/index.html
3. Prioritize uncovered critical code
4. Write tests for red/yellow sections
5. Re-run coverage and verify improvement
6. Repeat until target reached
```

## Coverage Exemptions
```python
# Mark code that should not be included in coverage

def debug_only_function():
    """This function is only used for debugging"""
    import pdb; pdb.set_trace()  # pragma: no cover

class DevelopmentConfig:
    DEBUG = True  # pragma: no cover
    SECRET_KEY = "dev-key"  # pragma: no cover

if __name__ == "__main__":  # pragma: no cover
    # This code is only executed when run directly
    app.run(debug=True)
```

## Best Practices
1. **Focus on critical paths**: Prioritize business logic over utility functions
2. **Measure branch coverage**: Ensure both if/else paths are tested
3. **Test error conditions**: Don't just test happy paths
4. **Set reasonable thresholds**: 80% is often sufficient
5. **Review regularly**: Check coverage reports during development
6. **Exclude appropriately**: Mark debug/dev-only code with exemptions
7. **Track progress**: Monitor coverage trends over time

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing test suite, coverage tools, project structure |
| **Conversation** | User's specific coverage goals, current coverage metrics |
| **Skill References** | Standard coverage tools, best practices for testing |
| **User Guidelines** | Project-specific requirements, acceptable coverage thresholds |