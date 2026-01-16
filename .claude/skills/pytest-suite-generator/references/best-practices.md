# Pytest Best Practices Reference

## Test Organization
- Group related tests in classes with descriptive names (TestUserAPI, TestUserService)
- Use meaningful test function names that describe the scenario
- Separate tests into different files based on functionality (test_api.py, test_services.py, test_models.py)

## Fixtures Best Practices
- Use appropriate fixture scopes (function, class, module, session)
- Create reusable fixtures in conftest.py for cross-test availability
- Use autouse fixtures sparingly - only when setup is always needed
- Clean up resources in fixtures to prevent side effects between tests

## Parametrization
- Use @pytest.mark.parametrize for testing multiple inputs
- Group related test parameters in tuples
- Use descriptive parameter names to make test failures easier to understand

## Mocking Strategies
- Use unittest.mock for complex object mocking
- Use pytest's monkeypatch for simple attribute/method replacement
- Create reusable mock fixtures for common scenarios
- Mock at the right level - mock external dependencies but test actual business logic

## Assertions
- Be specific with assertions - test the exact behavior you expect
- Use multiple assertions in a single test when testing related behaviors
- Use pytest's assertion introspection - it provides detailed failure messages
- Test both positive and negative cases

## Test Data Management
- Create test data factories for complex object creation
- Use database transactions and rollbacks to isolate tests
- Clean up test data after tests to prevent contamination
- Use test-specific configurations and databases

## Performance Considerations
- Use appropriate fixture scopes to avoid redundant setup
- Run tests in parallel when possible (pytest-xdist)
- Use lightweight test databases
- Avoid heavy computations in test setup