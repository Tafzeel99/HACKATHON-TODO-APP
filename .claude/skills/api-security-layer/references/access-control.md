# Access Control Guide

This guide covers access control patterns and authorization in FastAPI applications.

## Role-Based Access Control (RBAC)

### Basic Role Implementation
```python
from enum import Enum
from typing import List, Optional
from fastapi import Depends, HTTPException, status
from pydantic import BaseModel

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    MODERATOR = "moderator"
    GUEST = "guest"

class User(BaseModel):
    id: str
    email: str
    roles: List[UserRole]
    permissions: List[str]

# Role-based dependency
def require_role(role: UserRole):
    """
    Dependency that checks if user has a specific role
    """
    async def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_roles = current_user.get("roles", [])

        if role.value not in user_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: {role.value} role required"
            )

        return current_user

    return role_checker

# Multiple roles required
def require_any_role(*roles: UserRole):
    """
    Dependency that checks if user has any of the specified roles
    """
    async def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_roles = current_user.get("roles", [])
        required_roles = [role.value for role in roles]

        if not any(user_role in required_roles for user_role in user_roles):
            role_names = [role.value for role in roles]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: One of [{', '.join(role_names)}] role required"
            )

        return current_user

    return role_checker

def require_all_roles(*roles: UserRole):
    """
    Dependency that checks if user has all specified roles
    """
    async def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_roles = current_user.get("roles", [])
        required_roles = [role.value for role in roles]

        for required_role in required_roles:
            if required_role not in user_roles:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied: {required_role} role required"
                )

        return current_user

    return role_checker

# Usage examples
@app.post("/admin/users")
async def create_user(current_user: dict = Depends(require_role(UserRole.ADMIN))):
    return {"message": "User created by admin"}

@app.put("/content")
async def update_content(current_user: dict = Depends(require_any_role(UserRole.ADMIN, UserRole.MODERATOR))):
    return {"message": "Content updated"}

@app.delete("/sensitive-data")
async def delete_sensitive_data(current_user: dict = Depends(require_all_roles(UserRole.ADMIN, UserRole.MODERATOR))):
    return {"message": "Sensitive data deleted"}
```

### Role Hierarchy
```python
from typing import Dict

class RoleHierarchy:
    """
    Define role hierarchy where higher roles inherit permissions of lower roles
    """
    HIERARCHY: Dict[UserRole, List[UserRole]] = {
        UserRole.ADMIN: [UserRole.MODERATOR, UserRole.USER, UserRole.GUEST],
        UserRole.MODERATOR: [UserRole.USER, UserRole.GUEST],
        UserRole.USER: [UserRole.GUEST],
        UserRole.GUEST: []
    }

    @classmethod
    def can_access(cls, user_role: UserRole, required_role: UserRole) -> bool:
        """
        Check if user role can access resource requiring a specific role
        """
        if user_role == required_role:
            return True

        return required_role in cls.HIERARCHY.get(user_role, [])

def require_role_hierarchy(required_role: UserRole):
    """
    Dependency that checks role hierarchy
    """
    async def role_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_role_str = current_user.get("role", "guest")
        user_role = UserRole(user_role_str)

        if not RoleHierarchy.can_access(user_role, required_role):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: {required_role.value} role or higher required"
            )

        return current_user

    return role_checker
```

## Attribute-Based Access Control (ABAC)

### Permission-Based Access
```python
from typing import Set

class Permission(str, Enum):
    READ_USERS = "read:users"
    WRITE_USERS = "write:users"
    DELETE_USERS = "delete:users"
    READ_TASKS = "read:tasks"
    WRITE_TASKS = "write:tasks"
    DELETE_TASKS = "delete:tasks"

def require_permission(permission: Permission):
    """
    Dependency that checks if user has a specific permission
    """
    async def permission_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_permissions = current_user.get("permissions", [])

        if permission.value not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: {permission.value} permission required"
            )

        return current_user

    return permission_checker

def require_any_permission(*permissions: Permission):
    """
    Dependency that checks if user has any of the specified permissions
    """
    async def permission_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_permissions = current_user.get("permissions", [])
        required_perms = [perm.value for perm in permissions]

        if not any(perm in user_permissions for perm in required_perms):
            perm_names = [perm.value for perm in permissions]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied: One of [{', '.join(perm_names)}] permission required"
            )

        return current_user

    return permission_checker

# Usage
@app.get("/users")
async def list_users(current_user: dict = Depends(require_permission(Permission.READ_USERS))):
    return {"users": []}

@app.post("/users")
async def create_user(current_user: dict = Depends(require_permission(Permission.WRITE_USERS))):
    return {"message": "User created"}
```

## Ownership-Based Access Control

### Resource Ownership Verification
```python
def verify_resource_ownership(resource_owner_id: str):
    """
    Verify that the authenticated user owns the resource
    """
    async def ownership_checker(current_user: dict = Depends(get_current_user)) -> dict:
        authenticated_user_id = current_user.get("sub")  # or however user ID is stored

        if authenticated_user_id != resource_owner_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You do not own this resource"
            )

        return current_user

    return ownership_checker

def verify_user_access(user_id: str):
    """
    Verify that the authenticated user can access the specified user_id
    """
    async def access_checker(current_user: dict = Depends(get_current_user)) -> dict:
        authenticated_user_id = current_user.get("sub")

        # User can access their own resources
        if authenticated_user_id == user_id:
            return current_user

        # Admins can access any user's resources
        user_roles = current_user.get("roles", [])
        if "admin" in user_roles:
            return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You can only access your own resources"
        )

    return access_checker

# Usage in endpoints
@app.get("/api/{user_id}/tasks")
async def get_user_tasks(
    user_id: str,
    current_user: dict = Depends(verify_user_access)
):
    return {"tasks": [], "user_id": user_id}

@app.put("/api/{user_id}/tasks/{task_id}")
async def update_task(
    user_id: str,
    task_id: str,
    current_user: dict = Depends(verify_user_access)
):
    # Verify task belongs to user
    task = get_task_by_id(task_id)
    if task.owner_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return {"message": "Task updated"}
```

## Policy-Based Access Control

### Complex Policy Engine
```python
from abc import ABC, abstractmethod
from datetime import datetime

class Policy(ABC):
    """
    Abstract base class for access policies
    """
    @abstractmethod
    async def evaluate(self, user: dict, resource: dict, action: str) -> bool:
        pass

class TimeBasedPolicy(Policy):
    """
    Policy that restricts access based on time
    """
    def __init__(self, allowed_start_hour: int, allowed_end_hour: int):
        self.start_hour = allowed_start_hour
        self.end_hour = allowed_end_hour

    async def evaluate(self, user: dict, resource: dict, action: str) -> bool:
        current_hour = datetime.now().hour
        return self.start_hour <= current_hour <= self.end_hour

class IPBasedPolicy(Policy):
    """
    Policy that restricts access based on IP address
    """
    def __init__(self, allowed_ips: List[str]):
        self.allowed_ips = allowed_ips

    async def evaluate(self, user: dict, resource: dict, action: str) -> bool:
        client_ip = resource.get("client_ip", "")
        return client_ip in self.allowed_ips

class PolicyEngine:
    """
    Centralized policy evaluation engine
    """
    def __init__(self):
        self.policies: List[Policy] = []

    def add_policy(self, policy: Policy):
        self.policies.append(policy)

    async def evaluate_access(self, user: dict, resource: dict, action: str) -> bool:
        """
        Evaluate all policies and return access decision
        """
        for policy in self.policies:
            if not await policy.evaluate(user, resource, action):
                return False
        return True

policy_engine = PolicyEngine()

def require_policy_access(action: str):
    """
    Dependency that evaluates all registered policies
    """
    async def policy_checker(
        current_user: dict = Depends(get_current_user),
        resource: dict = Depends(get_resource_context)
    ) -> dict:
        if not await policy_engine.evaluate_access(current_user, resource, action):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied by policy"
            )

        return current_user

    return policy_checker

# Register policies
policy_engine.add_policy(TimeBasedPolicy(9, 17))  # Business hours only
```

## Multi-Tenant Access Control

### Tenant Isolation
```python
def verify_tenant_access(tenant_id: str):
    """
    Verify that the authenticated user belongs to the specified tenant
    """
    async def tenant_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_tenant_id = current_user.get("tenant_id")

        if user_tenant_id != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You do not belong to this tenant"
            )

        return current_user

    return tenant_checker

def verify_tenant_resource_access(tenant_id: str, resource_tenant_id: str):
    """
    Verify that the resource belongs to the same tenant as the user
    """
    async def access_checker(current_user: dict = Depends(get_current_user)) -> dict:
        user_tenant_id = current_user.get("tenant_id")

        # Verify user belongs to the requested tenant
        if user_tenant_id != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You do not belong to this tenant"
            )

        # Verify resource belongs to the same tenant
        if resource_tenant_id != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resource not found"
            )

        return current_user

    return access_checker

# Usage in multi-tenant API
@app.get("/tenants/{tenant_id}/users/{user_id}")
async def get_tenant_user(
    tenant_id: str,
    user_id: str,
    current_user: dict = Depends(verify_tenant_access)
):
    return {"user": {"id": user_id, "tenant_id": tenant_id}}
```

## Conditional Access Control

### Context-Aware Access Control
```python
def conditional_access(condition_func):
    """
    Generic conditional access decorator
    """
    async def access_checker(current_user: dict = Depends(get_current_user)) -> dict:
        if not condition_func(current_user):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied by conditional check"
            )

        return current_user

    return access_checker

def require_verified_email():
    """
    Require user to have verified email
    """
    def check_verified_email(user: dict) -> bool:
        return user.get("email_verified", False)

    return conditional_access(check_verified_email)

def require_account_age(minimum_days: int):
    """
    Require account to be older than specified days
    """
    from datetime import datetime, timedelta

    def check_account_age(user: dict) -> bool:
        account_created = user.get("account_created")
        if not account_created:
            return False

        created_date = datetime.fromisoformat(account_created.replace('Z', '+00:00'))
        min_date = datetime.now(created_date.tzinfo) - timedelta(days=minimum_days)
        return created_date <= min_date

    return conditional_access(check_account_age)

# Usage
@app.post("/premium-feature")
async def premium_action(
    current_user: dict = Depends(require_verified_email())
):
    return {"message": "Premium feature accessed"}

@app.delete("/account")
async def delete_account(
    current_user: dict = Depends(require_account_age(30))  # Account must be 30+ days old
):
    return {"message": "Account deleted"}
```

## Access Control Testing

### Unit Tests for Access Control
```python
import pytest
from unittest.mock import patch, MagicMock

def test_admin_role_access():
    """Test that admin users can access admin endpoints"""
    admin_user = {"sub": "admin123", "roles": ["admin"]}

    with patch('your_app.get_current_user') as mock_get_user:
        mock_get_user.return_value = admin_user

        # This should not raise an exception
        result = require_role(UserRole.ADMIN)(admin_user)
        assert result == admin_user

def test_non_admin_role_denied():
    """Test that non-admin users are denied access to admin endpoints"""
    regular_user = {"sub": "user123", "roles": ["user"]}

    with patch('your_app.get_current_user') as mock_get_user:
        mock_get_user.return_value = regular_user

        with pytest.raises(HTTPException) as exc_info:
            require_role(UserRole.ADMIN)(regular_user)

        assert exc_info.value.status_code == 403

def test_permission_based_access():
    """Test permission-based access control"""
    user_with_permission = {"sub": "user123", "permissions": ["read:users"]}

    with patch('your_app.get_current_user') as mock_get_user:
        mock_get_user.return_value = user_with_permission

        # This should not raise an exception
        result = require_permission(Permission.READ_USERS)(user_with_permission)
        assert result == user_with_permission

def test_ownership_verification():
    """Test resource ownership verification"""
    owner_user = {"sub": "owner123"}

    # Test with correct owner
    result = verify_resource_ownership("owner123")(owner_user)
    assert result == owner_user

    # Test with wrong owner
    with pytest.raises(HTTPException) as exc_info:
        verify_resource_ownership("different_user")(owner_user)

    assert exc_info.value.status_code == 403

def test_multi_role_access():
    """Test access with multiple possible roles"""
    moderator_user = {"sub": "mod123", "roles": ["moderator", "user"]}

    with patch('your_app.get_current_user') as mock_get_user:
        mock_get_user.return_value = moderator_user

        # User with moderator role should access admin-or-mod endpoint
        result = require_any_role(UserRole.ADMIN, UserRole.MODERATOR)(moderator_user)
        assert result == moderator_user
```

## Performance Considerations

### Caching Access Decisions
```python
from functools import lru_cache
import hashlib

class CachedAccessControl:
    """
    Access control with caching for performance
    """
    def __init__(self, ttl: int = 300):  # 5 minutes default TTL
        self.ttl = ttl
        self.cache = {}

    def get_cache_key(self, user_id: str, resource_id: str, action: str) -> str:
        """
        Generate cache key for access decision
        """
        key_data = f"{user_id}:{resource_id}:{action}"
        return hashlib.sha256(key_data.encode()).hexdigest()

    async def check_access(self, user: dict, resource_id: str, action: str) -> bool:
        """
        Check access with caching
        """
        user_id = user.get("sub")
        cache_key = self.get_cache_key(user_id, resource_id, action)

        # Check cache first
        if cache_key in self.cache:
            allowed, timestamp = self.cache[cache_key]
            if time.time() - timestamp < self.ttl:
                return allowed

        # Perform access check
        allowed = await self.perform_access_check(user, resource_id, action)

        # Cache the result
        self.cache[cache_key] = (allowed, time.time())
        return allowed

    async def perform_access_check(self, user: dict, resource_id: str, action: str) -> bool:
        """
        Perform the actual access check logic
        """
        # Implement your access control logic here
        # This is a simplified example
        return True  # or your actual logic

cached_access_control = CachedAccessControl()

def require_cached_access(resource_id: str, action: str):
    """
    Dependency with cached access control
    """
    async def access_checker(current_user: dict = Depends(get_current_user)) -> dict:
        has_access = await cached_access_control.check_access(current_user, resource_id, action)

        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )

        return current_user

    return access_checker
```

These access control patterns provide flexible and secure authorization for your FastAPI applications while maintaining good performance characteristics.