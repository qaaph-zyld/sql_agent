# SQL Agent User Guide

## Introduction

SQL Agent is a comprehensive tool for SQL Server database analysis and reporting. This guide will help you get started with using SQL Agent for database connectivity, query execution, and specialized analysis.

## Installation

### Prerequisites

- Python 3.6 or higher
- Access to a SQL Server database

### Setup

1. Install the SQL Agent package:
   ```powershell
   # Using the setup script (Windows)
   .\setup_and_test.bat

   # Or manually
   python -m venv venv
   .\venv\Scripts\activate
   pip install -e .
   ```

2. Configure your database connection:
   - Edit `configs/database.json` with your database credentials
   - Or set environment variables in a `.env` file:
     ```
     DB_SERVER=a265m001
     DB_NAME=QADEE2798
     DB_USER=PowerBI
     DB_PASSWORD=P0werB1
     ```

## SQL Command-Line Interface

The SQL CLI provides a convenient way to interact with your database from the command line.

### Basic Commands

#### Help
```powershell
sql-cli --help
```

#### Test Connection
```powershell
sql-cli test
```

#### List Tables
```powershell
sql-cli list
```

#### Describe a Table
```powershell
sql-cli describe --table tr_hist
```

#### Execute a Query
```powershell
sql-cli query --sql "SELECT TOP 10 * FROM tr_hist WHERE tr_type = 'RCT-WO'"
```

### Output Formats

You can specify different output formats:

```powershell
# Text format (default)
sql-cli query --sql "SELECT * FROM tr_hist LIMIT 10" --format text

# JSON format
sql-cli query --sql "SELECT * FROM tr_hist LIMIT 10" --format json

# CSV format
sql-cli query --sql "SELECT * FROM tr_hist LIMIT 10" --format csv --output results.csv
```

### Saving Results

```powershell
# Save to a file
sql-cli query --sql "SELECT * FROM tr_hist" --output query_results.txt

# Save to JSON
sql-cli query --sql "SELECT * FROM tr_hist" --format json --output query_results.json
```

## RCT-WO Analysis

The RCT-WO analysis module provides specialized analysis for RCT-WO transactions.

### Running the Analysis

```powershell
# Run the full analysis
python -m sql_agent.analysis.rct_wo.analysis

# Test the database connection
python -m sql_agent.analysis.rct_wo.connection_test
```

### Analysis Options

You can customize the analysis by editing `configs/app_config.json`:

```json
{
  "features": {
    "rct_wo_analysis": {
      "enabled": true,
      "default_date_range": "last_month",
      "generate_html_report": true,
      "generate_visualizations": true
    }
  }
}
```

### Analysis Output

The analysis generates several outputs:

- Text reports in `results/text/`
- JSON data in `results/json/`
- HTML reports in `results/html/`
- Visualizations in `results/visualizations/`

## Working with Database Tables

### Exploring Database Schema

```powershell
# List all tables
sql-cli list

# Get table details
sql-cli describe --table tr_hist

# Get column information
sql-cli describe --table tr_hist --columns
```

### Common Tables

- `tr_hist`: Transaction history
- `pt_mstr`: Part master
- `po_mstr`: Purchase order master

### Sample Queries

#### Transaction Analysis
```sql
SELECT 
    tr_type, 
    COUNT(*) as transaction_count, 
    SUM(tr_qty_chg) as total_quantity
FROM 
    tr_hist
WHERE 
    tr_date BETWEEN '2025-05-01' AND '2025-05-31'
GROUP BY 
    tr_type
ORDER BY 
    transaction_count DESC
```

#### Part Information
```sql
SELECT 
    pt_part, 
    pt_desc, 
    pt_um, 
    pt_group
FROM 
    pt_mstr
WHERE 
    pt_group = 'ELEC'
```

#### Joining Tables
```sql
SELECT 
    t.tr_part, 
    p.pt_desc, 
    t.tr_type, 
    t.tr_qty_chg, 
    t.tr_date
FROM 
    tr_hist t
JOIN 
    pt_mstr p ON t.tr_part = p.pt_part
WHERE 
    t.tr_type = 'RCT-WO'
    AND t.tr_date >= DATEADD(month, -1, GETDATE())
```

## Troubleshooting

### Common Issues

#### Connection Problems
```
Error: Could not connect to database server
```

**Solution**: 
- Verify your database credentials in `configs/database.json`
- Check that the database server is accessible from your network
- Ensure you have the correct permissions

#### Import Errors
```
ModuleNotFoundError: No module named 'sql_agent'
```

**Solution**:
- Make sure you've installed the package: `pip install -e .`
- Verify that your virtual environment is activated
- Check that the package is installed correctly: `pip list | grep sql-agent`

#### Query Execution Errors
```
Error executing query: Invalid column name 'column_name'
```

**Solution**:
- Verify the column names in your query
- Check the table schema using `sql-cli describe --table table_name`
- Test with a simpler query to isolate the issue

### Getting Help

If you encounter issues:

1. Check the logs in the `logs/` directory
2. Review the error messages for specific details
3. Consult the documentation in the `docs/` directory
4. Contact the development team for support

## Advanced Usage

### Creating Custom Analysis Modules

You can create custom analysis modules by extending the SQL Agent framework:

1. Create a new module in `src/sql_agent/analysis/`
2. Implement your analysis logic
3. Use the core database connectivity features

Example:
```python
from sql_agent.core.db_connector import DatabaseConnector

def run_custom_analysis():
    # Connect to the database
    db = DatabaseConnector()
    conn = db.get_connection()
    
    # Execute your analysis queries
    cursor = conn.cursor()
    cursor.execute("YOUR CUSTOM QUERY")
    results = cursor.fetchall()
    
    # Process and output results
    for row in results:
        print(row)
```

### Scheduling Analysis Jobs

You can schedule analysis jobs using Windows Task Scheduler or cron:

#### Windows Task Scheduler
```powershell
# Create a batch file to run the analysis
@echo off
cd C:\path\to\sql_agent
call venv\Scripts\activate
python -m sql_agent.analysis.rct_wo.analysis
```

Then create a scheduled task to run this batch file at your desired interval.

#### Cron (Linux/Mac)
```bash
# Add to crontab
0 8 * * 1 cd /path/to/sql_agent && source venv/bin/activate && python -m sql_agent.analysis.rct_wo.analysis
```

## Conclusion

This guide covers the basic usage of SQL Agent. For more detailed information, refer to the API documentation and other resources in the `docs/` directory.
