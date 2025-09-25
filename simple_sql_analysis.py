#!/usr/bin/env python3
"""
Simple SQL Analysis Tool - No Unicode characters
For analyzing RCT-WO transactions joined with pt_mstr
"""

import os
import sys
import json
import pandas as pd
from pathlib import Path
from datetime import datetime
import time
from scripts.db.db_connector import DatabaseConnector

# Configure output
output_dir = Path(__file__).parent / "analysis" / "rct_wo_analysis" / "results"
output_dir.mkdir(exist_ok=True, parents=True)
output_file = output_dir / f"rct_wo_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

def log_message(message):
    """Log message to console and file"""
    print(message)
    sys.stdout.flush()
    with open(output_file, "a", encoding="utf-8") as f:
        f.write(f"{message}\n")

def run_analysis():
    """Run RCT-WO analysis"""
    log_message("=" * 60)
    log_message(f"RCT-WO Analysis - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log_message("=" * 60)
    
    # Initialize database connector
    log_message("\nConnecting to database...")
    db = DatabaseConnector()
    
    # Test connection
    if not db.test_connection():
        log_message("[ERROR] Database connection failed")
        return False
    
    log_message("[SUCCESS] Database connection successful")
    
    # Define queries
    queries = {
        "summary": """
            SELECT 
                COUNT(*) AS total_transactions,
                SUM(th.tr_qty) AS total_quantity,
                SUM(th.tr_amt) AS total_amount,
                AVG(th.tr_qty) AS avg_quantity,
                AVG(th.tr_amt) AS avg_amount
            FROM 
                tr_hist th
            WHERE 
                th.tr_type = 'RCT-WO'
                AND th.tr_date >= DATEADD(month, -1, GETDATE())
                AND th.tr_date < DATEADD(day, 1, EOMONTH(GETDATE(), -1))
        """,
        
        "daily_trend": """
            SELECT 
                CAST(th.tr_date AS DATE) AS transaction_date,
                COUNT(*) AS transaction_count,
                SUM(th.tr_qty) AS total_quantity,
                SUM(th.tr_amt) AS total_amount
            FROM 
                tr_hist th
            WHERE 
                th.tr_type = 'RCT-WO'
                AND th.tr_date >= DATEADD(month, -1, GETDATE())
                AND th.tr_date < DATEADD(day, 1, EOMONTH(GETDATE(), -1))
            GROUP BY 
                CAST(th.tr_date AS DATE)
            ORDER BY 
                transaction_date
        """,
        
        "part_groups": """
            SELECT 
                pt.pt_group,
                COUNT(*) AS transaction_count,
                SUM(th.tr_qty) AS total_quantity,
                SUM(th.tr_amt) AS total_amount
            FROM 
                tr_hist th
            JOIN 
                pt_mstr pt ON th.tr_pt_part = pt.pt_part
            WHERE 
                th.tr_type = 'RCT-WO'
                AND th.tr_date >= DATEADD(month, -1, GETDATE())
                AND th.tr_date < DATEADD(day, 1, EOMONTH(GETDATE(), -1))
            GROUP BY 
                pt.pt_group
            ORDER BY 
                total_quantity DESC
        """,
        
        "top_parts": """
            SELECT TOP 10
                pt.pt_part,
                pt.pt_desc1,
                pt.pt_group,
                COUNT(*) AS transaction_count,
                SUM(th.tr_qty) AS total_quantity,
                SUM(th.tr_amt) AS total_amount
            FROM 
                tr_hist th
            JOIN 
                pt_mstr pt ON th.tr_pt_part = pt.pt_part
            WHERE 
                th.tr_type = 'RCT-WO'
                AND th.tr_date >= DATEADD(month, -1, GETDATE())
                AND th.tr_date < DATEADD(day, 1, EOMONTH(GETDATE(), -1))
            GROUP BY 
                pt.pt_part, pt.pt_desc1, pt.pt_group
            ORDER BY 
                total_quantity DESC
        """,
        
        "locations": """
            SELECT 
                th.tr_loc,
                COUNT(*) AS transaction_count,
                SUM(th.tr_qty) AS total_quantity,
                SUM(th.tr_amt) AS total_amount
            FROM 
                tr_hist th
            WHERE 
                th.tr_type = 'RCT-WO'
                AND th.tr_date >= DATEADD(month, -1, GETDATE())
                AND th.tr_date < DATEADD(day, 1, EOMONTH(GETDATE(), -1))
            GROUP BY 
                th.tr_loc
            ORDER BY 
                total_quantity DESC
        """,
        
        "sample_data": """
            SELECT TOP 20
                th.tr_nbr,
                th.tr_date,
                th.tr_time,
                th.tr_type,
                th.tr_qty,
                th.tr_um,
                th.tr_amt,
                th.tr_loc,
                th.tr_lot,
                th.tr_rmks,
                pt.pt_part,
                pt.pt_desc1,
                pt.pt_desc2,
                pt.pt_group,
                pt.pt_prod_line,
                pt.pt_status
            FROM 
                tr_hist th
            JOIN 
                pt_mstr pt ON th.tr_pt_part = pt.pt_part
            WHERE 
                th.tr_type = 'RCT-WO'
                AND th.tr_date >= DATEADD(month, -1, GETDATE())
                AND th.tr_date < DATEADD(day, 1, EOMONTH(GETDATE(), -1))
            ORDER BY 
                th.tr_date DESC
        """
    }
    
    # Execute queries and format results
    results = {}
    
    for name, query in queries.items():
        log_message(f"\n\n{'-' * 60}")
        log_message(f"Executing query: {name}")
        log_message(f"{'-' * 60}")
        
        try:
            start_time = time.time()
            data = db.execute_query(query)
            elapsed_time = time.time() - start_time
            
            if not data:
                log_message(f"[WARNING] No data returned for query: {name}")
                continue
                
            results[name] = data
            log_message(f"[SUCCESS] Query executed in {elapsed_time:.2f} seconds")
            log_message(f"Retrieved {len(data)} records")
            
            # Format as table
            if name == "summary":
                for key, value in data[0].items():
                    log_message(f"{key}: {value}")
            else:
                # Get column names
                columns = list(data[0].keys())
                
                # Calculate column widths
                col_widths = {}
                for col in columns:
                    col_widths[col] = max(len(str(col)), max(len(str(row.get(col, ''))) for row in data[:20]))
                    col_widths[col] = min(col_widths[col], 30)  # Cap width at 30
                
                # Print header
                header = " | ".join(f"{col:{col_widths[col]}}" for col in columns)
                separator = "-" * len(header)
                log_message(f"\n{header}")
                log_message(separator)
                
                # Print rows (limit to 20 for readability)
                for i, row in enumerate(data[:20]):
                    row_str = " | ".join(f"{str(row.get(col, ''))[:30]:{col_widths[col]}}" for col in columns)
                    log_message(row_str)
                
                # Show if there are more rows
                if len(data) > 20:
                    log_message(f"\n... and {len(data) - 20} more rows")
            
            # Save to JSON
            json_file = output_dir / f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
            log_message(f"\nComplete results saved to {json_file}")
            
        except Exception as e:
            log_message(f"[ERROR] Failed to execute query {name}: {e}")
            import traceback
            log_message(traceback.format_exc())
    
    log_message("\n\n" + "=" * 60)
    log_message("Analysis Complete!")
    log_message(f"Results saved to: {output_file}")
    log_message("=" * 60)
    
    return True

if __name__ == "__main__":
    # Create initial output file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(f"RCT-WO Analysis - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    
    # Run analysis
    success = run_analysis()
    
    if success:
        print(f"\nAnalysis completed successfully!")
        print(f"Results saved to: {output_file}")
    else:
        print(f"\nAnalysis failed. Check the log file for details.")
        sys.exit(1)
