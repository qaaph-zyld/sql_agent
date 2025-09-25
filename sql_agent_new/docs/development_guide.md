# SQL Agent Development Guide

## Overview

This guide provides information for developers working on the SQL Agent project. It covers the project structure, development workflow, coding standards, and best practices.

## Project Structure

The SQL Agent project follows a standardized Python package structure:

```
sql_agent/
├── src/                        # All source code
│   └── sql_agent/              # Main package
│       ├── core/               # Core functionality
│       ├── cli/                # Command-line interfaces
│       ├── analysis/           # Analysis modules
│       │   └── rct_wo/         # RCT-WO specific analysis
│       ├── utils/              # Utility functions
│       └── config/             # Configuration handling
├── tests/                      # All tests
├── configs/                    # Configuration files
├── docs/                       # Documentation
├── scripts/                    # Utility scripts
├── data/                       # Data files
│   └── Database_tables/        # Database schema definitions
└── examples/                   # Example usage
```

### Key Components

- **core**: Contains the core functionality of the SQL Agent, including database connection and query execution.
- **cli**: Command-line interface tools for interacting with databases.
- **analysis**: Specialized analysis modules, such as RCT-WO transaction analysis.
- **utils**: Utility functions used across the project.
- **config**: Configuration handling and settings management.

## Development Environment Setup

### Prerequisites

- Python 3.6 or higher
- Git
- Access to a SQL Server database for testing

### Setting Up the Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/your-organization/sql_agent.git
   cd sql_agent
   ```

2. Create and activate a virtual environment:
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Unix/Mac
   python -m venv venv
   source venv/bin/activate
   ```

3. Install the package in development mode:
   ```bash
   pip install -e .
   ```

4. Install development dependencies:
   ```bash
   pip install pytest pytest-cov flake8 black
   ```

## Development Workflow

### Feature Development

1. **Create a Feature Branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Implement the Feature**:
   - Add new modules in the appropriate directories
   - Update `__init__.py` files to expose new functionality
   - Follow the coding standards (see below)

3. **Write Tests**:
   - Add unit tests in `tests/unit/`
   - Add integration tests in `tests/integration/`

4. **Update Documentation**:
   - Update relevant documentation in `docs/`
   - Add examples if necessary

5. **Submit a Pull Request**:
   - Push your branch to the repository
   - Create a pull request with a clear description of the changes

### Bug Fixes

1. **Create a Bug Fix Branch**:
   ```bash
   git checkout -b fix/bug-description
   ```

2. **Fix the Bug**:
   - Identify the root cause
   - Implement the fix
   - Add tests to prevent regression

3. **Submit a Pull Request**:
   - Push your branch to the repository
   - Create a pull request with a clear description of the bug and fix

## Coding Standards

### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) style guide
- Use 4 spaces for indentation
- Maximum line length: 88 characters (Black default)
- Use descriptive variable and function names

### Docstrings

Use Google-style docstrings:

```python
def function_name(param1, param2):
    """Short description of the function.

    Longer description explaining the function's purpose and behavior.

    Args:
        param1 (type): Description of param1.
        param2 (type): Description of param2.

    Returns:
        type: Description of the return value.

    Raises:
        ExceptionType: When and why this exception is raised.
    """
    # Function implementation
```

### Imports

Organize imports in the following order:
1. Standard library imports
2. Third-party library imports
3. Local application imports

Separate each group with a blank line:

```python
import os
import sys
from pathlib import Path

import pandas as pd
import sqlalchemy as sa

from sql_agent.core import db_connector
from sql_agent.utils import helpers
```

### Error Handling

- Use specific exception types when catching exceptions
- Include meaningful error messages
- Log exceptions with appropriate log levels

```python
try:
    # Code that might raise an exception
except SpecificException as e:
    logger.error(f"Specific error occurred: {e}")
    # Handle the exception
except Exception as e:
    logger.critical(f"Unexpected error: {e}")
    # Handle unexpected exceptions
```

## Testing

### Running Tests

Run all tests:
```bash
python -m pytest
```

Run specific test files:
```bash
python -m pytest tests/unit/test_db_connector.py
```

Run with coverage:
```bash
python -m pytest --cov=sql_agent tests/
```

### Writing Tests

- Place unit tests in `tests/unit/`
- Place integration tests in `tests/integration/`
- Use descriptive test names that explain what is being tested
- Follow the Arrange-Act-Assert pattern

Example test:
```python
def test_database_connection_success():
    # Arrange
    connector = DatabaseConnector(host="test_host", database="test_db")
    
    # Act
    result = connector.connect()
    
    # Assert
    assert result is True
    assert connector.is_connected()
```

## Configuration Management

### Configuration Files

Configuration files are stored in the `configs/` directory:
- `database.json`: Database connection settings
- `logging.json`: Logging configuration
- `app_config.json`: Application settings

### Environment Variables

Sensitive information should be stored in environment variables or a `.env` file:
```
DB_HOST=server_name
DB_USER=username
DB_PASSWORD=password
```

Use the `python-dotenv` package to load environment variables:
```python
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file
```

## Logging

Use the standard Python logging module:

```python
import logging

# Get a logger for the current module
logger = logging.getLogger(__name__)

def some_function():
    logger.debug("Debug information")
    logger.info("Informational message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical error")
```

## Documentation

### Code Documentation

- Add docstrings to all modules, classes, and functions
- Keep docstrings up-to-date with code changes

### Project Documentation

- Update `README.md` with new features and changes
- Maintain user guides and API documentation in the `docs/` directory
- Document configuration options and environment variables

## Version Control

### Commit Messages

Follow the conventional commits format:
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

Types:
- feat: A new feature
- fix: A bug fix
- docs: Documentation changes
- style: Code style changes (formatting, etc.)
- refactor: Code changes that neither fix bugs nor add features
- test: Adding or modifying tests
- chore: Changes to the build process or auxiliary tools

Example:
```
feat(analysis): Add RCT-WO transaction analysis module

- Implemented daily transaction summary
- Added visualization for transaction trends
- Created HTML report generation

Closes #123
```

### Branching Strategy

- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: Feature development branches
- `fix/*`: Bug fix branches
- `release/*`: Release preparation branches

## Deployment

### Package Distribution

To create a distributable package:
```bash
python setup.py sdist bdist_wheel
```

### Installation in Production

```bash
pip install sql_agent-x.y.z.tar.gz
```

## Changelog Management

Update the `CHANGELOG.md` file with each significant change:

```markdown
## [x.y.z] - YYYY-MM-DD

### Added
- New feature A
- New feature B

### Changed
- Modified behavior of X
- Updated dependency Y

### Fixed
- Bug in module Z
```

## Conclusion

Following these guidelines will help maintain a consistent, high-quality codebase that is easy to understand, modify, and extend. If you have any questions or suggestions for improving this guide, please open an issue or submit a pull request.
