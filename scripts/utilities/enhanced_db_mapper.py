"""
Enhanced Database Mapping Tool

This script provides comprehensive database mapping capabilities:
1. Maps all tables in a database (with exclusion options)
2. Extracts detailed field descriptions from database metadata
3. Identifies relationships between tables (foreign keys)
4. Generates comprehensive documentation in markdown format
5. Creates folder structure with SQL and markdown files for each table
"""

import os
import sqlalchemy as sa
from sqlalchemy import create_engine, text, MetaData, Table, inspect
import pandas as pd
import json
import re
import matplotlib.pyplot as plt
import networkx as nx
from pathlib import Path

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

def get_all_tables(exclude_patterns=None):
    """
    Get all tables in the database, with optional exclusion patterns
    
    Args:
        exclude_patterns: List of patterns to exclude (e.g., ['Heureka'])
        
    Returns:
        List of table names
    """
    try:
        engine = get_engine()
        inspector = inspect(engine)
        all_tables = inspector.get_table_names()
        
        # Apply exclusion patterns if provided
        if exclude_patterns:
            filtered_tables = []
            for table in all_tables:
                exclude = False
                for pattern in exclude_patterns:
                    if pattern.lower() in table.lower():
                        exclude = True
                        break
                if not exclude:
                    filtered_tables.append(table)
            return filtered_tables
        
        return all_tables
    
    except Exception as e:
        print(f"Error getting tables: {str(e)}")
        return []

def extract_table_fields(table_name):
    """
    Extract comprehensive field information for a specific table
    
    Args:
        table_name: Name of the table to extract field information for
        
    Returns:
        DataFrame containing field information
    """
    # SQL query to extract detailed field information
    field_query = f"""
    SELECT 
        c.name AS ColumnName,
        t.name AS DataType,
        c.max_length AS MaxLength,
        c.precision AS Precision,
        c.scale AS Scale,
        c.is_nullable AS IsNullable,
        CASE WHEN pk.column_id IS NOT NULL THEN 1 ELSE 0 END AS IsPrimaryKey,
        ISNULL(ep.value, '') AS Description,
        c.column_id AS ColumnID,
        CASE WHEN fk.parent_column_id IS NOT NULL THEN 1 ELSE 0 END AS IsForeignKey,
        OBJECT_NAME(fk.referenced_object_id) AS ReferencedTable,
        COL_NAME(fk.referenced_object_id, fk.referenced_column_id) AS ReferencedColumn
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
    LEFT JOIN 
        sys.index_columns ic ON ic.object_id = c.object_id AND ic.column_id = c.column_id
    LEFT JOIN 
        sys.indexes i ON ic.object_id = i.object_id AND ic.index_id = i.index_id AND i.is_primary_key = 1
    LEFT JOIN
        sys.index_columns pk ON pk.object_id = c.object_id AND pk.column_id = c.column_id AND pk.index_id = i.index_id
    LEFT JOIN
        sys.foreign_key_columns fk ON fk.parent_object_id = c.object_id AND fk.parent_column_id = c.column_id
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
            df = pd.DataFrame(rows, columns=[
                'ColumnName', 'DataType', 'MaxLength', 'Precision', 'Scale', 
                'IsNullable', 'IsPrimaryKey', 'Description', 'ColumnID',
                'IsForeignKey', 'ReferencedTable', 'ReferencedColumn'
            ])
            return df
        else:
            print(f"No fields found for table {table_name}")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"Error extracting field information: {str(e)}")
        return pd.DataFrame()

def get_table_relationships(table_name=None):
    """
    Get relationships (foreign keys) for a specific table or all tables
    
    Args:
        table_name: Optional name of the table to get relationships for
                   If None, get relationships for all tables
    
    Returns:
        DataFrame containing relationship information
    """
    # SQL query to extract relationship information
    relationship_query = f"""
    SELECT 
        fk.name AS ForeignKeyName,
        OBJECT_NAME(fk.parent_object_id) AS TableName,
        COL_NAME(fkc.parent_object_id, fkc.parent_column_id) AS ColumnName,
        OBJECT_NAME(fk.referenced_object_id) AS ReferencedTableName,
        COL_NAME(fkc.referenced_object_id, fkc.referenced_column_id) AS ReferencedColumnName
    FROM 
        sys.foreign_keys AS fk
    INNER JOIN 
        sys.foreign_key_columns AS fkc ON fk.object_id = fkc.constraint_object_id
    {f"WHERE OBJECT_NAME(fk.parent_object_id) = '{table_name}'" if table_name else ""}
    ORDER BY 
        TableName, ReferencedTableName
    """
    
    try:
        # Create engine and connect to database
        engine = get_engine()
        
        # Execute query and fetch results
        with engine.connect() as conn:
            result = conn.execute(text(relationship_query))
            rows = result.fetchall()
            
        # Convert results to DataFrame
        if rows:
            df = pd.DataFrame(rows, columns=[
                'ForeignKeyName', 'TableName', 'ColumnName', 
                'ReferencedTableName', 'ReferencedColumnName'
            ])
            return df
        else:
            print(f"No relationships found{f' for table {table_name}' if table_name else ''}")
            return pd.DataFrame()
            
    except Exception as e:
        print(f"Error extracting relationship information: {str(e)}")
        return pd.DataFrame()

def get_table_definition(table_name):
    """
    Get the SQL definition for a table
    
    Args:
        table_name: Name of the table
        
    Returns:
        SQL definition string
    """
    # SQL query to get table definition
    definition_query = f"""
    SELECT 
        OBJECT_DEFINITION(OBJECT_ID('{table_name}')) AS TableDefinition
    """
    
    try:
        # Create engine and connect to database
        engine = get_engine()
        
        # Execute query and fetch results
        with engine.connect() as conn:
            result = conn.execute(text(definition_query))
            row = result.fetchone()
            
        if row and row[0]:
            return row[0]
        else:
            return f"-- No definition found for table {table_name}"
            
    except Exception as e:
        print(f"Error getting table definition: {str(e)}")
        return f"-- Error getting definition: {str(e)}"

def create_table_sql_query(table_name, fields_df):
    """
    Create a SQL SELECT query for a table based on its fields
    
    Args:
        table_name: Name of the table
        fields_df: DataFrame containing field information
        
    Returns:
        SQL query string
    """
    if fields_df.empty:
        return f"-- No fields found for table {table_name}"
    
    field_list = ", ".join([f"[{col}]" for col in fields_df['ColumnName']])
    return f"SELECT {field_list}\nFROM [{DB_NAME}].[dbo].[{table_name}]"

def create_relationship_diagram(relationships_df, output_path):
    """
    Create a relationship diagram using NetworkX and save it as an image
    
    Args:
        relationships_df: DataFrame containing relationship information
        output_path: Path to save the diagram
    """
    if relationships_df.empty:
        print("No relationships to diagram")
        return
    
    # Create directed graph
    G = nx.DiGraph()
    
    # Add nodes (tables)
    tables = set(relationships_df['TableName'].tolist() + relationships_df['ReferencedTableName'].tolist())
    for table in tables:
        G.add_node(table)
    
    # Add edges (relationships)
    for _, row in relationships_df.iterrows():
        G.add_edge(
            row['TableName'], 
            row['ReferencedTableName'],
            label=f"{row['ColumnName']} -> {row['ReferencedColumnName']}"
        )
    
    # Create figure
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, k=0.5, iterations=50)
    
    # Draw nodes and edges
    nx.draw(G, pos, with_labels=True, node_color='lightblue', 
            node_size=2000, font_size=10, font_weight='bold',
            arrows=True, arrowsize=15)
    
    # Add edge labels
    edge_labels = {(u, v): d['label'] for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
    
    # Save figure
    plt.title("Database Relationships")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Relationship diagram saved to {output_path}")

def save_field_names_markdown(table_name, fields_df, relationships_df, output_path):
    """Ensure we're using UTF-8 encoding for all file operations"""
    """
    Save comprehensive field information to a markdown file
    
    Args:
        table_name: Name of the table
        fields_df: DataFrame containing field information
        relationships_df: DataFrame containing relationship information
        output_path: Path to save the markdown file
    """
    if fields_df.empty:
        print(f"No field information available for table {table_name}")
        return
    
    # Create markdown content
    markdown_content = f"# Table: {table_name}\n\n"
    
    # Add table description if available
    # TODO: Add table description from documentation
    
    # Add field information
    markdown_content += "## Fields\n\n"
    markdown_content += "| Field Name | Data Type | Primary Key | Foreign Key | Nullable | Description |\n"
    markdown_content += "|------------|-----------|-------------|-------------|----------|-------------|\n"
    
    # Add each field to the markdown
    for _, row in fields_df.iterrows():
        # Format data type with length/precision/scale if applicable
        data_type = f"{row['DataType']}"
        if row['DataType'] in ['varchar', 'nvarchar', 'char', 'nchar']:
            data_type += f"({row['MaxLength'] if row['MaxLength'] != -1 else 'MAX'})"
        elif row['DataType'] in ['decimal', 'numeric']:
            data_type += f"({row['Precision']},{row['Scale']})"
            
        # Format primary key indicator
        pk = "Yes" if row['IsPrimaryKey'] == 1 else ""
        
        # Format foreign key indicator
        fk = "Yes" if row['IsForeignKey'] == 1 else ""
        
        # Format nullable indicator
        nullable = "YES" if row['IsNullable'] == 1 else "NO"
        
        # Format description
        description = row['Description'] if row['Description'] else 'No description available'
        
        # Add foreign key reference if applicable
        if row['IsForeignKey'] == 1 and not pd.isna(row['ReferencedTable']):
            description += f" (References {row['ReferencedTable']}.{row['ReferencedColumn']})"
        
        markdown_content += f"| {row['ColumnName']} | {data_type} | {pk} | {fk} | {nullable} | {description} |\n"
    
    # Add relationships section
    if not relationships_df.empty:
        filtered_relationships = relationships_df[relationships_df['TableName'] == table_name]
        if not filtered_relationships.empty:
            markdown_content += "\n## Foreign Key Relationships\n\n"
            markdown_content += "| Foreign Key | Column | References Table | References Column |\n"
            markdown_content += "|-------------|--------|------------------|-------------------|\n"
            
            for _, row in filtered_relationships.iterrows():
                markdown_content += f"| {row['ForeignKeyName']} | {row['ColumnName']} | {row['ReferencedTableName']} | {row['ReferencedColumnName']} |\n"
    
    # Add SQL query example
    markdown_content += "\n## SQL Query Example\n\n"
    markdown_content += "```sql\n"
    markdown_content += create_table_sql_query(table_name, fields_df)
    markdown_content += "\n```\n"
    
    # Save to file
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        print(f"Field information saved to {output_path}")
    except Exception as e:
        print(f"Error saving markdown file: {str(e)}")
        # Try with a different encoding if UTF-8 fails
        try:
            with open(output_path, 'w', encoding='cp1252') as f:
                f.write(markdown_content)
            print(f"Field information saved to {output_path} using cp1252 encoding")
        except Exception as e2:
            print(f"Error saving markdown file with alternative encoding: {str(e2)}")

def save_table_sql(table_name, fields_df, output_path):
    """
    Save a SQL SELECT query for a table to a file
    
    Args:
        table_name: Name of the table
        fields_df: DataFrame containing field information
        output_path: Path to save the SQL file
    """
    sql_content = create_table_sql_query(table_name, fields_df)
    
    try:
        with open(output_path, 'w') as f:
            f.write(sql_content)
        print(f"SQL query saved to {output_path}")
    except Exception as e:
        print(f"Error saving SQL file: {str(e)}")

def process_table(table_name, base_dir, relationships_df):
    """
    Process a single table and generate all documentation
    
    Args:
        table_name: Name of the table
        base_dir: Base directory for output
        relationships_df: DataFrame containing relationship information
    """
    print(f"\nProcessing table: {table_name}")
    
    # Create directory structure
    table_dir = os.path.join(base_dir, f"dbo.{table_name}")
    os.makedirs(table_dir, exist_ok=True)
    
    # Extract field information
    fields_df = extract_table_fields(table_name)
    
    if fields_df.empty:
        print(f"No fields found for table {table_name}, skipping")
        return
    
    # Save field information to markdown
    md_path = os.path.join(table_dir, f"{table_name}_field_names.md")
    save_field_names_markdown(table_name, fields_df, relationships_df, md_path)
    
    # Save SQL query
    sql_path = os.path.join(table_dir, f"{table_name}.sql")
    save_table_sql(table_name, fields_df, sql_path)
    
    # Create relationship diagram if relationships exist
    if not relationships_df.empty and 'TableName' in relationships_df.columns:
        filtered_relationships = relationships_df[
            (relationships_df['TableName'] == table_name) | 
            (relationships_df['ReferencedTableName'] == table_name)
        ]
    else:
        filtered_relationships = pd.DataFrame()
    
    if not filtered_relationships.empty:
        diagram_path = os.path.join(table_dir, f"{table_name}_relationships.png")
        create_relationship_diagram(filtered_relationships, diagram_path)

def create_database_summary(tables, base_dir, relationships_df):
    """
    Create a summary markdown file for the entire database
    
    Args:
        tables: List of table names
        base_dir: Base directory for output
        relationships_df: DataFrame containing relationship information
    """
    summary_path = os.path.join(base_dir, "database_summary.md")
    
    # Create summary content
    summary_content = f"# Database Summary: {DB_NAME}\n\n"
    summary_content += f"## Tables ({len(tables)})\n\n"
    
    # Add table list with links
    for table in sorted(tables):
        summary_content += f"- [{table}](dbo.{table}/{table}_field_names.md)\n"
    
    # Add relationship summary
    if not relationships_df.empty:
        summary_content += "\n## Relationships\n\n"
        summary_content += "| Table | Column | References Table | References Column |\n"
        summary_content += "|-------|--------|------------------|-------------------|\n"
        
        for _, row in relationships_df.iterrows():
            summary_content += f"| [{row['TableName']}](dbo.{row['TableName']}/{row['TableName']}_field_names.md) | {row['ColumnName']} | [{row['ReferencedTableName']}](dbo.{row['ReferencedTableName']}/{row['ReferencedTableName']}_field_names.md) | {row['ReferencedColumnName']} |\n"
    
    # Create overall relationship diagram
    if not relationships_df.empty:
        diagram_path = os.path.join(base_dir, "database_relationships.png")
        create_relationship_diagram(relationships_df, diagram_path)
        summary_content += "\n## Relationship Diagram\n\n"
        summary_content += "![Database Relationships](database_relationships.png)\n"
    
    # Save summary to file
    try:
        with open(summary_path, 'w') as f:
            f.write(summary_content)
        print(f"Database summary saved to {summary_path}")
    except Exception as e:
        print(f"Error saving summary file: {str(e)}")

def main():
    """Main function to process all tables"""
    # Base directory for output
    base_dir = os.path.join("Database_tables", DB_NAME)
    os.makedirs(base_dir, exist_ok=True)
    
    # Get all tables excluding those with "Heureka" in the name
    tables = get_all_tables(exclude_patterns=["Heureka"])
    print(f"Found {len(tables)} tables (excluding Heureka tables)")
    
    try:
        # Get all relationships
        relationships_df = get_table_relationships()
        relationship_count = len(relationships_df) if not relationships_df.empty else 0
        print(f"Found {relationship_count} relationships")
    except Exception as e:
        print(f"Error getting relationships: {str(e)}")
        relationships_df = pd.DataFrame()
    
    # Process each table
    for table in tables:
        try:
            process_table(table, base_dir, relationships_df)
        except Exception as e:
            print(f"Error processing table {table}: {str(e)}")
    
    # Create database summary
    try:
        create_database_summary(tables, base_dir, relationships_df)
    except Exception as e:
        print(f"Error creating database summary: {str(e)}")
    
    print("\nDatabase mapping complete!")

if __name__ == "__main__":
    main()
