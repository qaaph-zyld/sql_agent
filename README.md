# SQL Database Querying Agent

This repository contains a SQL Database Querying Agent that translates natural language questions into SQL queries. The agent provides an intuitive interface for database interaction without requiring SQL knowledge, extracts database schema information, and maintains comprehensive documentation.

## Directory Structure

The repository is organized into the following directories:

```
├── config/            # Configuration files
├── docs/              # Documentation files
├── logs/              # Log files
├── scripts/           # Python scripts
│   ├── core/          # Core system scripts
│   ├── data_quality/  # Data quality scripts
│   ├── reports/       # Report generation scripts
│   └── utilities/     # Utility scripts
└── Database_tables/   # Database structure documentation
```

## Changelog System

The repository includes an automated changelog system that tracks all significant changes to the codebase. The system follows a hierarchical structure:

- **Session → Answer → Operation → FileModification**
- Automated state detection with SHA-256 state hashing
- Performance optimization with multi-tier caching
- <50ms response overhead

### Validation Suite

A comprehensive validation suite ensures system integrity and performance compliance:

- **Changelog Integrity**: Validates structural integrity of the changelog
- **Workspace Consistency**: Verifies workspace structure against expected configuration
- **Performance Compliance**: Ensures system meets performance thresholds
- **Change Chain Continuity**: Validates answer chain continuity and state transitions

To run the validation suite:
```
python scripts/core/run_validation.py
```

## Components

### 1. Query Parameter Interface

The Query Parameter Interface provides a user-friendly GUI for executing custom SQL queries with parameterized inputs. It allows users to:

- Select from predefined custom queries
- Customize query parameters without editing SQL
- Export results to Excel or CSV
- Filter data based on various criteria

**Usage:**
```
python query_parameter_interface.py
```

### 2. Data Quality Reports

The Data Quality Reports system generates detailed reports on various data quality issues in the database. It includes:

- Missing cost information reports
- Missing routing information reports
- WIP overstock reports
- Summary reports with trends and visualizations

**Usage:**
```
python data_quality_manager.py [--report-type TYPE]
```

Where TYPE can be:
- `all` (default): Generate all reports
- `missing_cost`: Generate only missing cost reports
- `missing_routing`: Generate only missing routing reports
- `wip_overstock`: Generate only WIP overstock reports

### 3. Custom Query Analyzer

The Custom Query Analyzer extracts additional information about table relationships, business processes, and data flows from custom SQL queries.

**Usage:**
```
python custom_query_analyzer.py
```

### 4. Data Lineage Mapper

The Data Lineage Mapper creates comprehensive documentation of data lineage by analyzing table relationships and business processes.

**Usage:**
```
python data_lineage_mapper.py
```

### 5. Interactive Dashboard Generator

The Interactive Dashboard Generator creates an HTML-based dashboard that integrates all components of the database documentation.

**Usage:**
```
python generate_interactive_dashboard.py
```

## Installation

1. Clone this repository
2. Install required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Configure database connection in `config.ini` (created automatically on first run)

## Configuration

The default configuration connects to:
- Server: a265m001
- Database: QADEE2798
- User: PowerBI
- Password: P0werB1

You can modify these settings in the `config.ini` file that is created after the first run.

## Directory Structure

- `Database_tables/QADEE2798/custom_sql_queries/`: Contains custom SQL queries
- `Database_tables/QADEE2798/Column_prompts.md`: Contains column calculation rules
- `reports/`: Contains report modules and generated reports
- `qad_docs/`: Contains QAD documentation

## Features

- **Automated Data Quality Monitoring**: Regular reports on data quality issues
- **Customizable Queries**: Parameter-driven queries for flexible data analysis
- **Visual Analytics**: Charts and visualizations of data quality metrics
- **Trend Analysis**: Historical tracking of data quality improvements
- **Comprehensive Documentation**: Detailed documentation of database structure and relationships

## Next Steps

See the [project_conclusions.md](Database_tables/QADEE2798/project_conclusions.md) document for a detailed implementation roadmap and next steps.

## Error Handling

All tools include comprehensive error handling and logging. Logs are saved to:
- `data_quality.log` for data quality reports
- `query_interface.log` for the query parameter interface

## Command-Line Interface

Most tools provide command-line interfaces for automation and scheduling. See individual tool documentation for details.
