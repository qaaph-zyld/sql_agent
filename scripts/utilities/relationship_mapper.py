"""
Database Relationship Mapper

This script analyzes database tables to identify potential relationships
based on naming conventions and field types, even when foreign key constraints
are not explicitly defined in the database.

It preserves all existing database documentation while adding relationship
information as a layered enhancement.
"""

import os
import re
import json
import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from pathlib import Path
import sqlalchemy as sa
from sqlalchemy import create_engine, text, MetaData, Table, inspect

# Database connection parameters
DB_HOST = "a265m001"
DB_NAME = "QADEE2798"
DB_USER = "PowerBI"
DB_PASSWORD = "P0werB1"

# Database documentation directory
DB_DOCS_DIR = os.path.join("Database_tables", "QADEE2798")

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

def get_table_columns(table_name):
    """
    Get column information for a specific table
    
    Args:
        table_name: Name of the table
        
    Returns:
        DataFrame containing column information
    """
    try:
        engine = get_engine()
        inspector = inspect(engine)
        columns = inspector.get_columns(table_name)
        
        # Convert to DataFrame
        df = pd.DataFrame(columns)
        return df
    
    except Exception as e:
        print(f"Error getting columns for table {table_name}: {str(e)}")
        return pd.DataFrame()

def identify_potential_relationships():
    """
    Identify potential relationships between tables based on naming conventions
    
    Returns:
        DataFrame containing potential relationships
    """
    print("Identifying potential relationships...")
    
    # Get all tables
    tables = get_all_tables(exclude_patterns=["Heureka"])
    
    # Dictionary to store table columns
    table_columns = {}
    
    # Get columns for each table
    for table in tables:
        table_columns[table] = get_table_columns(table)
    
    # List to store potential relationships
    relationships = []
    
    # Common primary key patterns
    pk_patterns = [
        r'^id$', r'^oid_', r'_id$', r'_nbr$', r'_code$',
        r'^pk_', r'_key$', r'^code$', r'^nbr$'
    ]
    
    # Identify potential relationships
    for table1 in tables:
        if table1 not in table_columns or table_columns[table1].empty:
            continue
            
        for table2 in tables:
            if table1 == table2 or table2 not in table_columns or table_columns[table2].empty:
                continue
                
            # Get columns for both tables
            cols1 = table_columns[table1]
            cols2 = table_columns[table2]
            
            # Check for potential foreign key relationships
            for _, col1 in cols1.iterrows():
                col1_name = col1['name']
                col1_type = str(col1['type'])
                
                # Skip if column is likely not a foreign key
                if any(col1_name.startswith(x) for x in ['is_', 'has_', 'can_']):
                    continue
                
                # Check if column name contains table2 name (e.g., customer_id in orders table)
                table2_singular = table2[:-1] if table2.endswith('s') else table2
                
                # Check if column name matches a primary key pattern in table2
                for _, col2 in cols2.iterrows():
                    col2_name = col2['name']
                    col2_type = str(col2['type'])
                    
                    # Skip if types don't match
                    if col1_type != col2_type:
                        continue
                    
                    # Check for naming pattern matches
                    is_potential_relationship = False
                    
                    # Case 1: Column name contains table name (e.g., customer_id)
                    if table2_singular.lower() in col1_name.lower():
                        is_potential_relationship = True
                    
                    # Case 2: Column names match and one is likely a primary key
                    elif col1_name == col2_name and any(re.search(pattern, col2_name, re.IGNORECASE) for pattern in pk_patterns):
                        is_potential_relationship = True
                    
                    # Case 3: Column names follow common foreign key pattern
                    elif col1_name.endswith('_' + col2_name) or col1_name == table2_singular + '_' + col2_name:
                        is_potential_relationship = True
                    
                    if is_potential_relationship:
                        relationships.append({
                            'table1': table1,
                            'column1': col1_name,
                            'table2': table2,
                            'column2': col2_name,
                            'confidence': 'High' if table2_singular.lower() in col1_name.lower() else 'Medium'
                        })
    
    # Convert to DataFrame
    if relationships:
        df = pd.DataFrame(relationships)
        return df
    else:
        return pd.DataFrame(columns=['table1', 'column1', 'table2', 'column2', 'confidence'])

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
    tables = set(relationships_df['table1'].tolist() + relationships_df['table2'].tolist())
    for table in tables:
        G.add_node(table)
    
    # Add edges (relationships)
    for _, row in relationships_df.iterrows():
        G.add_edge(
            row['table1'], 
            row['table2'],
            label=f"{row['column1']} -> {row['column2']}",
            confidence=row['confidence']
        )
    
    # Create figure
    plt.figure(figsize=(16, 12))
    pos = nx.spring_layout(G, k=0.5, iterations=50, seed=42)
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=2000)
    nx.draw_networkx_labels(G, pos, font_size=10, font_weight='bold')
    
    # Draw edges with different colors based on confidence
    high_confidence_edges = [(u, v) for u, v, d in G.edges(data=True) if d['confidence'] == 'High']
    medium_confidence_edges = [(u, v) for u, v, d in G.edges(data=True) if d['confidence'] == 'Medium']
    
    nx.draw_networkx_edges(G, pos, edgelist=high_confidence_edges, 
                          width=2.0, alpha=0.7, edge_color='blue',
                          arrows=True, arrowsize=15)
    nx.draw_networkx_edges(G, pos, edgelist=medium_confidence_edges, 
                          width=1.5, alpha=0.5, edge_color='gray',
                          arrows=True, arrowsize=12)
    
    # Add edge labels
    edge_labels = {(u, v): d['label'] for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
    
    # Add legend
    plt.plot([0], [0], color='blue', linewidth=2, label='High Confidence')
    plt.plot([0], [0], color='gray', linewidth=1.5, label='Medium Confidence')
    plt.legend(loc='upper right')
    
    # Save figure
    plt.title("Database Relationships (Inferred)")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Relationship diagram saved to {output_path}")

def update_database_summary(relationships_df):
    """
    Update database summary with relationship information
    
    Args:
        relationships_df: DataFrame containing relationship information
    """
    print("Updating database summary with relationship information...")
    
    # Path to database summary markdown file
    summary_path = os.path.join(DB_DOCS_DIR, "database_summary.md")
    
    # Read existing summary content
    with open(summary_path, 'r', encoding='utf-8') as f:
        summary_content = f.read()
    
    # Add inferred relationships section if it doesn't exist
    if "## Inferred Relationships" not in summary_content:
        summary_content += "\n## Inferred Relationships\n\n"
        summary_content += "These relationships are inferred based on naming conventions and column types. They may not represent actual foreign key constraints in the database.\n\n"
        summary_content += "| Table | Column | References Table | References Column | Confidence |\n"
        summary_content += "|-------|--------|------------------|-------------------|------------|\n"
        
        # Add each relationship
        for _, row in relationships_df.iterrows():
            summary_content += f"| [{row['table1']}](dbo.{row['table1']}/{row['table1']}_field_names.md) | {row['column1']} | [{row['table2']}](dbo.{row['table2']}/{row['table2']}_field_names.md) | {row['column2']} | {row['confidence']} |\n"
        
        # Add relationship diagram reference
        summary_content += "\n### Relationship Diagram (Inferred)\n\n"
        summary_content += "![Database Relationships (Inferred)](database_relationships_inferred.png)\n"
    
    # Write updated summary content back to file
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(summary_content)
    
    print(f"Updated database summary saved to {summary_path}")

def create_query_examples():
    """Create example queries that demonstrate relationships between tables"""
    print("Creating query examples...")
    
    # Path to query examples file
    examples_path = os.path.join(DB_DOCS_DIR, "query_examples.md")
    
    # Create query examples content
    examples_content = "# Query Examples for QADEE2798 Database\n\n"
    examples_content += "This document provides example queries that demonstrate how to work with the QADEE2798 database.\n\n"
    
    # Inventory and Transaction History
    examples_content += "## Inventory and Transaction History\n\n"
    examples_content += "```sql\n"
    examples_content += "-- Get inventory and recent transactions for a specific part\n"
    examples_content += "SELECT \n"
    examples_content += "    i.in_part,\n"
    examples_content += "    i.in_site,\n"
    examples_content += "    i.in_qty_oh AS 'On Hand Qty',\n"
    examples_content += "    i.in_qty_avail AS 'Available Qty',\n"
    examples_content += "    t.tr_date AS 'Transaction Date',\n"
    examples_content += "    t.tr_type AS 'Transaction Type',\n"
    examples_content += "    t.tr_qty_loc AS 'Transaction Qty'\n"
    examples_content += "FROM \n"
    examples_content += "    [QADEE2798].[dbo].[15] i\n"
    examples_content += "LEFT JOIN \n"
    examples_content += "    [QADEE2798].[dbo].[tr_hist] t ON i.in_part = t.tr_part AND i.in_site = t.tr_site\n"
    examples_content += "WHERE \n"
    examples_content += "    i.in_part = 'PART_NUMBER'\n"
    examples_content += "ORDER BY \n"
    examples_content += "    t.tr_date DESC\n"
    examples_content += "```\n\n"
    
    # Sales Orders and Details
    examples_content += "## Sales Orders and Details\n\n"
    examples_content += "```sql\n"
    examples_content += "-- Get sales orders with details and customer information\n"
    examples_content += "SELECT \n"
    examples_content += "    so.so_nbr AS 'Order Number',\n"
    examples_content += "    so.so_cust AS 'Customer',\n"
    examples_content += "    ad.ad_name AS 'Customer Name',\n"
    examples_content += "    so.so_ord_date AS 'Order Date',\n"
    examples_content += "    sod.sod_part AS 'Part Number',\n"
    examples_content += "    sod.sod_qty_ord AS 'Ordered Qty',\n"
    examples_content += "    sod.sod_price AS 'Price'\n"
    examples_content += "FROM \n"
    examples_content += "    [QADEE2798].[dbo].[so_mstr] so\n"
    examples_content += "JOIN \n"
    examples_content += "    [QADEE2798].[dbo].[sod_det] sod ON so.so_nbr = sod.sod_nbr\n"
    examples_content += "LEFT JOIN \n"
    examples_content += "    [QADEE2798].[dbo].[ad_mstr] ad ON so.so_cust = ad.ad_addr\n"
    examples_content += "ORDER BY \n"
    examples_content += "    so.so_ord_date DESC\n"
    examples_content += "```\n\n"
    
    # Purchase Orders and Vendors
    examples_content += "## Purchase Orders and Vendors\n\n"
    examples_content += "```sql\n"
    examples_content += "-- Get purchase orders with vendor information\n"
    examples_content += "SELECT \n"
    examples_content += "    po.po_nbr AS 'PO Number',\n"
    examples_content += "    po.po_vend AS 'Vendor Code',\n"
    examples_content += "    vd.vd_name AS 'Vendor Name',\n"
    examples_content += "    po.po_ord_date AS 'Order Date',\n"
    examples_content += "    pod.pod_part AS 'Part Number',\n"
    examples_content += "    pod.pod_qty_ord AS 'Ordered Qty'\n"
    examples_content += "FROM \n"
    examples_content += "    [QADEE2798].[dbo].[po_mstr] po\n"
    examples_content += "JOIN \n"
    examples_content += "    [QADEE2798].[dbo].[pod_det] pod ON po.po_nbr = pod.pod_nbr\n"
    examples_content += "LEFT JOIN \n"
    examples_content += "    [QADEE2798].[dbo].[vd_mstr] vd ON po.po_vend = vd.vd_addr\n"
    examples_content += "ORDER BY \n"
    examples_content += "    po.po_ord_date DESC\n"
    examples_content += "```\n\n"
    
    # Production Scheduling
    examples_content += "## Production Scheduling\n\n"
    examples_content += "```sql\n"
    examples_content += "-- Get active production schedules\n"
    examples_content += "SELECT \n"
    examples_content += "    s.schd_nbr AS 'Schedule Number',\n"
    examples_content += "    s.schd_line AS 'Line',\n"
    examples_content += "    s.schd_date AS 'Schedule Date',\n"
    examples_content += "    s.schd_discr_qty AS 'Discrete Qty',\n"
    examples_content += "    s.schd_cum_qty AS 'Cumulative Qty',\n"
    examples_content += "    i.in_qty_oh AS 'On Hand Qty',\n"
    examples_content += "    i.in_qty_avail AS 'Available Qty'\n"
    examples_content += "FROM \n"
    examples_content += "    [QADEE2798].[dbo].[active_schd_det] s\n"
    examples_content += "LEFT JOIN \n"
    examples_content += "    [QADEE2798].[dbo].[15] i ON s.schd_part = i.in_part\n"
    examples_content += "WHERE \n"
    examples_content += "    s.schd_date >= GETDATE()\n"
    examples_content += "ORDER BY \n"
    examples_content += "    s.schd_date\n"
    examples_content += "```\n"
    
    # Write examples to file
    with open(examples_path, 'w', encoding='utf-8') as f:
        f.write(examples_content)
    
    print(f"Query examples saved to {examples_path}")

def main():
    """Main function to identify and document database relationships"""
    # Identify potential relationships
    relationships_df = identify_potential_relationships()
    
    if relationships_df.empty:
        print("No potential relationships identified")
        return
    
    print(f"Identified {len(relationships_df)} potential relationships")
    
    # Save relationships to CSV for reference
    relationships_csv_path = os.path.join(DB_DOCS_DIR, "inferred_relationships.csv")
    relationships_df.to_csv(relationships_csv_path, index=False)
    print(f"Relationships saved to {relationships_csv_path}")
    
    # Create relationship diagram
    diagram_path = os.path.join(DB_DOCS_DIR, "database_relationships_inferred.png")
    create_relationship_diagram(relationships_df, diagram_path)
    
    # Update database summary
    update_database_summary(relationships_df)
    
    # Create query examples
    create_query_examples()
    
    print("\nDatabase relationship mapping complete!")

if __name__ == "__main__":
    main()
