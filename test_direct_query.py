#!/usr/bin/env python3
"""
Direct SQL Query Test - Tests direct SQL query execution against the database
"""

import os
import sys
from pathlib import Path
import json
from datetime import datetime

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent))
from scripts.db.db_connector import DatabaseConnector

def main():
    """Main entry point for direct query test"""
    # Create a log file for output
    log_file_path = Path(__file__).parent / "direct_query_test_results.txt"
    
    # Write to both console and file
    def log(message):
        print(message)
        with open(log_file_path, "a") as log_file:
            log_file.write(f"{message}\n")
    
    # Initialize log file
    with open(log_file_path, "w") as log_file:
        log_file.write(f"Direct SQL Query Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    log("\n[INFO] Initializing database connector...")
    db = DatabaseConnector()
    
    log("\n[INFO] Testing database connection...")
    connection_success = db.test_connection()
    
    if connection_success:
        log("\n[SUCCESS] Database connection successful!")
        
        log("\n[INFO] Retrieving table names...")
        try:
            tables = db.get_table_names()
            log(f"\n[SUCCESS] Found {len(tables)} tables in the database.")
            
            # List all tables
            log("\nAvailable tables:")
            for i, table in enumerate(tables, 1):
                log(f"{i}. {table}")
            
            # Execute a simple query to get the first 5 records from po_mstr
            log("\n[INFO] Executing direct SQL query against po_mstr table...")
            query = "SELECT TOP 5 * FROM po_mstr"
            log(f"\nExecuting SQL: {query}")
            
            results = db.execute_query(query)
            
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
                
                # Print header (limit to first 10 columns for readability)
                display_columns = columns[:10] if len(columns) > 10 else columns
                header = "  ".join(f"{col:{col_widths[col]}}" for col in display_columns)
                separator = "-" * len(header)
                log(header)
                log(separator)
                
                # Print rows
                for result in results:
                    row = "  ".join(f"{str(result.get(col, '')):{col_widths[col]}}" for col in display_columns)
                    log(row)
                
                if len(columns) > 10:
                    log(f"\n[NOTE] Only showing first 10 of {len(columns)} columns for readability.")
                    
                # Write complete results to a JSON file for reference
                results_file_path = Path(__file__).parent / "query_results.json"
                with open(results_file_path, "w") as results_file:
                    json.dump(results, results_file, indent=2, default=str)
                log(f"\n[INFO] Complete results saved to {results_file_path}")
            else:
                log("\n[INFO] No results found for the query.")
        except Exception as e:
            log(f"\n[ERROR] Error during database operations: {e}")
            import traceback
            log(traceback.format_exc())
    else:
        log("\n[ERROR] Database connection failed")
    
    log(f"\n[INFO] Test completed. Results saved to {log_file_path}")

if __name__ == "__main__":
    main()
