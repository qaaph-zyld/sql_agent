# SQL Agent Troubleshooting Guide

*Last updated: 2025-06-04*

## Overview

This troubleshooting guide provides solutions for common issues encountered when using the SQL Agent system. It covers problems related to query generation, response processing, performance, and system integration.

## Table of Contents

1. [Query Engine Issues](#query-engine-issues)
2. [Response Processor Issues](#response-processor-issues)
3. [Database Connection Issues](#database-connection-issues)
4. [Performance Issues](#performance-issues)
5. [Security Issues](#security-issues)
6. [Changelog System Issues](#changelog-system-issues)
7. [Validation Suite Issues](#validation-suite-issues)
8. [Logging and Debugging](#logging-and-debugging)

## Query Engine Issues

### Issue: Query Generation Failures

**Symptoms:**
- Error message: "Failed to generate SQL query"
- Incomplete or invalid SQL queries
- Natural language processing errors

**Possible Causes:**
- Complex or ambiguous natural language input
- Missing schema information
- Unsupported SQL syntax

**Solutions:**
1. Simplify the natural language query
2. Update schema information using `schema_analyzer.py`
3. Check logs at `logs/query_engine.log` for specific errors
4. Verify that the query follows supported SQL syntax

```python
# Example: Update schema information
from scripts.core.schema_analyzer import SchemaAnalyzer

analyzer = SchemaAnalyzer()
analyzer.update_schema("database_name")
```

### Issue: Query Validation Errors

**Symptoms:**
- Error message: "Query validation failed"
- Security warnings in logs

**Possible Causes:**
- SQL injection attempts
- Unauthorized table or column access
- Syntax errors in generated queries

**Solutions:**
1. Check for potential SQL injection patterns
2. Verify access permissions for requested tables and columns
3. Review query syntax against database dialect

```sql
-- Example of a properly validated query
SELECT employee_name, department FROM employees WHERE department = 'Sales';

-- Example of a query that might fail validation (potential SQL injection)
SELECT employee_name, department FROM employees WHERE department = 'Sales' OR 1=1;
```

## Response Processor Issues

### Issue: Formatting Errors

**Symptoms:**
- Malformed output
- Missing data in results
- JSON parsing errors

**Possible Causes:**
- Unexpected data types in query results
- Formatting template errors
- Character encoding issues

**Solutions:**
1. Verify data types in query results
2. Check formatting templates in `config/formatting_templates.json`
3. Ensure proper character encoding (UTF-8 recommended)

```python
# Example: Set proper encoding for response processor
from scripts.core.response_processor import ResponseProcessor

processor = ResponseProcessor(encoding='utf-8')
```

### Issue: Visualization Failures

**Symptoms:**
- Missing charts or graphs
- Error message: "Failed to generate visualization"
- Blank or corrupted images

**Possible Causes:**
- Incompatible data format for visualization
- Missing visualization libraries
- Insufficient data points

**Solutions:**
1. Verify data format is compatible with selected visualization type
2. Check that required visualization libraries are installed
3. Ensure sufficient data points for meaningful visualization

```python
# Example: Generate a compatible visualization
from scripts.core.response_processor import ResponseProcessor

processor = ResponseProcessor()
processor.generate_visualization(
    data=query_results,
    visualization_type='bar_chart',
    x_column='category',
    y_column='value'
)
```

## Database Connection Issues

### Issue: Connection Failures

**Symptoms:**
- Error message: "Failed to connect to database"
- Timeout errors
- Authentication failures

**Possible Causes:**
- Incorrect connection string
- Network connectivity issues
- Invalid credentials
- Database server down

**Solutions:**
1. Verify connection string in `.env` file
2. Check network connectivity to database server
3. Validate credentials
4. Confirm database server is running

```python
# Example: Test database connection
from scripts.core.db_connector import DatabaseConnector

connector = DatabaseConnector()
connection_status = connector.test_connection()
print(f"Connection status: {connection_status}")
```

### Issue: Query Execution Timeout

**Symptoms:**
- Error message: "Query execution timed out"
- Long-running queries without results

**Possible Causes:**
- Complex queries with large data sets
- Missing indexes
- Database server resource constraints

**Solutions:**
1. Optimize query with proper indexing
2. Add query timeout parameter
3. Consider breaking complex queries into smaller parts

```python
# Example: Set query timeout
from scripts.core.query_engine import QueryEngine

engine = QueryEngine()
results = engine.execute_query(query, timeout_seconds=30)
```

## Performance Issues

### Issue: Slow Query Generation

**Symptoms:**
- Long wait times for query generation
- High CPU usage during query generation

**Possible Causes:**
- Complex natural language processing
- Large schema with many tables and columns
- Insufficient system resources

**Solutions:**
1. Simplify natural language input
2. Optimize schema representation
3. Increase system resources
4. Enable caching for frequently used queries

```python
# Example: Enable query caching
from scripts.core.query_engine import QueryEngine

engine = QueryEngine(enable_caching=True, cache_size=100)
```

### Issue: Slow Response Processing

**Symptoms:**
- Long wait times for response formatting
- High memory usage during visualization generation

**Possible Causes:**
- Large result sets
- Complex visualizations
- Memory leaks

**Solutions:**
1. Limit result set size
2. Simplify visualizations
3. Optimize memory usage in response processor
4. Use pagination for large result sets

```python
# Example: Use pagination for large result sets
from scripts.core.response_processor import ResponseProcessor

processor = ResponseProcessor()
paginated_results = processor.paginate_results(
    results=query_results,
    page_size=100,
    page_number=1
)
```

## Security Issues

### Issue: Potential SQL Injection

**Symptoms:**
- Security warnings in logs
- Unexpected query behavior
- Access to unauthorized data

**Possible Causes:**
- Insufficient input validation
- Bypassed query validation
- Vulnerable query construction

**Solutions:**
1. Ensure all user input is properly validated
2. Use parameterized queries
3. Implement strict query validation rules
4. Review security test results

```python
# Example: Use parameterized queries
from scripts.core.query_engine import QueryEngine

engine = QueryEngine()
query = "SELECT * FROM employees WHERE department = %s"
parameters = ["Sales"]
results = engine.execute_parameterized_query(query, parameters)
```

### Issue: Unauthorized Access Attempts

**Symptoms:**
- Security warnings in logs
- Access attempts to restricted tables
- Suspicious query patterns

**Possible Causes:**
- Missing access controls
- Insufficient authentication
- Privilege escalation attempts

**Solutions:**
1. Implement table-level access controls
2. Enforce user authentication
3. Audit query patterns for suspicious activity
4. Use row-level security where applicable

```python
# Example: Check table access permissions
from scripts.core.security_manager import SecurityManager

security_manager = SecurityManager()
has_access = security_manager.check_table_access(
    user_id="user123",
    table_name="employees",
    access_type="SELECT"
)
```

## Changelog System Issues

### Issue: Missing Changelog Entries

**Symptoms:**
- Validation failures for changelog
- Incomplete changelog history
- Missing file modification records

**Possible Causes:**
- Manual edits bypassing changelog system
- Failed changelog updates
- Corrupted changelog file

**Solutions:**
1. Always use the changelog engine for updates
2. Restore from backup if corruption is detected
3. Regenerate missing entries using file history

```python
# Example: Force changelog update
from scripts.core.changelog_engine import ChangelogEngine

engine = ChangelogEngine()
engine.force_update(
    action_summary="Manual changelog correction",
    files_affected=["path/to/modified/file.py"]
)
```

### Issue: Changelog Format Errors

**Symptoms:**
- Validation failures for changelog format
- Parsing errors when reading changelog
- Inconsistent formatting

**Possible Causes:**
- Manual edits to changelog file
- Version conflicts
- Incomplete entries

**Solutions:**
1. Use changelog templates for consistent formatting
2. Validate changelog format regularly
3. Fix formatting issues using the changelog engine

```python
# Example: Validate changelog format
from scripts.core.validation_suite import ValidationSuite

validator = ValidationSuite()
format_validation = validator.validate_changelog_format("Changelog.md")
print(f"Format validation: {format_validation}")
```

## Validation Suite Issues

### Issue: Validation Failures

**Symptoms:**
- Failed validation checks
- Error messages from validation suite
- CI/CD pipeline failures

**Possible Causes:**
- Structural changes without documentation updates
- Performance degradation
- Security vulnerabilities
- Changelog inconsistencies

**Solutions:**
1. Address specific validation failures
2. Update documentation to match structural changes
3. Optimize performance for failing operations
4. Fix security vulnerabilities
5. Correct changelog inconsistencies

```python
# Example: Run specific validation checks
from scripts.core.validation_suite import ValidationSuite

validator = ValidationSuite()
results = validator.run_specific_validation(
    validation_types=["structural", "performance"],
    fix_issues=True
)
```

### Issue: False Positive Validation Failures

**Symptoms:**
- Validation failures for correct implementations
- Inconsistent validation results

**Possible Causes:**
- Outdated validation rules
- Incorrect expected values
- Environment-specific issues

**Solutions:**
1. Update validation rules to match current requirements
2. Adjust expected values for validation checks
3. Account for environment-specific factors

```python
# Example: Update validation thresholds
from scripts.core.validation_suite import ValidationSuite

validator = ValidationSuite(
    performance_threshold_ms=100,  # Adjusted threshold
    structure_compliance_threshold=0.95  # Allow for some flexibility
)
```

## Logging and Debugging

### Issue: Missing Log Information

**Symptoms:**
- Insufficient information in logs
- Unable to diagnose issues
- Generic error messages

**Possible Causes:**
- Incorrect log level
- Log configuration issues
- Log rotation problems

**Solutions:**
1. Set appropriate log level (DEBUG for detailed information)
2. Verify log configuration in `config/logging_config.json`
3. Check log rotation settings

```python
# Example: Set detailed logging
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='logs/detailed_debug.log'
)
```

### Issue: Log File Size Issues

**Symptoms:**
- Very large log files
- Disk space warnings
- Slow log file access

**Possible Causes:**
- Missing log rotation
- Excessive logging
- Debug mode in production

**Solutions:**
1. Implement log rotation
2. Adjust log levels for production
3. Archive old log files

```python
# Example: Configure log rotation
import logging
from logging.handlers import RotatingFileHandler

handler = RotatingFileHandler(
    'logs/app.log',
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5
)
logger = logging.getLogger()
logger.addHandler(handler)
```

## Advanced Troubleshooting

For issues not covered in this guide, consider the following approaches:

1. **System Diagnostics**
   - Run the comprehensive diagnostic tool:
   ```bash
   python scripts/tools/run_diagnostics.py --comprehensive
   ```

2. **Performance Profiling**
   - Profile specific components:
   ```bash
   python scripts/tools/profile_component.py --component query_engine
   ```

3. **Community Support**
   - Check the issue tracker for similar problems
   - Consult the SQL Agent community forum

4. **Contact Support**
   - For enterprise users, contact technical support with:
     - Detailed issue description
     - Log files
     - System configuration
     - Steps to reproduce

## Conclusion

This troubleshooting guide covers the most common issues encountered when using the SQL Agent system. If you encounter an issue not covered in this guide, please consult the API documentation or contact support for assistance.
