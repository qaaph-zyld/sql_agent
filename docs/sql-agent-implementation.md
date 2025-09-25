# SQL Database Querying Agent Implementation Guide

## Project Overview

This guide outlines the implementation of an AI-powered SQL querying agent designed to interpret natural language questions about production data and generate appropriate SQL queries. The system facilitates database interaction without requiring users to write SQL code directly.

## Core Requirements

- Natural language to SQL query translation
- Support for queries about production metrics
- Filtering capabilities for specific part numbers, time periods
- Customizable output formats
- Open source technology stack
- Automated, step-by-step query processing

## System Architecture

```
┌─────────────────┐     ┌───────────────┐     ┌────────────────┐
│ Natural Language│     │ Query         │     │ Database       │
│ Input           │────▶│ Translation   │────▶│ Interaction    │
└─────────────────┘     └───────────────┘     └────────────────┘
                                                      │
┌─────────────────┐     ┌───────────────┐            │
│ Formatted       │     │ Response      │◀───────────┘
│ Output          │◀────│ Processing    │
└─────────────────┘     └───────────────┘
```

## Technology Stack

- **LlamaIndex**: Core framework for query translation
- **SQLAlchemy**: Database interaction layer
- **OpenAI**: LLM for natural language understanding
- **Python**: Implementation language
- **PyMSSQL**: Microsoft SQL Server connector

## Implementation Plan

### 1. Environment Setup

```bash
mkdir sql-agent
cd sql-agent
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install llama-index-llms-openai llama-index-readers-database llama-index python-dotenv sqlalchemy pymssql
```

### 2. Project Structure

```
sql-agent/
├── .env                    # Environment variables
├── app.py                  # Main application entry point
├── db_connector.py         # Database connection utilities
├── query_engine.py         # Natural language to SQL processing
├── schema_extractor.py     # Database schema documentation tools
├── output_formatter.py     # Response formatting utilities
└── sample_queries.json     # Example queries for testing
```

### 3. Environment Configuration (.env)

```
DB_HOST=your_host
DB_NAME=your_db_name
DB_USER=your_username
DB_PASSWORD=your_password
OPENAI_API_KEY=your_openai_key
```

### 4. Schema Documentation Utility (schema_extractor.py)

```python
import sqlalchemy as sa
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import json

load_dotenv()

def get_connection_string():
    return f"mssql+pymssql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"

def get_engine():
    connection_string = get_connection_string()
    return create_engine(connection_string)

def extract_schema():
    """Extract database schema information and save to file"""
    schema_query = """
    SELECT 
        t.name AS TableName,
        c.name AS ColumnName,
        ty.name AS DataType,
        c.max_length AS MaxLength,
        c.is_nullable AS IsNullable,
        ISNULL(ep.value, '') AS Description
    FROM 
        sys.tables t
    INNER JOIN 
        sys.columns c ON t.object_id = c.object_id
    INNER JOIN 
        sys.types ty ON c.user_type_id = ty.user_type_id
    LEFT JOIN
        sys.extended_properties ep ON t.object_id = ep.major_id 
        AND c.column_id = ep.minor_id 
        AND ep.name = 'MS_Description'
    ORDER BY 
        t.name, c.column_id;
    """
    
    engine = get_engine()
    
    with engine.connect() as conn:
        result = conn.execute(text(schema_query))
        rows = result.fetchall()
        
    schema_info = {}
    for row in rows:
        table_name = row[0]
        column_info = {
            "name": row[1],
            "type": row[2],
            "max_length": row[3],
            "nullable": row[4],
            "description": row[5]
        }
        
        if table_name not in schema_info:
            schema_info[table_name] = []
            
        schema_info[table_name].append(column_info)
    
    # Save schema to file
    with open('db_schema.json', 'w') as f:
        json.dump(schema_info, f, indent=2)
    
    return schema_info

def print_schema_summary():
    """Print a human-readable summary of the schema"""
    if not os.path.exists('db_schema.json'):
        schema = extract_schema()
    else:
        with open('db_schema.json', 'r') as f:
            schema = json.load(f)
    
    for table, columns in schema.items():
        print(f"\n=== Table: {table} ===")
        for col in columns:
            nullable = "NULL" if col['nullable'] else "NOT NULL"
            print(f"  - {col['name']} ({col['type']}, {nullable})")
            if col['description']:
                print(f"    Description: {col['description']}")

if __name__ == "__main__":
    print_schema_summary()
```

### 5. Database Connector (db_connector.py)

```python
from llama_index.readers.database import DatabaseReader
from sqlalchemy import create_engine, MetaData
import os
from dotenv import load_dotenv
import json

load_dotenv()

def get_db_engine():
    """Create and return a SQLAlchemy engine for database connection"""
    connection_string = f"mssql+pymssql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
    return create_engine(connection_string)

def get_db_reader():
    """Create a DatabaseReader instance for LlamaIndex"""
    engine = get_db_engine()
    return DatabaseReader(engine=engine)

def get_table_metadata(table_names=None):
    """Retrieve metadata for specified tables or all tables"""
    engine = get_db_engine()
    metadata = MetaData()
    
    if table_names:
        metadata.reflect(engine, only=table_names)
    else:
        metadata.reflect(engine)
    
    return metadata

def execute_direct_query(query, params=None):
    """Execute a raw SQL query and return results"""
    engine = get_db_engine()
    
    with engine.connect() as connection:
        result = connection.execute(query, params or {})
        columns = result.keys()
        rows = [dict(zip(columns, row)) for row in result.fetchall()]
    
    return {
        "columns": columns,
        "rows": rows
    }
```

### 6. Query Engine (query_engine.py)

```python
from llama_index import VectorStoreIndex
from llama_index.llms import OpenAI
from llama_index.indices.struct_store import SQLTableSchema
from llama_index.indices.struct_store.sql_query import NLSQLTableQueryEngine
from db_connector import get_db_engine, get_table_metadata
import sqlalchemy as sa
import os
import json
from dotenv import load_dotenv

load_dotenv()

def load_schema_context():
    """Load schema information with descriptions for context enhancement"""
    if os.path.exists('db_schema.json'):
        with open('db_schema.json', 'r') as f:
            return json.load(f)
    return {}

def create_table_schemas(table_names=None):
    """Create SQLTableSchema objects for the specified tables"""
    schema_info = load_schema_context()
    
    metadata = get_table_metadata(table_names)
    table_schemas = []
    
    for table_name, table in metadata.tables.items():
        # Create context description from schema info
        context = f"Table {table_name} contains "
        
        if table_name in schema_info:
            column_descriptions = []
            for col in schema_info[table_name]:
                desc = f"{col['name']} ({col['type']})"
                if col['description']:
                    desc += f": {col['description']}"
                column_descriptions.append(desc)
            
            context += "columns: " + ", ".join(column_descriptions)
        else:
            context += "various columns related to parts and production data"
        
        table_schema = SQLTableSchema(
            table_name=table_name,
            context_str=context
        )
        table_schemas.append(table_schema)
    
    return table_schemas

def create_query_engine(table_names=None):
    """Create a natural language to SQL query engine"""
    engine = get_db_engine()
    table_schemas = create_table_schemas(table_names)
    
    # Initialize the LLM
    llm = OpenAI(api_key=os.getenv('OPENAI_API_KEY'), temperature=0.1)
    
    # Create the NL to SQL query engine
    query_engine = NLSQLTableQueryEngine(
        sql_database=engine,
        tables=table_schemas,
        llm=llm
    )
    
    return query_engine

def execute_query(query_text, table_names=None):
    """Process a natural language query and return results"""
    query_engine = create_query_engine(table_names)
    
    # Add query refinement with specific context
    if "week" in query_text.lower():
        query_text += " Note: Week numbers can be calculated from date fields using ISO week standards."
    
    if "production" in query_text.lower() or "produced" in query_text.lower():
        query_text += " Note: Production is indicated by tr_type = 'RCT-WO' in transaction records."
    
    response = query_engine.query(query_text)
    return response
```

### 7. Output Formatter (output_formatter.py)

```python
import json
import pandas as pd
import matplotlib.pyplot as plt
import io
import base64

def format_output(query_result, format_type="tabular"):
    """Format the query results according to the specified format"""
    
    # Extract result data
    result_text = query_result.response
    result_metadata = getattr(query_result, 'metadata', {})
    
    if format_type == "summary":
        # Extract just count/aggregate with context
        return {
            "format": "summary",
            "result": result_text,
            "query": getattr(query_result, 'query', '')
        }
        
    elif format_type == "json":
        # Convert to machine-readable format
        return {
            "format": "json",
            "result": result_metadata if result_metadata else {"text": result_text},
            "query": getattr(query_result, 'query', '')
        }
        
    elif format_type == "chart":
        # Generate chart configuration and data
        # This is just a placeholder - actual implementation would depend on the data structure
        try:
            # Try to parse result as data for charting
            if hasattr(query_result, 'pandas_df'):
                df = query_result.pandas_df
            else:
                # Create DataFrame from result text if possible
                # This is a simplified approach and may need refinement
                lines = result_text.strip().split('\n')
                if len(lines) > 1:
                    headers = [h.strip() for h in lines[0].split('|') if h.strip()]
                    data = []
                    for line in lines[2:]:  # Skip header separator line
                        row = [cell.strip() for cell in line.split('|') if cell.strip()]
                        if len(row) == len(headers):
                            data.append(row)
                    
                    df = pd.DataFrame(data, columns=headers)
                    # Convert numeric columns
                    for col in df.columns:
                        try:
                            df[col] = pd.to_numeric(df[col])
                        except:
                            pass
                else:
                    raise ValueError("Insufficient data for charting")
                
            # Create a simple chart based on data types
            plt.figure(figsize=(10, 6))
            
            if len(df.columns) >= 2:
                # Identify numeric columns for y-axis
                x_col = df.columns[0]
                numeric_cols = df.select_dtypes(include=['number']).columns
                
                if len(numeric_cols) > 0:
                    y_col = numeric_cols[0]
                    df.plot(x=x_col, y=y_col, kind='bar')
                    plt.title(f"{y_col} by {x_col}")
                    plt.tight_layout()
                    
                    # Convert plot to base64 string
                    buffer = io.BytesIO()
                    plt.savefig(buffer, format='png')
                    buffer.seek(0)
                    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
                    
                    return {
                        "format": "chart",
                        "chart_type": "bar",
                        "image_data": f"data:image/png;base64,{image_base64}",
                        "raw_data": df.to_dict(orient='records')
                    }
            
            raise ValueError("Could not determine appropriate chart type for data")
                
        except Exception as e:
            # Fall back to tabular if charting fails
            return {
                "format": "tabular",
                "result": result_text,
                "error": f"Could not create chart: {str(e)}"
            }
    
    else:  # Default tabular format
        return {
            "format": "tabular",
            "result": result_text,
            "query": getattr(query_result, 'query', '')
        }
```

### 8. Main Application (app.py)

```python
from query_engine import execute_query
from output_formatter import format_output
import json
import argparse
import os

def load_sample_queries():
    """Load sample queries from configuration file"""
    if os.path.exists('sample_queries.json'):
        with open('sample_queries.json', 'r') as f:
            return json.load(f)
    return []

def get_relevant_tables(query_text):
    """Determine relevant tables based on query content"""
    # This is a simplified approach - in production, you'd want more sophisticated logic
    query_lower = query_text.lower()
    
    tables = []
    
    # Add logic to identify relevant tables based on query keywords
    if "part" in query_lower or "item" in query_lower:
        tables.append("dbo.parts")  # Adjust to your actual table name
    
    if "produc" in query_lower or "manufactur" in query_lower or "week" in query_lower:
        tables.append("dbo.production")  # Adjust to your actual table name
    
    # If no specific tables identified, return empty list (will use all tables)
    return tables if tables else None

def main():
    parser = argparse.ArgumentParser(description='SQL Query Agent')
    parser.add_argument('--query', type=str, help='Natural language query')
    parser.add_argument('--sample', type=int, help='Use sample query by index')
    parser.add_argument('--format', type=str, choices=['tabular', 'summary', 'json', 'chart'], 
                        default='tabular', help='Output format')
    parser.add_argument('--interactive', action='store_true', help='Run in interactive mode')
    args = parser.parse_args()
    
    if args.interactive:
        # Interactive mode
        print("SQL Query Agent - Interactive Mode")
        print("Type 'exit' to quit")
        
        while True:
            query_text = input("\nEnter your query: ")
            if query_text.lower() == 'exit':
                break
                
            relevant_tables = get_relevant_tables(query_text)
            
            try:
                response = execute_query(query_text, relevant_tables)
                formatted_response = format_output(response, args.format)
                
                print("\nQuery Result:")
                if isinstance(formatted_response, dict):
                    if formatted_response.get('format') == 'json':
                        print(json.dumps(formatted_response.get('result', {}), indent=2))
                    else:
                        print(formatted_response.get('result', 'No result'))
                else:
                    print(formatted_response)
                    
            except Exception as e:
                print(f"Error processing query: {str(e)}")
    else:
        # Single query mode
        if args.query:
            query_text = args.query
        elif args.sample is not None:
            samples = load_sample_queries()
            if samples and 0 <= args.sample < len(samples):
                query_text = samples[args.sample]['query']
                print(f"Using sample query: {query_text}")
            else:
                print(f"Sample index must be between 0 and {len(samples)-1}")
                return
        else:
            query_text = input("Enter your query: ")
        
        relevant_tables = get_relevant_tables(query_text)
        
        try:
            response = execute_query(query_text, relevant_tables)
            formatted_response = format_output(response, args.format)
            
            print("\nQuery Result:")
            if isinstance(formatted_response, dict):
                if formatted_response.get('format') == 'json':
                    print(json.dumps(formatted_response.get('result', {}), indent=2))
                else:
                    print(formatted_response.get('result', 'No result'))
            else:
                print(formatted_response)
                
        except Exception as e:
            print(f"Error processing query: {str(e)}")

if __name__ == "__main__":
    main()
```

### 9. Sample Queries Configuration (sample_queries.json)

```json
[
    {
        "query": "How many parts of 5414515 were produced in week 21 of 2024?",
        "description": "Count query with item filter and time range",
        "expected_tables": ["dbo.production"]
    },
    {
        "query": "Extract item numbers without production line (tr_prod_line = '0000')",
        "description": "Filter query with exclusion condition",
        "expected_tables": ["dbo.parts", "dbo.production"]
    },
    {
        "query": "What was the total production quantity in April 2022?",
        "description": "Aggregate query with time range",
        "expected_tables": ["dbo.production"]
    },
    {
        "query": "List the top 5 most produced parts in 2023",
        "description": "Rank query with time range",
        "expected_tables": ["dbo.parts", "dbo.production"]
    }
]
```

## Database Schema Refinement

Before implementing the agent, it's recommended to clean up your database schema:

1. **Field Standardization**: Rename fields using consistent naming conventions
2. **Remove Unused Columns**: Drop columns that are not utilized in queries
3. **Add Column Descriptions**: Document the purpose of each column
4. **Create Views**: Consider creating views for commonly accessed data combinations

This refinement will:
- Improve query performance
- Simplify query generation
- Enhance natural language understanding
- Reduce maintenance complexity

## Usage Instructions

### Setup

1. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure database connection in `.env` file
   ```
   DB_HOST=your_host
   DB_NAME=your_db_name
   DB_USER=your_username
   DB_PASSWORD=your_password
   OPENAI_API_KEY=your_openai_key
   ```

3. Extract and document your database schema:
   ```bash
   python schema_extractor.py
   ```

### Running the Agent

#### Interactive Mode
```bash
python app.py --interactive --format tabular
```

#### Single Query
```bash
python app.py --query "How many parts of 5414515 were produced in week 21 of 2024?" --format summary
```

#### Using Sample Queries
```bash
python app.py --sample 0 --format chart
```

## Extending the System

### Custom Query Templates

Add specialized templates for common query patterns:

```python
# In query_engine.py
def add_query_templates(query_engine):
    templates = [
        "SELECT COUNT(*) FROM production WHERE part_number = {part_number} AND DATEPART(week, production_date) = {week} AND DATEPART(year, production_date) = {year}",
        "SELECT part_number FROM parts WHERE production_line != {production_line}"
    ]
    
    for template in templates:
        query_engine.add_query_template(template)
    
    return query_engine
```

### Additional Output Formats

Extend the output formatter to support new formats:

```python
# In output_formatter.py
def format_as_excel(result_data):
    """Format results as Excel file"""
    # Implementation here
```

## Conclusion

This implementation provides a robust foundation for natural language querying of SQL databases. By following the open-source approach with LlamaIndex and related technologies, the system can be incrementally extended and refined to meet evolving requirements while maintaining a clean, modular architecture.
