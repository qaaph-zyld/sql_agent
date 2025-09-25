#!/usr/bin/env python3
"""
Schema Explorer - Utility to explore and document database schema
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent))
from scripts.db.db_connector import DatabaseConnector
from scripts.db.schema_extractor import SchemaExtractor
from scripts.core.changelog_engine import ChangelogEngine

# Configure logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path(__file__).parent / "logs" / "schema_explorer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("schema_explorer")

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Database Schema Explorer")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # List tables command
    list_parser = subparsers.add_parser("list", help="List all tables in the database")
    list_parser.add_argument("--output", type=str, help="Output file for results (JSON format)")
    
    # Describe table command
    describe_parser = subparsers.add_parser("describe", help="Describe a specific table")
    describe_parser.add_argument("--table", type=str, required=True, help="Table name to describe")
    describe_parser.add_argument("--output", type=str, help="Output file for results (JSON format)")
    
    # Extract full schema command
    extract_parser = subparsers.add_parser("extract", help="Extract full database schema")
    extract_parser.add_argument("--output", type=str, help="Output directory for schema files")
    
    return parser.parse_args()

def format_table(headers: List[str], rows: List[List[Any]]) -> str:
    """Format data as a text table
    
    Args:
        headers: List of column headers
        rows: List of rows, each row is a list of values
        
    Returns:
        Formatted table as string
    """
    # Calculate column widths
    col_widths = [len(str(header)) for header in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Format header
    header_row = " | ".join(f"{header:{col_widths[i]}}" for i, header in enumerate(headers))
    separator = "-" * len(header_row)
    
    # Format rows
    formatted_rows = []
    for row in rows:
        formatted_row = " | ".join(f"{str(cell):{col_widths[i]}}" for i, cell in enumerate(row))
        formatted_rows.append(formatted_row)
    
    # Combine all parts
    return f"{header_row}\n{separator}\n" + "\n".join(formatted_rows)

def list_tables(db_connector: DatabaseConnector, schema_extractor: SchemaExtractor, output_file: Optional[str] = None) -> None:
    """List all tables in the database
    
    Args:
        db_connector: Database connector instance
        schema_extractor: Schema extractor instance
        output_file: Optional output file path for JSON results
    """
    print("\n[INFO] Retrieving table list from database...")
    
    try:
        # Get table names
        tables = db_connector.get_table_names()
        
        if not tables:
            print("\n[WARNING] No tables found in the database.")
            return
        
        print(f"\n[SUCCESS] Found {len(tables)} tables in the database.")
        
        # Get row counts for each table
        table_info = []
        for table in tables:
            try:
                count_query = f"SELECT COUNT(*) AS row_count FROM {table}"
                result = db_connector.execute_query(count_query)
                row_count = result[0]['row_count'] if result else 0
            except Exception as e:
                logger.warning(f"Error getting row count for table {table}: {e}")
                row_count = "Error"
            
            table_info.append({
                "table_name": table,
                "row_count": row_count
            })
        
        # Display table list
        headers = ["Table Name", "Row Count"]
        rows = [[info["table_name"], info["row_count"]] for info in table_info]
        
        print("\nDatabase Tables:")
        print(format_table(headers, rows))
        
        # Save to JSON file if requested
        if output_file:
            output_path = Path(output_file)
            with open(output_path, "w") as f:
                json.dump(table_info, f, indent=2)
            print(f"\n[INFO] Table list saved to {output_path}")
    
    except Exception as e:
        print(f"\n[ERROR] Error listing tables: {e}")
        import traceback
        print(traceback.format_exc())

def describe_table(schema_extractor: SchemaExtractor, table_name: str, output_file: Optional[str] = None) -> None:
    """Describe a specific table
    
    Args:
        schema_extractor: Schema extractor instance
        table_name: Name of the table to describe
        output_file: Optional output file path for JSON results
    """
    print(f"\n[INFO] Retrieving schema for table: {table_name}")
    
    try:
        # Get table schema
        schema = schema_extractor.extract_table_schema(table_name)
        
        if not schema:
            print(f"\n[WARNING] Table '{table_name}' not found or has no columns.")
            return
        
        print(f"\n[SUCCESS] Retrieved schema for table '{table_name}'")
        print(f"Number of columns: {len(schema)}")
        
        # Format column information
        headers = ["Column Name", "Data Type", "Nullable", "Primary Key", "Foreign Key"]
        rows = []
        
        for column in schema:
            rows.append([
                column.get("column_name", ""),
                column.get("data_type", ""),
                "YES" if column.get("is_nullable") else "NO",
                "YES" if column.get("is_primary_key") else "NO",
                column.get("foreign_key_reference", "")
            ])
        
        print("\nTable Schema:")
        print(format_table(headers, rows))
        
        # Save to JSON file if requested
        if output_file:
            output_path = Path(output_file)
            with open(output_path, "w") as f:
                json.dump(schema, f, indent=2)
            print(f"\n[INFO] Table schema saved to {output_path}")
    
    except Exception as e:
        print(f"\n[ERROR] Error describing table: {e}")
        import traceback
        print(traceback.format_exc())

def extract_full_schema(schema_extractor: SchemaExtractor, output_dir: Optional[str] = None) -> None:
    """Extract full database schema
    
    Args:
        schema_extractor: Schema extractor instance
        output_dir: Optional output directory path for schema files
    """
    print("\n[INFO] Extracting full database schema...")
    
    try:
        # Extract full schema
        full_schema = schema_extractor.extract_full_schema()
        
        if not full_schema:
            print("\n[WARNING] No schema information found.")
            return
        
        # Prepare output directory
        if output_dir:
            output_path = Path(output_dir)
        else:
            output_path = Path(__file__).parent / "schema"
        
        output_path.mkdir(exist_ok=True)
        
        # Save schema files
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        schema_file = output_path / f"full_schema_{timestamp}.json"
        
        with open(schema_file, "w") as f:
            json.dump(full_schema, f, indent=2)
        
        # Create individual table schema files
        tables_dir = output_path / "tables"
        tables_dir.mkdir(exist_ok=True)
        
        for table_name, table_schema in full_schema.items():
            table_file = tables_dir / f"{table_name}.json"
            with open(table_file, "w") as f:
                json.dump(table_schema, f, indent=2)
        
        print(f"\n[SUCCESS] Full schema extracted and saved to {output_path}")
        print(f"Number of tables: {len(full_schema)}")
        print(f"Full schema file: {schema_file}")
        print(f"Individual table schemas: {tables_dir}")
    
    except Exception as e:
        print(f"\n[ERROR] Error extracting full schema: {e}")
        import traceback
        print(traceback.format_exc())

def main():
    """Main entry point for schema explorer"""
    # Parse arguments
    args = parse_arguments()
    
    # Create log directory if it doesn't exist
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Initialize components
    db_connector = DatabaseConnector()
    schema_extractor = SchemaExtractor()
    changelog_engine = ChangelogEngine()
    
    # Test database connection
    print("\n[INFO] Testing database connection...")
    if not db_connector.test_connection():
        print("\n[ERROR] Database connection failed. Please check your configuration.")
        return
    
    print("\n[SUCCESS] Database connection successful!")
    
    # Execute requested command
    if args.command == "list":
        list_tables(db_connector, schema_extractor, args.output)
        
        # Update changelog
        changelog_engine.quick_update(
            "Listed database tables",
            ["Database schema exploration"],
            ["schema_explorer.py"]
        )
    
    elif args.command == "describe":
        describe_table(schema_extractor, args.table, args.output)
        
        # Update changelog
        changelog_engine.quick_update(
            f"Described table schema for {args.table}",
            ["Database schema exploration", args.table],
            ["schema_explorer.py"]
        )
    
    elif args.command == "extract":
        extract_full_schema(schema_extractor, args.output)
        
        # Update changelog
        changelog_engine.quick_update(
            "Extracted full database schema",
            ["Database schema exploration"],
            ["schema_explorer.py"]
        )
    
    else:
        print("\n[ERROR] No command specified. Use --help for usage information.")

if __name__ == "__main__":
    main()
