#!/usr/bin/env python3
"""
Test runner for SQL Agent tests.

This script discovers and runs all unit and integration tests in the tests directory.
"""

import unittest
import sys
import os
from pathlib import Path

def run_tests():
    """Discover and run all tests in the tests directory."""
    # Add the project root to the path so we can import our package
    project_root = str(Path(__file__).parent.parent)
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    # Add the src directory to the path
    src_dir = os.path.join(project_root, 'src')
    if src_dir not in sys.path:
        sys.path.insert(0, src_dir)
    
    print(f"Python path: {sys.path}")
    print(f"Current working directory: {os.getcwd()}")
    
    # Discover and run tests
    test_loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    
    # Manually add test modules
    test_modules = [
        'tests.unit.test_db_connector',
        'tests.unit.test_changelog_engine'
    ]
    
    for module in test_modules:
        try:
            # If the module cannot be found, this will raise an ImportError
            mod = __import__(module, fromlist=['*'])
            # Add all test cases from the module
            test_suite.addTests(test_loader.loadTestsFromModule(mod))
            print(f"Added tests from {module}")
        except ImportError as e:
            print(f"Failed to import {module}: {e}")
    
    # Also try to discover tests in the tests directory
    discovered_suite = test_loader.discover(
        start_dir=os.path.dirname(os.path.abspath(__file__)),
        pattern='test_*.py'
    )
    test_suite.addTests(discovered_suite)
    
    if test_suite.countTestCases() == 0:
        print("No tests found!")
        return 1
    
    print(f"Running {test_suite.countTestCases()} test cases...")
    
    # Run the tests
    test_runner = unittest.TextTestRunner(verbosity=2)
    result = test_runner.run(test_suite)
    
    # Return an appropriate exit code
    return 0 if result.wasSuccessful() else 1

if __name__ == "__main__":
    sys.exit(run_tests())
