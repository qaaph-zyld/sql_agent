#!/usr/bin/env python3
"""
Direct SQL Query - Execute SQL queries directly against the database
"""

import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent))
from scripts.db.db_connector import DatabaseConnector

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Direct SQL Query Tool")
    parser.add_argument("--sql", type=str, required=True, help="SQL query to execute")
    parser.add_argument("--output", type=str, help="Output file for results (JSON format)")
    parser.add_argument("--limit", type=int, default=10, help="Maximum number of columns to display")
    return parser.parse_args()

def main():
    """Main entry point for direct SQL query tool"""
    # Parse arguments
    args = parse_arguments()
    
    # Create a log file for output
    log_file_path = Path(__file__).parent / "direct_sql_results.txt"
    
    # Write to both console and file
    def log(message):
        print(message)
        with open(log_file_path, "a") as log_file:
            log_file.write(f"{message}\n")
    
    # Initialize log file
    with open(log_file_path, "w") as log_file:
        log_file.write(f"Direct SQL Query Execution - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_file.write(f"SQL Query: {args.sql}\n\n")
    
    log("\n[INFO] Initializing database connector...")
    db = DatabaseConnector()
    
    log("\n[INFO] Testing database connection...")
    connection_success = db.test_connection()
    
    if connection_success:
        log("\n[SUCCESS] Database connection successful!")
        
        # Execute SQL query
        log(f"\n[INFO] Executing SQL query: {args.sql}")
        try:
            results = db.execute_query(args.sql)
            
            if results:
                log(f"\n[SUCCESS] Query executed successfully! Retrieved {len(results)} records.\n")
                
                # Get column names from first result
                columns = list(results[0].keys())
                log(f"Columns in result: {', '.join(columns)}")
                
                # Calculate column widths based on data
                col_widths = {}
                for col in columns:
                    # Start with column name length
                    col_widths[col] = len(str(col))
                    # Check data lengths
                    for result in results:
                        val_len = len(str(result.get(col, '')))
                        col_widths[col] = max(col_widths[col], val_len)
                
                # Print header (limit columns for readability)
                display_columns = columns[:args.limit] if len(columns) > args.limit else columns
                header = "  ".join(f"{col:{col_widths[col]}}" for col in display_columns)
                separator = "-" * len(header)
                log(header)
                log(separator)
                
                # Print rows
                for result in results:
                    row = "  ".join(f"{str(result.get(col, '')):{col_widths[col]}}" for col in display_columns)
                    log(row)
                
                if len(columns) > args.limit:
                    log(f"\n[NOTE] Only showing first {args.limit} of {len(columns)} columns for readability.")
                    
                # Write complete results to a JSON file
                if args.output:
                    output_path = Path(args.output)
                else:
                    output_path = Path(__file__).parent / "direct_sql_results.json"
                    
                with open(output_path, "w") as results_file:
                    json.dump(results, results_file, indent=2, default=str)
                log(f"\n[INFO] Complete results saved to {output_path}")
            else:
                log("\n[INFO] Query executed but no results were returned.")
        except Exception as e:
            log(f"\n[ERROR] Error executing SQL query: {e}")
            import traceback
            log(traceback.format_exc())
    else:
        log("\n[ERROR] Database connection failed")
    
    log(f"\n[INFO] Query execution completed. Results saved to {log_file_path}")

if __name__ == "__main__":
    main()
