# SQL Agent Project Migration Plan

## Overview

This document outlines the step-by-step plan to reorganize the SQL Agent project according to the dev_framework structure and best practices. The reorganization will transform the current mixed structure into a standardized Python package structure with clear separation of concerns.

## New Directory Structure

```
sql_agent/                      # Root package directory
├── src/                        # All source code
│   ├── sql_agent/              # Main package
│   │   ├── __init__.py
│   │   ├── core/               # Core functionality
│   │   │   ├── __init__.py
│   │   │   ├── db_connector.py # Database connection logic
│   │   │   └── query_engine.py # SQL query processing
│   │   ├── cli/                # Command-line interfaces
│   │   │   ├── __init__.py
│   │   │   └── sql_cli.py      # SQL CLI tool
│   │   ├── analysis/           # Analysis modules
│   │   │   ├── __init__.py
│   │   │   └── rct_wo/         # RCT-WO specific analysis
│   │   ├── utils/              # Utility functions
│   │   │   ├── __init__.py
│   │   │   └── helpers.py
│   │   └── config/             # Configuration handling
│   │       ├── __init__.py
│   │       └── settings.py
├── tests/                      # All tests
│   ├── unit/                   # Unit tests
│   ├── integration/            # Integration tests
│   └── conftest.py             # Test configurations
├── configs/                    # Configuration files
│   ├── database.json
│   ├── logging.json
│   └── app_config.json
├── docs/                       # Documentation
│   ├── user_guide.md
│   ├── api_docs.md
│   └── development/
├── scripts/                    # Utility scripts
│   ├── setup_db.py
│   └── generate_report.py
├── data/                       # Data files
│   └── Database_tables/        # Database schema definitions
├── examples/                   # Example usage
├── .env.example                # Example environment variables
├── requirements.txt            # Project dependencies
├── setup.py                    # Package setup
├── README.md                   # Project readme
└── CHANGELOG.md                # Project changelog
```

## Migration Steps

### Step 1: Create the new directory structure

```powershell
# Create main directory structure
mkdir -p src\sql_agent\core
mkdir -p src\sql_agent\cli
mkdir -p src\sql_agent\analysis\rct_wo
mkdir -p src\sql_agent\utils
mkdir -p src\sql_agent\config
mkdir -p tests\unit
mkdir -p tests\integration
mkdir -p configs
mkdir -p docs\development
mkdir -p scripts
mkdir -p data
mkdir -p examples

# Create necessary __init__.py files
"# SQL Agent package" | Out-File -FilePath src\sql_agent\__init__.py
"# Core functionality" | Out-File -FilePath src\sql_agent\core\__init__.py
"# CLI tools" | Out-File -FilePath src\sql_agent\cli\__init__.py
"# Analysis modules" | Out-File -FilePath src\sql_agent\analysis\__init__.py
"# RCT-WO analysis" | Out-File -FilePath src\sql_agent\analysis\rct_wo\__init__.py
"# Utility functions" | Out-File -FilePath src\sql_agent\utils\__init__.py
"# Configuration handling" | Out-File -FilePath src\sql_agent\config\__init__.py
```

### Step 2: Move and reorganize existing files

#### Core functionality

```powershell
# Move database connector code
Copy-Item -Path "scripts\db\db_connector.py" -Destination "src\sql_agent\core\" -ErrorAction SilentlyContinue
```

#### CLI tools

```powershell
# Move SQL CLI code
Copy-Item -Path "sql_cli.py" -Destination "src\sql_agent\cli\" -ErrorAction SilentlyContinue
```

#### Analysis code

```powershell
# Move RCT-WO analysis code
Copy-Item -Path "analysis\rct_wo_analysis\standalone_analysis.py" -Destination "src\sql_agent\analysis\rct_wo\analysis.py" -ErrorAction SilentlyContinue
Copy-Item -Path "analysis\rct_wo_analysis\simple_test.py" -Destination "src\sql_agent\analysis\rct_wo\connection_test.py" -ErrorAction SilentlyContinue
```

#### Configuration files

```powershell
# Move configuration files
Copy-Item -Path "config\*.json" -Destination "configs\" -ErrorAction SilentlyContinue
```

#### Database tables

```powershell
# Move database table definitions
Copy-Item -Path "Database_tables" -Destination "data\" -Recurse -ErrorAction SilentlyContinue
```

#### Documentation

```powershell
# Move documentation
Copy-Item -Path "docs\*.md" -Destination "docs\" -ErrorAction SilentlyContinue
Copy-Item -Path "sql-agent-roadmap.md" -Destination "docs\roadmap.md" -ErrorAction SilentlyContinue
```

#### Test files

```powershell
# Move test files
Copy-Item -Path "scripts\testing\*.py" -Destination "tests\unit\" -ErrorAction SilentlyContinue
```

### Step 3: Create package setup files

#### setup.py

```python
from setuptools import setup, find_packages

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
```

#### requirements.txt

```
# Core dependencies
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
```

### Step 4: Update import paths in code files

You'll need to update import statements in all Python files to reflect the new structure. Here are some examples:

#### Before:

```python
from scripts.db.db_connector import DatabaseConnector
from scripts.utilities.helpers import format_output
```

#### After:

```python
from sql_agent.core.db_connector import DatabaseConnector
from sql_agent.utils.helpers import format_output
```

### Step 5: Update README.md

Create a new README.md file with updated installation and usage instructions:

```markdown
# SQL Agent

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
source venv/bin/activate  # On Windows: venv\Scripts\activate

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
```

### Step 6: Update CHANGELOG.md

Add a new entry to the changelog documenting the reorganization:

```markdown
## Session: 2025-06-12

### Project Reorganization
**Timestamp:** 2025-06-12 17:15
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
```

## Post-Migration Checklist

After completing the migration steps, perform the following checks:

1. **Verify Directory Structure**:
   - Ensure all directories have been created correctly
   - Check that files have been moved to their appropriate locations

2. **Test Package Installation**:
   - Create a new virtual environment
   - Install the package in development mode: `pip install -e .`
   - Verify that the package can be imported: `import sql_agent`

3. **Test Functionality**:
   - Run the SQL CLI tool: `sql-cli --help`
   - Run the RCT-WO analysis: `python -m sql_agent.analysis.rct_wo.analysis`
   - Verify that all functionality works as expected

4. **Update Documentation**:
   - Ensure all documentation references the new file structure
   - Update any usage examples to reflect the new import paths

5. **Clean Up**:
   - Remove any temporary files or backups created during migration
   - Commit the changes to version control

## Rollback Plan

If issues are encountered during migration, follow these steps to roll back:

1. Revert to the previous commit in version control
2. If files were moved or renamed manually, move them back to their original locations
3. Restore any modified configuration files from backups
4. Test that the original functionality works as expected

## Conclusion

This migration plan provides a comprehensive guide to reorganizing the SQL Agent project into a standardized Python package structure. Following these steps will result in a more maintainable, scalable, and developer-friendly codebase that adheres to best practices.
