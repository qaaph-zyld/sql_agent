#!/usr/bin/env python3
"""
SQL Agent Installation Test Script

This script tests that the SQL Agent package has been properly installed
and that its modules can be imported correctly.
"""

import sys
import importlib
import os
from pathlib import Path

def check_import(module_name):
    """Check if a module can be imported."""
    try:
        module = importlib.import_module(module_name)
        return True, module
    except ImportError as e:
        return False, str(e)

def main():
    """Main function."""
    print("SQL Agent Installation Test")
    print("==========================")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")
    print()

    # Check if the package is installed
    print("Checking SQL Agent package installation...")
    success, result = check_import('sql_agent')
    if success:
        print("✓ sql_agent package imported successfully")
        print(f"  Package location: {result.__file__}")
    else:
        print("✗ Failed to import sql_agent package")
        print(f"  Error: {result}")
        print("\nTry installing the package with: pip install -e .")
        return

    # Check core modules
    modules_to_check = [
        'sql_agent.core',
        'sql_agent.cli',
        'sql_agent.analysis',
        'sql_agent.analysis.rct_wo',
        'sql_agent.utils',
        'sql_agent.config'
    ]

    print("\nChecking SQL Agent modules...")
    all_successful = True
    for module in modules_to_check:
        success, result = check_import(module)
        if success:
            print(f"✓ {module} imported successfully")
        else:
            print(f"✗ Failed to import {module}")
            print(f"  Error: {result}")
            all_successful = False

    # Check configuration files
    print("\nChecking configuration files...")
    config_files = [
        'configs/database.json',
        'configs/logging.json',
        'configs/app_config.json'
    ]

    for config_file in config_files:
        if os.path.exists(config_file):
            print(f"✓ {config_file} exists")
        else:
            print(f"✗ {config_file} not found")
            all_successful = False

    # Print summary
    print("\nTest Summary")
    print("===========")
    if all_successful:
        print("All tests passed! The SQL Agent package is correctly installed and configured.")
        print("\nYou can now use the package in your Python code:")
        print("  import sql_agent")
        print("  from sql_agent.analysis.rct_wo import analysis")
    else:
        print("Some tests failed. Please check the errors above and fix them.")
        print("\nCommon solutions:")
        print("1. Make sure you've installed the package: pip install -e .")
        print("2. Check that all required files are in the correct locations")
        print("3. Verify that your PYTHONPATH includes the project directory")

if __name__ == "__main__":
    main()
