#!/usr/bin/env python3
"""
Check Schema - Simple utility to check table schema
"""

import sys
from scripts.db.db_connector import DatabaseConnector

def main():
    """Check database schema"""
    print("\n=== Database Schema Check ===\n")
    
    # Initialize database connector
    db = DatabaseConnector()
    
    # Test connection
    if not db.test_connection():
        print("Database connection failed")
        return False
    
    print("Database connection successful\n")
    
    # Check tr_hist table schema
    print("Checking tr_hist table schema...")
    tr_hist_query = """
    SELECT TOP 0 * 
    FROM tr_hist
    """
    
    try:
        result = db.execute_query(tr_hist_query)
        if result is not None:
            columns = list(result[0].keys()) if result else []
            print(f"tr_hist columns: {columns}")
        else:
            print("No schema information returned for tr_hist")
    except Exception as e:
        print(f"Error checking tr_hist schema: {e}")
    
    # Check pt_mstr table schema
    print("\nChecking pt_mstr table schema...")
    pt_mstr_query = """
    SELECT TOP 0 * 
    FROM pt_mstr
    """
    
    try:
        result = db.execute_query(pt_mstr_query)
        if result is not None:
            columns = list(result[0].keys()) if result else []
            print(f"pt_mstr columns: {columns}")
        else:
            print("No schema information returned for pt_mstr")
    except Exception as e:
        print(f"Error checking pt_mstr schema: {e}")
    
    # Check if tr_hist has RCT-WO records
    print("\nChecking for RCT-WO transactions...")
    rct_wo_query = """
    SELECT TOP 5 * 
    FROM tr_hist 
    WHERE tr_type = 'RCT-WO'
    """
    
    try:
        result = db.execute_query(rct_wo_query)
        if result:
            print(f"Found {len(result)} RCT-WO transactions")
            print("Sample transaction fields:")
            for key, value in result[0].items():
                print(f"  {key}: {value}")
        else:
            print("No RCT-WO transactions found")
    except Exception as e:
        print(f"Error checking RCT-WO transactions: {e}")
    
    return True

if __name__ == "__main__":
    main()
