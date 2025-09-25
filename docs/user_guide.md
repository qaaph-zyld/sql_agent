# SQL Agent User Guide

*Last updated: 2025-06-04*

## Introduction

Welcome to the SQL Agent User Guide. This document provides instructions on how to use the SQL Agent system to generate, execute, and visualize SQL queries using natural language.

## Getting Started

### System Requirements

- Modern web browser (Chrome, Firefox, Safari, Edge)
- Network access to the SQL Agent server
- Valid user credentials

### Logging In

1. Navigate to the SQL Agent web interface at `https://sqlagent.example.com`
2. Enter your username and password
3. Click "Login"

## Using the Query Interface

### Creating a Query

1. From the dashboard, click "New Query"
2. Type your question in natural language (e.g., "Show me sales by region for last quarter")
3. Select the target database from the dropdown menu
4. Click "Generate SQL"

The system will analyze your question and generate the appropriate SQL query.

### Reviewing and Editing the Generated SQL

After SQL generation:

1. Review the generated SQL in the editor
2. Make any necessary modifications
3. Click "Validate" to check your changes

### Executing Queries

Once your query is validated:

1. Click "Execute" to run the query
2. View the results in the results panel
3. Use the pagination controls to navigate through large result sets

## Working with Results

### Formatting Options

The SQL Agent provides several formatting options for query results:

- **Table View**: Default view showing data in rows and columns
- **JSON View**: Data formatted as JSON objects
- **CSV View**: Data formatted as comma-separated values

To change the format:

1. Click the "Format" dropdown in the results panel
2. Select your preferred format

### Data Visualization

To create visualizations from your query results:

1. Click "Visualize" in the results panel
2. Select a visualization type (bar chart, line chart, pie chart, etc.)
3. Map your data columns to visualization parameters
4. Click "Generate Visualization"

### Saving and Exporting

#### Saving Queries

To save a query for future use:

1. Click "Save" in the query editor
2. Enter a name and optional description
3. Click "Save Query"

#### Exporting Results

To export your results:

1. Click "Export" in the results panel
2. Select an export format (CSV, Excel, JSON, PDF)
3. Click "Export"

## Advanced Features

### Query Templates

SQL Agent provides templates for common query types:

1. Click "Templates" in the query editor
2. Select a template category
3. Choose a specific template
4. Customize the template parameters

### Scheduled Queries

To schedule a query to run automatically:

1. Save your query
2. Click "Schedule" from the saved queries list
3. Set the frequency and timing
4. Click "Save Schedule"

## Troubleshooting

### Common Issues

#### Query Generation Failures

If the system fails to generate SQL:
- Simplify your natural language query
- Be more specific about what data you need
- Check that you're referencing valid tables and fields

#### Execution Errors

If your query fails to execute:
- Check the error message for specific issues
- Verify that referenced tables and columns exist
- Ensure you have permission to access the data

#### Slow Performance

If queries are running slowly:
- Limit the date range in your query
- Reduce the number of joins
- Add appropriate filters

### Getting Help

For additional assistance:
- Click the "Help" icon in the top navigation
- Check the knowledge base for similar issues
- Contact support through the "Support" tab

## Conclusion

This user guide covers the basic functionality of the SQL Agent system. For more detailed information on specific features, please refer to the API documentation and administrator manual.
