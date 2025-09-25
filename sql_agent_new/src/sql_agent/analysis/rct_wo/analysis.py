#!/usr/bin/env python3
"""
Standalone RCT-WO Analysis - No external dependencies
"""

import os
import sys
import json
import time
from pathlib import Path
from datetime import datetime
import pymssql

# Configure output
output_dir = Path(__file__).parent / "results"
output_dir.mkdir(exist_ok=True, parents=True)
output_file = output_dir / f"rct_wo_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

def log_message(message):
    """Log message to console and file"""
    print(message)
    sys.stdout.flush()
    with open(output_file, "a", encoding="utf-8") as f:
        f.write(f"{message}\n")

def execute_query(conn, query):
    """Execute SQL query and return results as list of dictionaries"""
    cursor = conn.cursor(as_dict=True)
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    return results

def run_analysis():
    """Run RCT-WO analysis with direct database connection"""
    log_message("=" * 60)
    log_message(f"RCT-WO Analysis - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log_message("=" * 60)
    
    # Connect to database
    log_message("\nConnecting to database...")
    try:
        conn = pymssql.connect(
            server='a265m001',
            user='PowerBI',
            password='P0werB1',
            database='QADEE2798'
        )
        log_message("[SUCCESS] Database connection successful")
    except Exception as e:
        log_message(f"[ERROR] Database connection failed: {e}")
        return False
    
    # Define queries with corrected column names
    queries = {
        "summary": """
            SELECT 
                COUNT(*) AS total_transactions,
                SUM(tr_qty_chg) AS total_quantity,
                SUM(tr_gl_amt) AS total_amount,
                AVG(tr_qty_chg) AS avg_quantity,
                AVG(tr_gl_amt) AS avg_amount
            FROM 
                tr_hist
            WHERE 
                tr_type = 'RCT-WO'
                AND tr_date >= DATEADD(month, -1, GETDATE())
                AND tr_date < DATEADD(day, 1, EOMONTH(GETDATE(), -1))
        """,
        
        "daily_trend": """
            SELECT 
                CAST(tr_date AS DATE) AS transaction_date,
                COUNT(*) AS transaction_count,
                SUM(tr_qty_chg) AS total_quantity,
                SUM(tr_gl_amt) AS total_amount
            FROM 
                tr_hist
            WHERE 
                tr_type = 'RCT-WO'
                AND tr_date >= DATEADD(month, -1, GETDATE())
                AND tr_date < DATEADD(day, 1, EOMONTH(GETDATE(), -1))
            GROUP BY 
                CAST(tr_date AS DATE)
            ORDER BY 
                transaction_date
        """,
        
        "part_groups": """
            SELECT 
                pt.pt_group,
                COUNT(*) AS transaction_count,
                SUM(tr.tr_qty_chg) AS total_quantity,
                SUM(tr.tr_gl_amt) AS total_amount
            FROM 
                tr_hist tr
            JOIN 
                pt_mstr pt ON tr.tr_part = pt.pt_part
            WHERE 
                tr.tr_type = 'RCT-WO'
                AND tr.tr_date >= DATEADD(month, -1, GETDATE())
                AND tr.tr_date < DATEADD(day, 1, EOMONTH(GETDATE(), -1))
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
                SUM(tr.tr_qty_chg) AS total_quantity,
                SUM(tr.tr_gl_amt) AS total_amount
            FROM 
                tr_hist tr
            JOIN 
                pt_mstr pt ON tr.tr_part = pt.pt_part
            WHERE 
                tr.tr_type = 'RCT-WO'
                AND tr.tr_date >= DATEADD(month, -1, GETDATE())
                AND tr.tr_date < DATEADD(day, 1, EOMONTH(GETDATE(), -1))
            GROUP BY 
                pt.pt_part, pt.pt_desc1, pt.pt_group
            ORDER BY 
                total_quantity DESC
        """,
        
        "locations": """
            SELECT 
                tr_loc,
                COUNT(*) AS transaction_count,
                SUM(tr_qty_chg) AS total_quantity,
                SUM(tr_gl_amt) AS total_amount
            FROM 
                tr_hist
            WHERE 
                tr_type = 'RCT-WO'
                AND tr_date >= DATEADD(month, -1, GETDATE())
                AND tr_date < DATEADD(day, 1, EOMONTH(GETDATE(), -1))
            GROUP BY 
                tr_loc
            ORDER BY 
                total_quantity DESC
        """,
        
        "sample_data": """
            SELECT TOP 20
                tr_nbr,
                tr_date,
                tr_time,
                tr_type,
                tr_qty_chg,
                tr_um,
                tr_gl_amt,
                tr_loc,
                tr_lot,
                tr_rmks,
                tr_part,
                tr_prod_line,
                tr_status
            FROM 
                tr_hist
            WHERE 
                tr_type = 'RCT-WO'
                AND tr_date >= DATEADD(month, -1, GETDATE())
                AND tr_date < DATEADD(day, 1, EOMONTH(GETDATE(), -1))
            ORDER BY 
                tr_date DESC
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
            data = execute_query(conn, query)
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
    
    # Generate simple HTML report
    try:
        log_message("\n\nGenerating HTML report...")
        html_report = output_dir / f"rct_wo_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>RCT-WO Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1, h2 {{ color: #333366; }}
                table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                .summary {{ background-color: #eef; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                .section {{ margin-bottom: 30px; }}
            </style>
        </head>
        <body>
            <h1>RCT-WO Analysis Report</h1>
            <p>Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        """
        
        # Add summary section if available
        if "summary" in results and results["summary"]:
            summary = results["summary"][0]
            html_content += """
            <div class="section">
                <h2>Summary</h2>
                <div class="summary">
                    <table>
                        <tr><th>Metric</th><th>Value</th></tr>
            """
            
            for key, value in summary.items():
                html_content += f"<tr><td>{key}</td><td>{value}</td></tr>"
                
            html_content += """
                    </table>
                </div>
            </div>
            """
        
        # Add other sections
        for name, data in results.items():
            if name == "summary" or not data:
                continue
                
            html_content += f"""
            <div class="section">
                <h2>{name.replace('_', ' ').title()}</h2>
                <table>
                    <tr>
            """
            
            # Add headers
            columns = list(data[0].keys())
            for col in columns:
                html_content += f"<th>{col}</th>"
                
            html_content += "</tr>"
            
            # Add rows (limit to 50 for readability)
            for row in data[:50]:
                html_content += "<tr>"
                for col in columns:
                    html_content += f"<td>{row.get(col, '')}</td>"
                html_content += "</tr>"
                
            html_content += """
                </table>
            </div>
            """
        
        html_content += """
        </body>
        </html>
        """
        
        with open(html_report, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        log_message(f"HTML report generated: {html_report}")
        
    except Exception as e:
        log_message(f"[ERROR] Failed to generate HTML report: {e}")
        import traceback
        log_message(traceback.format_exc())
    
    # Close database connection
    conn.close()
    
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
