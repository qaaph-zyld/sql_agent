"""
Database Field Information Extractor

This script connects to the SQL Server database and extracts field information
for specified tables, including field names, data types, and descriptions.
"""

import os
import sqlalchemy as sa
from sqlalchemy import create_engine, text
import pandas as pd

# Database connection parameters
DB_HOST = "a265m001"
DB_NAME = "QADEE2798"
DB_USER = "PowerBI"
DB_PASSWORD = "P0werB1"

def get_connection_string():
    """Create the database connection string"""
    return f"mssql+pymssql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

def get_engine():
    """Create and return a SQLAlchemy engine"""
    connection_string = get_connection_string()
    return create_engine(connection_string)

def extract_table_fields(table_name):
    """
    Extract field information for a specific table
    
    Args:
        table_name: Name of the table to extract field information for
        
    Returns:
        DataFrame containing field information
    """
    # SQL query to extract field information
    field_query = f"""
    SELECT 
        c.name AS ColumnName,
        t.name AS DataType,
        c.max_length AS MaxLength,
        c.is_nullable AS IsNullable,
        ISNULL(ep.value, '') AS Description,
        c.column_id AS ColumnID
    FROM 
        sys.columns c
    INNER JOIN 
        sys.types t ON c.user_type_id = t.user_type_id
    INNER JOIN
        sys.tables tbl ON c.object_id = tbl.object_id
    LEFT JOIN
        sys.extended_properties ep ON c.object_id = ep.major_id 
        AND c.column_id = ep.minor_id 
        AND ep.name = 'MS_Description'
    WHERE 
        tbl.name = '{table_name}'
    ORDER BY 
        c.column_id;
    """
    
    try:
        # Create engine and connect to database
        engine = get_engine()
        
        # Execute query and fetch results
        with engine.connect() as conn:
            result = conn.execute(text(field_query))
            rows = result.fetchall()
            
        # Convert results to DataFrame
        if rows:
            df = pd.DataFrame(rows, columns=['ColumnName', 'DataType', 'MaxLength', 'IsNullable', 'Description', 'ColumnID'])
            return df
        else:
            print(f"No fields found for table {table_name}")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"Error extracting field information: {str(e)}")
        return pd.DataFrame()

def save_field_names_markdown(table_name, output_path):
    """
    Save field names to a markdown file
    
    Args:
        table_name: Name of the table
        output_path: Path to save the markdown file
    """
    # Extract field information
    df = extract_table_fields(table_name)
    
    if df.empty:
        print(f"No field information available for table {table_name}")
        return
    
    # Create markdown content
    markdown_content = f"# Field Names for Table: {table_name}\n\n"
    markdown_content += "| Field Name | Data Type | Description |\n"
    markdown_content += "|------------|-----------|-------------|\n"
    
    # Add each field to the markdown
    for _, row in df.iterrows():
        data_type = f"{row['DataType']}"
        if row['DataType'] in ['varchar', 'nvarchar', 'char', 'nchar']:
            data_type += f"({row['MaxLength'] if row['MaxLength'] != -1 else 'MAX'})"
            
        description = row['Description'] if row['Description'] else 'No description available'
        markdown_content += f"| {row['ColumnName']} | {data_type} | {description} |\n"
    
    # Add SQL query example
    markdown_content += "\n## SQL Query Example\n\n"
    markdown_content += "```sql\n"
    markdown_content += f"SELECT {', '.join(['[' + col + ']' for col in df['ColumnName']])}\n"
    markdown_content += f"FROM [{DB_NAME}].[dbo].[{table_name}]\n"
    markdown_content += "```\n"
    
    # Save to file
    try:
        with open(output_path, 'w') as f:
            f.write(markdown_content)
        print(f"Field information saved to {output_path}")
    except Exception as e:
        print(f"Error saving markdown file: {str(e)}")

if __name__ == "__main__":
    # Tables to process
    tables = ["15", "active_schd_det"]
    
    # Process each table
    for table_name in tables:
        print(f"\nProcessing table: {table_name}")
        output_path = os.path.join("Database_tables", "QADEE2798", f"dbo.{table_name}", f"{table_name}_field_names.md")
        save_field_names_markdown(table_name, output_path)
