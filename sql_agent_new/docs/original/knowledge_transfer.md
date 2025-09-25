# SQL Agent Knowledge Transfer Document

*Last updated: 2025-06-05*

## Table of Contents
1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Key Components](#key-components)
4. [Database Schema](#database-schema)
5. [Configuration](#configuration)
6. [Deployment Process](#deployment-process)
7. [Monitoring and Maintenance](#monitoring-and-maintenance)
8. [Troubleshooting](#troubleshooting)
9. [Future Enhancements](#future-enhancements)
10. [Contact Information](#contact-information)

## Project Overview

The SQL Agent is an intelligent system designed to process natural language queries and convert them into SQL statements for database interaction. It provides a user-friendly interface for non-technical users to query databases without requiring SQL knowledge.

### Project Goals
- Simplify database querying for non-technical users
- Improve query accuracy and performance
- Provide robust error handling and recovery
- Ensure secure and reliable operation in production environments

### Key Features
- Natural language to SQL conversion
- Query optimization and validation
- Error detection and recovery
- Comprehensive logging and monitoring
- Secure database access

## System Architecture

The SQL Agent follows a modular architecture with the following layers:

1. **User Interface Layer**: Handles user interactions and displays results
2. **Query Processing Layer**: Converts natural language to SQL
3. **Database Interaction Layer**: Executes SQL queries and processes results
4. **Monitoring and Logging Layer**: Tracks system performance and errors

### Architecture Diagram

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  User Interface │────▶│ Query Processor │────▶│ Query Validator │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                                         │
┌─────────────────┐     ┌─────────────────┐             ▼
│ Result Renderer │◀────│ Query Executor  │◀────┌─────────────────┐
└─────────────────┘     └─────────────────┘     │ Database Adapter │
                                                └─────────────────┘
```

## Key Components

### Core Components

#### Query Engine (`scripts/core/query_engine.py`)
The heart of the system, responsible for processing natural language queries and converting them to SQL. It uses advanced NLP techniques and database schema knowledge to generate accurate SQL queries.

Key functions:
- `process_query(query_text)`: Processes a natural language query
- `generate_sql(processed_query)`: Generates SQL from processed query
- `execute_query(sql)`: Executes the generated SQL query

#### Database Connector (`scripts/core/db_connector.py`)
Handles database connections and query execution. Supports multiple database types and provides connection pooling for optimal performance.

Key functions:
- `connect()`: Establishes a database connection
- `execute_query(sql)`: Executes a SQL query
- `fetch_results()`: Retrieves query results

#### Error Handler (`scripts/core/error_handler.py`)
Manages error detection, logging, and recovery. Implements retry logic for transient errors and provides detailed error messages.

Key functions:
- `handle_error(error)`: Processes and logs errors
- `classify_error(error)`: Classifies errors by type and severity
- `suggest_resolution(error)`: Suggests resolution steps for errors

### Utility Components

#### Utilities (`scripts/core/utils.py`)
Contains common utility functions used throughout the application, including the retry decorator for handling transient errors.

Key functions:
- `retry_on_exception(max_attempts, delay)`: Decorator for retrying operations

#### Configuration Manager (`scripts/core/config_manager.py`)
Handles loading and validation of configuration settings from various sources.

Key functions:
- `load_config(config_path)`: Loads configuration from file
- `validate_config(config)`: Validates configuration settings
- `get_setting(key)`: Retrieves a specific configuration setting

## Database Schema

The SQL Agent uses the following database tables:

### Queries Table
Stores information about executed queries.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| user_id | INTEGER | User who executed the query |
| query_text | TEXT | Original natural language query |
| sql_text | TEXT | Generated SQL query |
| execution_time_ms | INTEGER | Query execution time in milliseconds |
| created_at | TIMESTAMP | When the query was executed |

### Results Table
Stores query results for future reference.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| query_id | INTEGER | Foreign key to Queries table |
| result_data | TEXT | JSON-encoded query results |
| row_count | INTEGER | Number of rows returned |
| created_at | TIMESTAMP | When the result was created |

### Users Table
Stores user information.

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| username | TEXT | User's username |
| email | TEXT | User's email address |
| created_at | TIMESTAMP | When the user was created |

## Configuration

The SQL Agent uses a hierarchical configuration system with environment-specific settings.

### Configuration Files

- `config/config.ini`: Base configuration file
- `config/production_config.json`: Production environment configuration
- `config/config.{env}.json`: Environment-specific configurations (dev, test, staging)

### Key Configuration Sections

#### Database Configuration
```json
"database": {
  "host": "${PROD_DB_HOST}",
  "port": 5432,
  "user": "${PROD_DB_USER}",
  "password": "${PROD_DB_PASSWORD}",
  "database": "sql_agent",
  "pool_size": 10,
  "connection_timeout_seconds": 5
}
```

#### Logging Configuration
```json
"logging": {
  "level": "WARNING",
  "log_directory": "logs/production",
  "file_rotation_size_mb": 10,
  "retention_days": 30,
  "sensitive_data_masking": true
}
```

#### Performance Configuration
```json
"performance": {
  "query_timeout_seconds": 10,
  "max_rows_returned": 1000,
  "cache_enabled": true,
  "cache_ttl_seconds": 3600
}
```

## Deployment Process

The SQL Agent uses a staged deployment process to ensure reliability and minimize downtime.

### Deployment Stages

1. **Development (Dev)**: Initial deployment for development testing
2. **Testing (Test)**: Deployment for QA and automated testing
3. **Staging**: Pre-production environment for final validation
4. **Production**: Live production environment

### Deployment Scripts

- `deployment/deploy.py`: Main deployment script
- `deployment/rollback.py`: Rollback script for recovery
- `deployment/staged_deploy.py`: Staged deployment across environments
- `deployment/monitoring.py`: Monitoring setup
- `deployment/security_review.py`: Security validation
- `deployment/data_verification.py`: Data integrity verification
- `deployment/performance_validation.py`: Performance testing
- `deployment/user_acceptance.py`: User acceptance testing

### Deployment Process

To deploy the SQL Agent:

1. **Prepare Configuration**:
   ```bash
   python deployment/deploy.py --prepare-config
   ```

2. **Run Security Review**:
   ```bash
   python deployment/security_review.py --config config/production_config.json
   ```

3. **Execute Staged Deployment**:
   ```bash
   python deployment/staged_deploy.py --start-stage dev --end-stage production
   ```

4. **Verify Deployment**:
   ```bash
   python deployment/data_verification.py --config config/production_config.json
   python deployment/performance_validation.py --config config/production_config.json
   ```

5. **Run User Acceptance Testing**:
   ```bash
   python deployment/user_acceptance.py --config config/production_config.json
   ```

### Rollback Procedure

If deployment fails or issues are detected:

1. **Execute Rollback**:
   ```bash
   python deployment/rollback.py --backup [backup_directory]
   ```

2. **Verify Rollback**:
   ```bash
   python deployment/data_verification.py --config config/config.ini
   ```

## Monitoring and Maintenance

### Monitoring Setup

The SQL Agent includes comprehensive monitoring capabilities:

- **Performance Monitoring**: Tracks query execution times, resource usage
- **Error Monitoring**: Logs and alerts on errors
- **Usage Analytics**: Tracks system usage patterns

### Monitoring Script

To set up monitoring:

```bash
python deployment/monitoring.py --config config/production_config.json
```

### Maintenance Tasks

Regular maintenance tasks include:

1. **Log Rotation**: Automatically handled based on configuration
2. **Database Optimization**: Recommended monthly
3. **Configuration Review**: Recommended quarterly
4. **Security Audits**: Recommended quarterly

## Troubleshooting

### Common Issues and Resolutions

#### Database Connection Issues
- **Symptom**: "Failed to connect to database" errors
- **Resolution**: 
  - Verify database credentials in configuration
  - Check network connectivity
  - Ensure database service is running

#### Query Processing Errors
- **Symptom**: "Failed to process query" errors
- **Resolution**:
  - Check query syntax
  - Verify database schema is up to date
  - Review error logs for specific error messages

#### Performance Issues
- **Symptom**: Slow query execution
- **Resolution**:
  - Review database indexes
  - Check for resource constraints
  - Optimize complex queries

### Logging and Diagnostics

Log files are stored in the `logs` directory with the following structure:

- `logs/app.log`: Main application log
- `logs/error.log`: Error-specific log
- `logs/performance.log`: Performance metrics
- `logs/security.log`: Security-related events

## Future Enhancements

Planned future enhancements for the SQL Agent include:

1. **Advanced NLP**: Improved natural language understanding
2. **Query Templates**: Support for saved query templates
3. **Visualization**: Integrated data visualization
4. **Machine Learning**: Adaptive query optimization
5. **Multi-database Support**: Support for additional database types

## Contact Information

For questions or support:

- **Project Lead**: [project.lead@example.com](mailto:project.lead@example.com)
- **Technical Support**: [support@example.com](mailto:support@example.com)
- **Documentation**: [docs@example.com](mailto:docs@example.com)

---

*This document is confidential and proprietary to Adient. It is intended for internal use only.*
