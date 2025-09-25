# SQL Agent

A comprehensive SQL analysis and reporting tool for interacting with SQL Server databases. This project provides tools for database connectivity, query execution, transaction analysis, and reporting.

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

## Features

- **SQL Command-line Interface**: Execute SQL queries with formatted output
- **Database Schema Exploration**: Analyze database structure and relationships
- **Transaction Analysis**: Specialized analysis for RCT-WO transactions
- **Visualization**: Generate charts and graphs for data analysis
- **Reporting**: Create HTML and text-based reports

## Installation

### Prerequisites

- Python 3.6 or higher
- Access to a SQL Server database

### Setup

```powershell
# Clone the repository
git clone https://github.com/your-organization/sql_agent.git
cd sql_agent

# Run the setup script (Windows)
.\setup_and_test.bat

# Or set up manually:
# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate  # On Windows
# source venv/bin/activate  # On Unix/Mac

# Install the package in development mode
pip install -e .
```

### Configuration

Edit the configuration files in the `configs/` directory:

- `database.json`: Database connection settings
- `logging.json`: Logging configuration
- `app_config.json`: Application settings

## Usage

### SQL CLI

```powershell
# Run the SQL CLI
sql-cli --help

# Execute a query
sql-cli query --sql "SELECT * FROM tr_hist WHERE tr_type = 'RCT-WO'"

# List all tables
sql-cli list

# Describe a table
sql-cli describe --table tr_hist
```

### RCT-WO Analysis

```powershell
# Run the RCT-WO analysis
python -m sql_agent.analysis.rct_wo.analysis

# Test database connection
python -m sql_agent.analysis.rct_wo.connection_test
```

## Development

### Project Organization

- Place new core functionality in `src/sql_agent/core/`
- Add new analysis modules in `src/sql_agent/analysis/`
- Create tests for new functionality in `tests/`
- Update configuration as needed in `configs/`

### Testing

```powershell
# Run all tests
python -m pytest

# Run specific tests
python -m pytest tests/unit/
```

### Adding New Features

1. Create a new module in the appropriate directory
2. Update `__init__.py` files to expose the new functionality
3. Add tests for the new feature
4. Update documentation

## Documentation

See the `docs/` directory for detailed documentation:

- User Guide: `docs/user_guide.md`
- API Documentation: `docs/api_docs.md`
- Development Guide: `docs/development/`
- Roadmap: `docs/roadmap.md`

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature-name`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature-name`
5. Submit a pull request

## License

[Your License] - See LICENSE file for details

## Acknowledgments

- [List any acknowledgments or third-party libraries used]
