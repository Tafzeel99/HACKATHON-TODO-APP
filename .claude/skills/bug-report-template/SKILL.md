---
name: bug-report-template
description: |
  Generate standardized bug reports with reproducible steps. Use when users need to document issues.
---

# Bug Report Template

Generate standardized bug reports with reproducible steps.

## When to Use
- User asks to "report a bug" or "document an issue"
- User needs bug tracking template
- User wants reproducible bug documentation

## Procedure
1. **Title**: Clear, specific description
2. **Environment**: OS, version, dependencies
3. **Steps to reproduce**: Exact sequence
4. **Expected vs Actual**: What should happen vs what does
5. **Evidence**: Logs, screenshots, stack traces

## Bug Report Templates

### Standard Bug Report
```markdown
## Bug Report: [Short Description]

### Priority
- [ ] Critical (system down, data loss)
- [ ] High (major feature broken)
- [ ] Medium (feature partially working)
- [ ] Low (minor issue, workaround exists)

### Environment
- **OS**: Ubuntu 22.04 / macOS 13.0 / Windows 11
- **Python Version**: 3.11.2
- **Framework**: FastAPI 0.104.1
- **Database**: PostgreSQL 15.2
- **Browser** (if applicable): Chrome 120.0

### Description
Clear and concise description of the bug.

### Steps to Reproduce
1. Go to user registration page
2. Fill in email: test@example.com
3. Fill in password: Test123!
4. Click "Sign Up" button
5. Observe error message

### Expected Behavior
User should be registered and redirected to dashboard with success message.

### Actual Behavior
Server returns 500 Internal Server Error. No user is created in database.

### Error Logs
```
Traceback (most recent call last):
  File "/app/api/users.py", line 45, in create_user
    user = User(**user_data)
  File "/app/models/user.py", line 23, in __init__
    self.password_hash = hash_password(password)
KeyError: 'password'
```

### Screenshots
[Attach screenshot of error page]

### Additional Context
- Issue started after deploying version 1.2.3
- Only affects new registrations, existing users can login
- Reproduced on both dev and staging environments

### Possible Fix
The `password` field is not being passed to the User model constructor.
Should map `password_data` to `password` before creating user instance.

### Related Issues
- #234 (Similar validation error)
- #189 (User registration refactor)
```

### API Bug Report
```markdown
## API Bug: POST /api/users returns 500 on valid input

### Endpoint
`POST /api/users`

### Request
```bash
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "SecurePass123!",
    "name": "Test User"
  }'
```

### Expected Response
```json
{
  "id": 1,
  "email": "test@example.com",
  "name": "Test User",
  "created_at": "2024-01-15T10:30:00Z"
}
```
**Status Code**: 201 Created

### Actual Response
```json
{
  "detail": "Internal server error"
}
```
**Status Code**: 500 Internal Server Error

### Server Logs
```
ERROR:    Exception in ASGI application
Traceback (most recent call last):
  File "app/api/users.py", line 32, in create_user
    db.add(user)
sqlalchemy.exc.IntegrityError: duplicate key value violates unique constraint "users_email_key"
```

### Root Cause
Email uniqueness check is missing before attempting to insert user.

### Suggested Fix
```python
# Add before db.add(user)
existing_user = db.query(User).filter(User.email == email).first()
if existing_user:
    raise HTTPException(status_code=409, detail="Email already registered")
```

### Impact
- New users cannot register if email exists
- Returns 500 instead of meaningful error
- No validation feedback to user
```

### Database Bug Report
```markdown
## Database Migration Failed: duplicate column "created_at"

### Migration File
`migrations/versions/abc123_add_timestamps.py`

### Command
```bash
alembic upgrade head
```

### Error
```
sqlalchemy.exc.ProgrammingError: (psycopg2.errors.DuplicateColumn)
column "created_at" of relation "users" already exists

[SQL: ALTER TABLE users ADD COLUMN created_at TIMESTAMP]
```

### Investigation
1. Checked current schema: `created_at` column exists
2. Checked migration history: Previous migration already added it
3. Issue: Migration file doesn't check if column exists

### Fix
```python
# Option 1: Check if column exists
from sqlalchemy import inspect

def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [col['name'] for col in inspector.get_columns('users')]

    if 'created_at' not in columns:
        op.add_column('users', sa.Column('created_at', sa.DateTime()))

# Option 2: Create new migration that checks state
# Option 3: Rollback and recreate migration
```

### Workaround
1. Manually remove duplicate column addition from migration
2. Run: `alembic stamp head` to mark as complete
3. Create new migration for any remaining changes
```

### Performance Bug Report
```markdown
## Performance: /api/users endpoint timeout after 30s

### Issue
User list endpoint times out when fetching all users.

### Metrics
- **Response Time**: >30 seconds (timeout)
- **Users in DB**: 50,000
- **Query**: `SELECT * FROM users`
- **N+1 Queries**: Yes (fetching related posts for each user)

### Reproduction
```bash
curl http://localhost:8000/api/users
# Waits 30 seconds, then timeout
```

### Database Query Analysis
```sql
-- Current query (runs 50,000 times)
SELECT * FROM posts WHERE author_id = 1;
SELECT * FROM posts WHERE author_id = 2;
...

-- Should be:
SELECT users.*, posts.*
FROM users
LEFT JOIN posts ON users.id = posts.author_id;
```

### Solution
```python
# Before (N+1 problem)
users = db.query(User).all()
for user in users:
    user.posts  # Triggers separate query

# After (eager loading)
from sqlalchemy.orm import joinedload

users = db.query(User).options(
    joinedload(User.posts)
).all()
```

### Performance Impact
- Before: 30+ seconds, timeout
- After: <200ms
- Queries reduced: 50,000 → 1

### Additional Optimizations
1. Add pagination: `?page=1&limit=20`
2. Add indexes on foreign keys
3. Cache frequently accessed data
4. Return only necessary fields (exclude posts if not needed)
```

## Issue Templates for GitHub

### Bug Report Template
```yaml
name: Bug Report
description: Report a bug to help us improve
labels: ["bug", "needs-triage"]
body:
  - type: markdown
    attributes:
      value: |
        Thanks for reporting this bug! Please fill out the sections below.

  - type: dropdown
    id: priority
    attributes:
      label: Priority
      options:
        - Critical
        - High
        - Medium
        - Low
    validations:
      required: true

  - type: input
    id: version
    attributes:
      label: Version
      description: What version are you running?
      placeholder: "1.2.3"
    validations:
      required: true

  - type: textarea
    id: description
    attributes:
      label: Bug Description
      description: Clear description of the bug
    validations:
      required: true

  - type: textarea
    id: reproduction
    attributes:
      label: Steps to Reproduce
      description: Step-by-step instructions
      placeholder: |
        1. Go to...
        2. Click on...
        3. See error
    validations:
      required: true

  - type: textarea
    id: expected
    attributes:
      label: Expected Behavior
      description: What should happen?
    validations:
      required: true

  - type: textarea
    id: actual
    attributes:
      label: Actual Behavior
      description: What actually happens?
    validations:
      required: true

  - type: textarea
    id: logs
    attributes:
      label: Error Logs
      description: Paste any relevant logs
      render: shell

  - type: textarea
    id: context
    attributes:
      label: Additional Context
      description: Anything else we should know?
```

## Automated Bug Detection

### Test Failure Report
```python
# conftest.py
import pytest

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Generate bug report on test failure"""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        # Generate bug report
        bug_report = f"""
## Test Failure: {item.name}

### Test Location
File: {item.fspath}
Line: {item.location[1]}

### Failure Details
{report.longreprtext}

### Test Code
```python
{item.function.__doc__ or "No docstring"}
```

### Environment
- Python: {sys.version}
- Pytest: {pytest.__version__}

### Timestamp
{datetime.now().isoformat()}
        """

        # Save to file
        with open(f"bug_reports/{item.name}.md", "w") as f:
            f.write(bug_report)
```

## Best Practices
1. **Clear title**: Describe the issue concisely
2. **Reproducible steps**: Anyone should be able to reproduce
3. **Evidence**: Include logs, screenshots, data
4. **Environment**: Specify versions and setup
5. **Expected vs Actual**: Be explicit about the problem
6. **Minimal example**: Reduce to simplest case
7. **One issue per report**: Don't combine multiple bugs
8. **Follow up**: Update with new findings

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing issue tracking system, bug report formats, project conventions |
| **Conversation** | User's specific bug reporting needs, tracking tools used |
| **Skill References** | Standard bug report templates, best practices for issue documentation |
| **User Guidelines** | Project-specific requirements, priority levels, categorization |