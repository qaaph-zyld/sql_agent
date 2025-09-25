# SQL Agent Testing and Running Guide

*Last updated: 2025-06-05*

## Table of Contents
1. [Introduction](#introduction)
2. [Prerequisites](#prerequisites)
3. [Testing the SQL Agent](#testing-the-sql-agent)
4. [Running the SQL Agent](#running-the-sql-agent)
5. [Common Commands](#common-commands)
6. [Troubleshooting](#troubleshooting)

## Introduction

This guide provides instructions for testing and running the SQL Agent application. The SQL Agent allows users to query databases using natural language, which is then converted to SQL and executed against the target database.

## Prerequisites

Before running the SQL Agent, ensure you have:

1. Python 3.8 or higher installed
2. All dependencies installed (`pip install -r requirements.txt`)
3. Database connection configured in `config/config.json`
4. Appropriate database access permissions

## Testing the SQL Agent

The SQL Agent includes comprehensive test suites to verify functionality before deployment.

### Running Unit Tests

```bash
# Run all unit tests
python -m unittest discover tests/unit

# Run specific test file
python -m unittest tests/unit/test_query_engine.py
```

### Running Integration Tests

```bash
# Run all integration tests
python -m unittest discover tests/integration

# Run specific integration test
python -m unittest tests/integration/test_db_integration.py
```

### Running End-to-End Tests

```bash
# Run end-to-end tests
python tests/e2e/test_e2e.py
```

### Running Performance Tests

```bash
# Run performance validation
python deployment/performance_validation.py --config config/config.json
```

### Running User Acceptance Tests

```bash
# Run user acceptance tests in interactive mode
python deployment/user_acceptance.py --config config/config.json --interactive

# Run user acceptance tests with predefined test cases
python deployment/user_acceptance.py --config config/config.json --test-file tests/acceptance/test_cases.json
```

## Running the SQL Agent

The SQL Agent can be run using the main `app.py` script with different commands.

### Testing Database Connection

```bash
# Test database connection
python app.py test
```

### Extracting Database Schema

```bash
# Extract schema and generate documentation
python app.py schema

# Specify output directory
python app.py schema --output schema_docs
```

### Processing Natural Language Queries

```bash
# Process a query and display results
python app.py query "Show me all customers in Germany"

# Process a query and save results to file
python app.py query "List all orders from 2023" --output results.json
```

## Common Commands

Here are some example natural language queries to try:

1. "Show me all customers"
2. "List the top 10 products by sales"
3. "Find all orders placed in the last month"
4. "Show me the average order value by country"
5. "List employees who haven't made any sales"

## Troubleshooting

### Common Issues

#### Database Connection Errors

If you encounter database connection errors:

1. Verify database credentials in `config/config.json`
2. Check that the database server is running
3. Ensure network connectivity to the database server
4. Verify firewall settings allow the connection

#### Query Processing Errors

If natural language queries aren't processing correctly:

1. Check the query syntax and try simplifying the query
2. Verify the database schema has been extracted (`python app.py schema`)
3. Check logs for specific error messages (`logs/app.log`)

#### Performance Issues

If experiencing slow performance:

1. Run the performance validation (`python deployment/performance_validation.py`)
2. Check database indexing
3. Verify system resources (CPU, memory, disk)

For additional support, refer to the knowledge transfer documentation or contact the support team.
