#!/usr/bin/env python3
"""
Pytest Suite Generator Script

This script generates pytest test files based on user input and codebase analysis.
"""

import os
import argparse
from pathlib import Path
import inspect
import ast
from typing import Dict, List, Optional


class PytestGenerator:
    """Generates pytest test files for Python code."""

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.test_dir = self.project_root / "tests"

    def analyze_module(self, module_path: str) -> Dict:
        """
        Analyze a Python module to extract classes, functions, and methods.
        """
        with open(module_path, 'r') as file:
            tree = ast.parse(file.read())

        result = {
            'classes': [],
            'functions': [],
            'imports': []
        }

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = {
                    'name': node.name,
                    'methods': []
                }
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        class_info['methods'].append({
                            'name': item.name,
                            'args': [arg.arg for arg in item.args.args],
                            'has_return': any(isinstance(child, ast.Return) for child in ast.walk(item))
                        })
                result['classes'].append(class_info)
            elif isinstance(node, ast.FunctionDef):
                if node.name.startswith('_'):  # Skip private functions
                    continue
                result['functions'].append({
                    'name': node.name,
                    'args': [arg.arg for arg in node.args.args],
                    'has_return': any(isinstance(child, ast.Return) for child in ast.walk(node))
                })
            elif isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    result['imports'].append(alias.name)

        return result

    def generate_test_class(self, class_name: str, methods: List[Dict]) -> str:
        """Generate test class for a given class."""
        test_methods = []
        for method in methods:
            method_name = method['name']
            if method_name.startswith('__'):
                continue  # Skip dunder methods

            test_method = f'''
    def test_{class_name.lower()}_{method_name}_basic(self):
        """Test {class_name}.{method_name} basic functionality."""
        # Arrange
        obj = {class_name}()

        # Act
        result = obj.{method_name}()

        # Assert
        assert result is not None  # Replace with actual assertion
'''
            test_methods.append(test_method)

        class_tests = f'''
class Test{class_name}:
    """Test cases for {class_name} class."""
{''.join(test_methods)}
'''
        return class_tests

    def generate_test_function(self, func_name: str, args: List[str]) -> str:
        """Generate test for a standalone function."""
        # Create sample arguments for testing
        sample_args = []
        for i, arg in enumerate(args):
            if i == 0:  # Skip 'self' argument for methods
                continue
            sample_args.append(f'"{arg}_value"')

        args_str = ', '.join(sample_args)

        func_test = f'''
def test_{func_name}_basic():
    """Test {func_name} basic functionality."""
    # Arrange
    expected = "expected_result"  # Replace with actual expectation

    # Act
    result = {func_name}({args_str})

    # Assert
    assert result == expected  # Replace with actual assertion
'''
        return func_test

    def generate_api_test(self, endpoint: str, method: str = "GET") -> str:
        """Generate API endpoint test."""
        method_lower = method.lower()
        client_call = f"client.{method_lower}(\"{endpoint}\")"

        api_test = f'''
def test_{endpoint.replace('/', '_').strip('_')}_returns_ok(client):
    """Test {endpoint} returns successful response."""
    # Arrange
    # Add any setup needed for the request

    # Act
    response = {client_call}

    # Assert
    assert response.status_code == 200  # Adjust status code as needed
    # Add more assertions based on expected response
'''
        return api_test

    def create_test_file(self, target_path: str, output_path: Optional[str] = None):
        """Create test file for a given target module."""
        target_path = Path(target_path)
        if output_path is None:
            # Generate output path based on target
            parts = list(target_path.parts)
            # Replace 'src' or 'app' with 'tests'
            for i, part in enumerate(parts):
                if part in ['src', 'app', 'lib']:
                    parts[i] = 'tests'
                    break
            else:
                # If no src/app/lib found, add tests prefix
                parts = ['tests'] + parts

            # Change .py to _test.py or add test_ prefix
            filename = parts[-1]
            if filename.endswith('.py'):
                base_name = filename[:-3]
                if base_name.startswith('test_'):
                    parts[-1] = filename
                else:
                    parts[-1] = f"test_{base_name}.py"

            output_path = Path(*parts)

        # Create directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Analyze the target module
        analysis = self.analyze_module(str(target_path))

        # Generate test content
        content_parts = [
            'import pytest',
            '# Add imports based on the module being tested\n'
        ]

        # Generate tests for functions
        for func in analysis['functions']:
            content_parts.append(self.generate_test_function(func['name'], func['args']))

        # Generate tests for classes
        for cls in analysis['classes']:
            content_parts.append(self.generate_test_class(cls['name'], cls['methods']))

        # Write the test file
        with open(output_path, 'w') as f:
            f.write('\n'.join(content_parts))

        print(f"Generated test file: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Generate pytest test files')
    parser.add_argument('target', help='Target module to generate tests for')
    parser.add_argument('-o', '--output', help='Output test file path')
    parser.add_argument('--api', action='store_true', help='Generate API endpoint tests')
    parser.add_argument('--endpoint', help='API endpoint for API tests')

    args = parser.parse_args()

    generator = PytestGenerator()

    if args.api and args.endpoint:
        # Generate API test
        test_content = generator.generate_api_test(args.endpoint)
        output_path = args.output or f"test_api_{args.endpoint.replace('/', '_').strip('_')}.py"

        with open(output_path, 'w') as f:
            f.write(f"import pytest\nfrom fastapi.testclient import TestClient\nfrom app.main import app\n\nclient = TestClient(app)\n\n{test_content}")

        print(f"Generated API test file: {output_path}")
    else:
        # Generate regular test file
        generator.create_test_file(args.target, args.output)


if __name__ == "__main__":
    main()