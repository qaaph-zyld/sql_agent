#!/usr/bin/env python3
"""
Check Table Schema - Utility to check the schema of a specific table
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent))
from scripts.db.db_connector import DatabaseConnector
from scripts.db.schema_extractor import SchemaExtractor

def main():
    """Main entry point for schema check utility"""
    if len(sys.argv) < 2:
        print("Usage: python check_table_schema.py <table_name>")
        sys.exit(1)
        
    table_name = sys.argv[1]
    
    print(f"\n[INFO] Checking schema for table: {table_name}")
    
    # Initialize components
    db = DatabaseConnector()
    schema_extractor = SchemaExtractor()
    
    # Test connection
    if db.test_connection():
        print("[SUCCESS] Database connection successful!")
        
        try:
            # Get table schema
            schema = schema_extractor.extract_table_schema(table_name)
            
            if schema:
                print(f"\n[SUCCESS] Retrieved schema for {table_name}")
                print(f"Number of columns: {len(schema)}")
                
                # Print column details
                print("\nColumn Name                 Data Type                 Nullable")
                print("-" * 70)
                
                for column in schema:
                    col_name = column.get("column_name", "")
                    data_type = column.get("data_type", "")
                    nullable = "YES" if column.get("is_nullable") else "NO"
                    
                    print(f"{col_name:<25} {data_type:<25} {nullable:<10}")
                
                # Save schema to file
                output_file = Path(__file__).parent / f"{table_name}_schema.json"
                with open(output_file, "w") as f:
                    json.dump(schema, f, indent=2)
                    
                print(f"\n[INFO] Schema saved to {output_file}")
            else:
                print(f"\n[ERROR] Could not retrieve schema for {table_name}")
        except Exception as e:
            print(f"\n[ERROR] Error retrieving schema: {e}")
    else:
        print("\n[ERROR] Database connection failed")

if __name__ == "__main__":
    main()
