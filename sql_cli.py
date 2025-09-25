#!/usr/bin/env python3
"""
SQL CLI - Command Line Interface for SQL Agent
A robust tool for interacting with the SQL database with guaranteed output visibility
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
import time

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent))
from scripts.db.db_connector import DatabaseConnector
from scripts.core.changelog_engine import ChangelogEngine

# Configure logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(Path(__file__).parent / "logs" / "sql_cli.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("sql_cli")

class SqlCli:
    """SQL Command Line Interface"""
    
    def __init__(self):
        """Initialize SQL CLI"""
        self.db_connector = DatabaseConnector()
        self.changelog_engine = ChangelogEngine()
        self.output_file = Path(__file__).parent / f"sql_cli_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        
        # Ensure output is visible
        with open(self.output_file, "w") as f:
            f.write(f"SQL CLI Session - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Print with guaranteed output
        self.print("SQL CLI initialized")
        self.print(f"Output will be saved to: {self.output_file}")
    
    def print(self, message):
        """Print message with guaranteed output visibility
        
        Args:
            message: Message to print
        """
        print(message)
        sys.stdout.flush()  # Force flush to ensure visibility
        
        # Also log to file
        with open(self.output_file, "a") as f:
            f.write(f"{message}\n")
    
    def test_connection(self):
        """Test database connection"""
        self.print("\n=== Testing Database Connection ===")
        
        try:
            start_time = time.time()
            success = self.db_connector.test_connection()
            elapsed_time = time.time() - start_time
            
            if success:
                self.print(f"✅ Connection successful! ({elapsed_time:.2f}s)")
                
                # Get database info
                try:
                    info_query = "SELECT @@version AS version, DB_NAME() AS database_name"
                    result = self.db_connector.execute_query(info_query)
                    if result:
                        self.print(f"\nServer: {result[0].get('version', 'Unknown')}")
                        self.print(f"Database: {result[0].get('database_name', 'Unknown')}")
                except Exception as e:
                    self.print(f"Could not retrieve database info: {e}")
                
                return True
            else:
                self.print("❌ Connection failed!")
                return False
        except Exception as e:
            self.print(f"❌ Connection error: {e}")
            return False
    
    def list_tables(self):
        """List all tables in the database"""
        self.print("\n=== Database Tables ===")
        
        try:
            # Get table names
            start_time = time.time()
            tables = self.db_connector.get_table_names()
            elapsed_time = time.time() - start_time
            
            if not tables:
                self.print("No tables found in the database.")
                return
            
            self.print(f"Found {len(tables)} tables ({elapsed_time:.2f}s)")
            
            # Format as table
            self.print("\nTable Name")
            self.print("-" * 40)
            
            for table in sorted(tables):
                self.print(table)
            
            # Update changelog
            self.changelog_engine.quick_update(
                "Listed database tables",
                ["Database exploration"],
                ["sql_cli.py"]
            )
        except Exception as e:
            self.print(f"Error listing tables: {e}")
            import traceback
            self.print(traceback.format_exc())
    
    def execute_query(self, query, limit_columns=None):
        """Execute SQL query
        
        Args:
            query: SQL query to execute
            limit_columns: Maximum number of columns to display
        """
        self.print("\n=== Executing SQL Query ===")
        self.print(f"Query: {query}")
        
        try:
            # Execute query
            start_time = time.time()
            results = self.db_connector.execute_query(query)
            elapsed_time = time.time() - start_time
            
            # Display results
            if not results:
                self.print(f"\nQuery executed successfully, but no results returned. ({elapsed_time:.2f}s)")
                return
            
            self.print(f"\nQuery executed successfully! ({elapsed_time:.2f}s)")
            self.print(f"Retrieved {len(results)} records")
            
            # Get column names from first result
            columns = list(results[0].keys())
            
            # Limit columns for display if requested
            display_columns = columns
            if limit_columns and len(columns) > limit_columns:
                display_columns = columns[:limit_columns]
                self.print(f"\nNote: Only showing first {limit_columns} of {len(columns)} columns")
            
            # Calculate column widths
            col_widths = {}
            for col in display_columns:
                # Start with column name length
                col_widths[col] = len(str(col))
                # Check data lengths
                for result in results:
                    val_len = len(str(result.get(col, '')))
                    col_widths[col] = max(col_widths[col], min(val_len, 30))  # Cap at 30 chars
            
            # Print header
            header = "  ".join(f"{col:{col_widths[col]}}" for col in display_columns)
            separator = "-" * len(header)
            self.print(f"\n{header}")
            self.print(separator)
            
            # Print rows
            for i, result in enumerate(results):
                row = "  ".join(f"{str(result.get(col, ''))[:30]:{col_widths[col]}}" for col in display_columns)
                self.print(row)
                
                # Add separator every 20 rows for readability
                if i > 0 and i % 20 == 0 and i < len(results) - 1:
                    self.print(separator)
            
            # Save to JSON file
            json_file = Path(__file__).parent / f"query_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(json_file, "w") as f:
                json.dump(results, f, indent=2, default=str)
            self.print(f"\nComplete results saved to {json_file}")
            
            # Update changelog
            self.changelog_engine.quick_update(
                "Executed SQL query",
                ["Database query", query[:100] + "..." if len(query) > 100 else query],
                ["sql_cli.py"]
            )
        except Exception as e:
            self.print(f"Error executing query: {e}")
            import traceback
            self.print(traceback.format_exc())
    
    def describe_table(self, table_name):
        """Describe table structure
        
        Args:
            table_name: Name of the table to describe
        """
        self.print(f"\n=== Table Structure: {table_name} ===")
        
        try:
            # Get column information using SQL Server system tables
            query = f"""
            SELECT 
                c.name AS column_name,
                t.name AS data_type,
                c.max_length,
                c.precision,
                c.scale,
                c.is_nullable,
                CASE WHEN pk.column_id IS NOT NULL THEN 1 ELSE 0 END AS is_primary_key
            FROM 
                sys.columns c
            INNER JOIN 
                sys.types t ON c.user_type_id = t.user_type_id
            INNER JOIN 
                sys.tables tbl ON c.object_id = tbl.object_id
            LEFT JOIN 
                (SELECT ic.column_id, ic.object_id
                 FROM sys.index_columns ic
                 INNER JOIN sys.indexes i ON ic.object_id = i.object_id AND ic.index_id = i.index_id
                 WHERE i.is_primary_key = 1) pk 
                ON c.object_id = pk.object_id AND c.column_id = pk.column_id
            WHERE 
                tbl.name = '{table_name}'
            ORDER BY 
                c.column_id
            """
            
            # Execute query
            start_time = time.time()
            columns = self.db_connector.execute_query(query)
            elapsed_time = time.time() - start_time
            
            if not columns:
                self.print(f"Table '{table_name}' not found or has no columns.")
                return
            
            self.print(f"Found {len(columns)} columns ({elapsed_time:.2f}s)")
            
            # Format as table
            self.print("\nColumn Name                 Data Type      Length/Precision  Nullable  PK")
            self.print("-" * 80)
            
            for col in columns:
                col_name = col.get("column_name", "")
                data_type = col.get("data_type", "")
                
                # Format length/precision based on data type
                if data_type in ("nvarchar", "varchar", "char", "nchar"):
                    type_details = str(col.get("max_length", ""))
                elif data_type in ("decimal", "numeric"):
                    type_details = f"{col.get('precision', '')},{col.get('scale', '')}"
                else:
                    type_details = ""
                
                nullable = "YES" if col.get("is_nullable") else "NO"
                pk = "YES" if col.get("is_primary_key") else "NO"
                
                self.print(f"{col_name:<25} {data_type:<14} {type_details:<17} {nullable:<9} {pk}")
            
            # Get sample data
            try:
                sample_query = f"SELECT TOP 5 * FROM {table_name}"
                self.print(f"\n=== Sample Data: {table_name} (First 5 rows) ===")
                self.execute_query(sample_query, limit_columns=8)
            except Exception as e:
                self.print(f"Could not retrieve sample data: {e}")
            
            # Update changelog
            self.changelog_engine.quick_update(
                f"Described table structure for {table_name}",
                ["Database exploration", table_name],
                ["sql_cli.py"]
            )
        except Exception as e:
            self.print(f"Error describing table: {e}")
            import traceback
            self.print(traceback.format_exc())

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="SQL Command Line Interface")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Test connection command
    subparsers.add_parser("test", help="Test database connection")
    
    # List tables command
    subparsers.add_parser("list", help="List all tables in the database")
    
    # Execute query command
    query_parser = subparsers.add_parser("query", help="Execute SQL query")
    query_parser.add_argument("--sql", type=str, required=True, help="SQL query to execute")
    query_parser.add_argument("--limit-columns", type=int, default=10, help="Maximum number of columns to display")
    
    # Describe table command
    describe_parser = subparsers.add_parser("describe", help="Describe table structure")
    describe_parser.add_argument("--table", type=str, required=True, help="Table name to describe")
    
    return parser.parse_args()

def main():
    """Main entry point for SQL CLI"""
    # Parse arguments
    args = parse_arguments()
    
    # Create log directory if it doesn't exist
    log_dir = Path(__file__).parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # Initialize SQL CLI
    cli = SqlCli()
    
    # Execute requested command
    if args.command == "test":
        cli.test_connection()
    elif args.command == "list":
        if cli.test_connection():
            cli.list_tables()
    elif args.command == "query":
        if cli.test_connection():
            cli.execute_query(args.sql, args.limit_columns)
    elif args.command == "describe":
        if cli.test_connection():
            cli.describe_table(args.table)
    else:
        cli.print("No command specified. Use --help for usage information.")

if __name__ == "__main__":
    main()
