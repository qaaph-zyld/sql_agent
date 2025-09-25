# SQL Agent API Documentation

*Last updated: 2025-06-04*

## Overview

The SQL Agent API provides programmatic access to the SQL Agent system's functionality, allowing developers to integrate SQL query generation, execution, and response processing into their applications.

## Base URL

```
https://api.sqlagent.example.com/v1
```

## Authentication

All API requests require authentication using an API key. Include your API key in the request header:

```
Authorization: Bearer YOUR_API_KEY
```

## Core Endpoints

### Query Generation

```
POST /query/generate
```

Generates SQL from natural language.

**Example Request:**
```json
{
  "natural_language_query": "Show sales by region",
  "database_dialect": "postgresql"
}
```

**Example Response:**
```json
{
  "query_id": "q-12345",
  "generated_sql": "SELECT region, SUM(amount) FROM sales GROUP BY region;"
}
```

### Query Execution

```
POST /query/execute
```

Executes a validated SQL query.

**Example Request:**
```json
{
  "sql_query": "SELECT region, SUM(amount) FROM sales GROUP BY region;"
}
```

**Example Response:**
```json
{
  "execution_id": "e-12345",
  "status": "success",
  "results": [
    {"region": "North", "sum": 12500},
    {"region": "South", "sum": 9800}
  ]
}
```

### Response Formatting

```
POST /response/format
```

Formats query results.

**Example Request:**
```json
{
  "execution_id": "e-12345",
  "format": "table"
}
```

**Example Response:**
```json
{
  "formatted_response": {
    "type": "table",
    "headers": ["Region", "Total Sales"],
    "rows": [
      ["North", "12,500"],
      ["South", "9,800"]
    ]
  }
}
```

## Error Handling

All API endpoints return standard HTTP status codes:

- 200: Success
- 400: Bad request
- 401: Unauthorized
- 500: Server error

Error responses include a message field with details.

## Rate Limits

- 100 requests per minute
- 1000 requests per hour

## For More Information

See the detailed documentation for each endpoint in the User Guide.
