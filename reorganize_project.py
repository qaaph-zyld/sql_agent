#!/usr/bin/env python3
"""
SQL Agent Project Reorganization Script
"""

import os
import shutil
import sys
from pathlib import Path
import datetime

def create_directory_structure(base_dir):
    """Create the new directory structure"""
    dirs = [
        "src/sql_agent",
        "src/sql_agent/core",
        "src/sql_agent/cli",
        "src/sql_agent/analysis",
        "src/sql_agent/analysis/rct_wo",
        "src/sql_agent/utils",
        "src/sql_agent/config",
        "tests/unit",
        "tests/integration",
        "configs",
        "docs",
        "scripts",
        "data",
        "examples"
    ]
    
    for dir_path in dirs:
        full_path = os.path.join(base_dir, dir_path)
        os.makedirs(full_path, exist_ok=True)
        print(f"Created directory: {full_path}")
    
    # Create __init__.py files
    init_dirs = [
        "src/sql_agent",
        "src/sql_agent/core",
        "src/sql_agent/cli",
        "src/sql_agent/analysis",
        "src/sql_agent/analysis/rct_wo",
        "src/sql_agent/utils",
        "src/sql_agent/config"
    ]
    
    for dir_path in init_dirs:
        init_file = os.path.join(base_dir, dir_path, "__init__.py")
        with open(init_file, 'w') as f:
            f.write('"""SQL Agent package."""\n')
        print(f"Created file: {init_file}")

def copy_files(source_base, target_base):
    """Copy files to their new locations"""
    file_mappings = [
        # Core files
        ("scripts/db/db_connector.py", "src/sql_agent/core/db_connector.py"),
        ("sql_cli.py", "src/sql_agent/cli/sql_cli.py"),
        
        # Analysis files
        ("analysis/rct_wo_analysis/standalone_analysis.py", "src/sql_agent/analysis/rct_wo/analysis.py"),
        ("analysis/rct_wo_analysis/simple_test.py", "src/sql_agent/analysis/rct_wo/connection_test.py"),
        
        # Config files
        ("config/database.json", "configs/database.json"),
        ("config/logging.json", "configs/logging.json"),
        ("config/app_config.json", "configs/app_config.json"),
        ("config/database_mock.json", "configs/database_mock.json"),
        
        # Documentation
        ("README.md", "README.md"),
        ("Changelog.md", "CHANGELOG.md"),
        ("sql-agent-roadmap.md", "docs/roadmap.md"),
    ]
    
    for source, target in file_mappings:
        source_path = os.path.join(source_base, source)
        target_path = os.path.join(target_base, target)
        
        if os.path.exists(source_path):
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            shutil.copy2(source_path, target_path)
            print(f"Copied: {source_path} -> {target_path}")
        else:
            print(f"Warning: Source file not found: {source_path}")
    
    # Copy directory trees
    dir_mappings = [
        ("Database_tables", "data/Database_tables"),
        ("docs", "docs/original"),
    ]
    
    for source, target in dir_mappings:
        source_path = os.path.join(source_base, source)
        target_path = os.path.join(target_base, target)
        
        if os.path.exists(source_path):
            if os.path.exists(target_path):
                shutil.rmtree(target_path)
            shutil.copytree(source_path, target_path)
            print(f"Copied directory: {source_path} -> {target_path}")
        else:
            print(f"Warning: Source directory not found: {source_path}")

def create_setup_py(base_dir):
    """Create setup.py file"""
    setup_py = os.path.join(base_dir, "setup.py")
    with open(setup_py, 'w') as f:
        f.write('''from setuptools import setup, find_packages

setup(
    name="sql_agent",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "pymssql",
        "pandas",
        "matplotlib",
        "seaborn",
        "sqlalchemy",
        "python-dotenv",
    ],
    python_requires=">=3.6",
    entry_points={
        "console_scripts": [
            "sql-cli=sql_agent.cli.sql_cli:main",
        ],
    },
)
''')
    print(f"Created file: {setup_py}")

def create_readme(base_dir):
    """Create an updated README.md file"""
    readme_path = os.path.join(base_dir, "README.md")
    
    # Check if README already exists, if so, create a backup
    if os.path.exists(readme_path):
        backup_path = os.path.join(base_dir, f"README.md.bak.{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
        shutil.copy2(readme_path, backup_path)
        print(f"Created backup of README: {backup_path}")
    
    with open(readme_path, 'w') as f:
        f.write('''# SQL Agent

A comprehensive SQL analysis and reporting tool for interacting with SQL Server databases.

## Features

- SQL command-line interface with formatted output
- Database schema exploration and analysis
- Transaction analysis and reporting
- Visualization capabilities for data analysis

## Installation

```bash
# Clone the repository
git clone https://github.com/your-username/sql_agent.git
cd sql_agent

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate

# Install dependencies
pip install -e .
```

## Usage

```bash
# Run the SQL CLI
sql-cli query --sql "SELECT * FROM your_table"

# Run RCT-WO analysis
python -m sql_agent.analysis.rct_wo.analysis
```

## Documentation

See the [docs](docs/) directory for detailed documentation.
''')
    print(f"Created updated README: {readme_path}")

def create_requirements_txt(base_dir):
    """Create requirements.txt file"""
    req_path = os.path.join(base_dir, "requirements.txt")
    with open(req_path, 'w') as f:
        f.write('''# Core dependencies
pymssql>=2.2.0
pandas>=1.3.0
matplotlib>=3.4.0
seaborn>=0.11.0
sqlalchemy>=1.4.0
python-dotenv>=0.19.0

# Development dependencies
pytest>=6.2.0
pytest-cov>=2.12.0
flake8>=3.9.0
black>=21.5b0
''')
    print(f"Created requirements.txt: {req_path}")

def update_changelog(base_dir):
    """Update the changelog with reorganization information"""
    changelog_path = os.path.join(base_dir, "CHANGELOG.md")
    
    # Create a backup of the original changelog
    if os.path.exists(changelog_path):
        backup_path = os.path.join(base_dir, f"CHANGELOG.md.bak.{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}")
        shutil.copy2(changelog_path, backup_path)
        print(f"Created backup of CHANGELOG: {backup_path}")
        
        # Read the original content
        with open(changelog_path, 'r') as f:
            original_content = f.read()
        
        # Add the reorganization entry
        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        reorganization_entry = f'''# CHANGELOG.md

## Session: {datetime.datetime.now().strftime('%Y-%m-%d')}

### Project Reorganization
**Timestamp:** {now}
**Action Type:** Restructuring
**Previous State:** Mixed project structure with no clear separation of concerns
**Current State:** Standardized Python package structure following best practices

#### Changes Made:
- Reorganized project into a proper Python package structure
- Created src/sql_agent directory for all source code
- Separated code into logical modules (core, cli, analysis, utils, config)
- Moved configuration files to configs/ directory
- Moved database tables to data/ directory
- Created proper package setup with setup.py
- Updated documentation to reflect new structure

#### Files Affected:
- All Python modules moved to new locations
- Configuration files centralized
- Documentation reorganized

#### Technical Decisions:
- Adopted standard Python package structure for better maintainability
- Implemented proper package installation with entry points
- Separated concerns between different modules
- Created clear boundaries between components

#### Next Actions Required:
- Update import statements in all Python files
- Test the reorganized project structure
- Update any scripts that reference the old file paths

---

'''
        
        # Write the updated content
        with open(changelog_path, 'w') as f:
            f.write(reorganization_entry + original_content)
        
        print(f"Updated CHANGELOG: {changelog_path}")
    else:
        print(f"Warning: CHANGELOG not found at {changelog_path}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python reorganize_project.py <target_directory>")
        sys.exit(1)
    
    target_dir = sys.argv[1]
    source_dir = os.path.dirname(os.path.abspath(__file__))
    
    print(f"Reorganizing project from {source_dir} to {target_dir}")
    
    # Create new directory structure
    create_directory_structure(target_dir)
    
    # Copy files to new structure
    copy_files(source_dir, target_dir)
    
    # Create setup.py
    create_setup_py(target_dir)
    
    # Create/update README.md
    create_readme(target_dir)
    
    # Create requirements.txt
    create_requirements_txt(target_dir)
    
    # Update changelog
    update_changelog(target_dir)
    
    print("\nReorganization complete!")
    print("\nNext steps:")
    print("1. Update import statements in all Python files")
    print("2. Test the reorganized project")
    print("3. Update any scripts or documentation that reference the old structure")

if __name__ == "__main__":
    main()
