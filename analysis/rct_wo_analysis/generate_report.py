#!/usr/bin/env python3
"""
RCT-WO Analysis Report Generator
This script generates visualizations and an HTML report for RCT-WO transactions
"""

import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine
from datetime import datetime, timedelta
import matplotlib.dates as mdates
from pathlib import Path

# Configuration
OUTPUT_DIR = Path(__file__).parent / 'output'
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

# Database connection
def get_db_connection():
    """Create and return a database connection"""
    server = 'a265m001'
    database = 'QADEE2798'
    
    # Get credentials from environment variables
    username = os.getenv('DB_USERNAME')
    password = os.getenv('DB_PASSWORD')
    
    if not username or not password:
        raise ValueError("DB_USERNAME and DB_PASSWORD environment variables must be set")
    
    connection_string = f'mssql+pymssql://{username}:{password}@{server}/{database}'
    return create_engine(connection_string)

def setup_plotting():
    """Configure plotting style"""
    sns.set_style("whitegrid")
    plt.rcParams['figure.figsize'] = (14, 8)
    plt.rcParams['font.size'] = 12


def execute_query(engine, query, params=None):
    """Execute a SQL query and return results as a DataFrame"""
    try:
        return pd.read_sql(query, engine, params=params)
    except Exception as e:
        print(f"Error executing query: {e}")
        raise


def generate_visualizations(engine, start_date, end_date):
    """Generate all visualizations"""
    # 1. Daily trend
    daily_query = """
    SELECT 
        CAST(tr_date AS DATE) AS transaction_date,
        COUNT(*) AS transaction_count,
        SUM(tr_qty) AS total_quantity,
        SUM(tr_amt) AS total_amount
    FROM tr_hist
    WHERE tr_type = 'RCT-WO'
      AND tr_date >= %(start_date)s
      AND tr_date <= %(end_date)s
    GROUP BY CAST(tr_date AS DATE)
    ORDER BY transaction_date
    """
    
    # 2. By part group
    part_group_query = """
    SELECT 
        pt.pt_group,
        COUNT(*) AS transaction_count,
        SUM(th.tr_qty) AS total_quantity,
        SUM(th.tr_amt) AS total_amount
    FROM tr_hist th
    JOIN pt_mstr pt ON th.tr_pt_part = pt.pt_part
    WHERE th.tr_type = 'RCT-WO'
      AND th.tr_date >= %(start_date)s
      AND th.tr_date <= %(end_date)s
    GROUP BY pt.pt_group
    ORDER BY total_quantity DESC
    """
    
    # 3. Top parts
    top_parts_query = """
    SELECT TOP 10
        pt.pt_part,
        pt.pt_desc1,
        pt.pt_group,
        COUNT(*) AS transaction_count,
        SUM(th.tr_qty) AS total_quantity,
        SUM(th.tr_amt) AS total_amount
    FROM tr_hist th
    JOIN pt_mstr pt ON th.tr_pt_part = pt.pt_part
    WHERE th.tr_type = 'RCT-WO'
      AND th.tr_date >= %(start_date)s
      AND th.tr_date <= %(end_date)s
    GROUP BY pt.pt_part, pt.pt_desc1, pt.pt_group
    ORDER BY total_quantity DESC
    """
    
    # 4. By location
    location_query = """
    SELECT 
        tr_loc,
        COUNT(*) AS transaction_count,
        SUM(tr_qty) AS total_quantity,
        SUM(tr_amt) AS total_amount
    FROM tr_hist
    WHERE tr_type = 'RCT-WO'
      AND tr_date >= %(start_date)s
      AND tr_date <= %(end_date)s
    GROUP BY tr_loc
    ORDER BY total_quantity DESC
    """
    
    # Common parameters
    params = {
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d')
    }
    
    # Execute queries
    print("Executing queries...")
    daily_df = execute_query(engine, daily_query, params)
    part_group_df = execute_query(engine, part_group_query, params)
    top_parts_df = execute_query(engine, top_parts_query, params)
    location_df = execute_query(engine, location_query, params)
    
    # 1. Daily Trend
    print("Generating daily trend visualization...")
    plt.figure()
    plt.plot(daily_df['transaction_date'], daily_df['total_quantity'], 
             marker='o', linestyle='-', color='#1f77b4')
    plt.title(f'Daily RCT-WO Quantity Trend - {start_date.strftime("%B %Y")}')
    plt.xlabel('Date')
    plt.ylabel('Total Quantity')
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%m-%d'))
    plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=2))
    plt.xticks(rotation=45)
    plt.tight_layout()
    daily_chart = OUTPUT_DIR / 'daily_trend.png'
    plt.savefig(daily_chart, dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Part Group Distribution
    print("Generating part group visualization...")
    plt.figure()
    part_group_df = part_group_df.sort_values('total_quantity', ascending=False)
    sns.barplot(x='total_quantity', y='pt_group', data=part_group_df, palette='viridis')
    plt.title('RCT-WO Quantity by Part Group')
    plt.xlabel('Total Quantity')
    plt.ylabel('Part Group')
    plt.tight_layout()
    part_group_chart = OUTPUT_DIR / 'part_group.png'
    plt.savefig(part_group_chart, dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3. Top Parts
    print("Generating top parts visualization...")
    plt.figure()
    top_parts_df = top_parts_df.sort_values('total_quantity', ascending=True)
    sns.barplot(x='total_quantity', y='pt_part', data=top_parts_df, palette='rocket')
    plt.title('Top 10 Parts by RCT-WO Quantity')
    plt.xlabel('Total Quantity')
    plt.ylabel('Part Number')
    plt.tight_layout()
    top_parts_chart = OUTPUT_DIR / 'top_parts.png'
    plt.savefig(top_parts_chart, dpi=300, bbox_inches='tight')
    plt.close()
    
    # 4. Location Distribution
    print("Generating location visualization...")
    plt.figure()
    location_df = location_df.sort_values('total_quantity', ascending=False)
    sns.barplot(x='total_quantity', y='tr_loc', data=location_df, palette='mako')
    plt.title('RCT-WO Quantity by Location')
    plt.xlabel('Total Quantity')
    plt.ylabel('Location')
    plt.tight_layout()
    location_chart = OUTPUT_DIR / 'location.png'
    plt.savefig(location_chart, dpi=300, bbox_inches='tight')
    plt.close()
    
    return {
        'daily': daily_df,
        'part_groups': part_group_df,
        'top_parts': top_parts_df,
        'locations': location_df,
        'charts': {
            'daily': daily_chart.relative_to(OUTPUT_DIR),
            'part_groups': part_group_chart.relative_to(OUTPUT_DIR),
            'top_parts': top_parts_chart.relative_to(OUTPUT_DIR),
            'locations': location_chart.relative_to(OUTPUT_DIR)
        }
    }


def generate_html_report(data, start_date, end_date):
    """Generate HTML report from the analysis data"""
    print("Generating HTML report...")
    
    # Format data for display
    total_transactions = data['daily']['transaction_count'].sum()
    total_quantity = data['daily']['total_quantity'].sum()
    total_amount = data['daily']['total_amount'].sum()
    
    # Generate HTML
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>RCT-WO Analysis Report - {start_date.strftime('%B %Y')}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .header {{ margin-bottom: 30px; }}
            .summary {{ background: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 30px; }}
            .grid {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            .card {{ 
                background: white; 
                padding: 15px; 
                border-radius: 5px; 
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .card img {{ 
                max-width: 100%; 
                height: auto;
                border: 1px solid #ddd;
                border-radius: 4px;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 15px 0;
            }}
            th, td {{
                padding: 10px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            th {{
                background-color: #f2f2f2;
                font-weight: bold;
            }}
            tr:hover {{ background-color: #f5f5f5; }}
            .section {{ margin: 30px 0; }}
            h1, h2, h3 {{ color: #2c3e50; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>RCT-WO Analysis Report</h1>
                <p>Period: {start_date.strftime('%B %d, %Y')} to {end_date.strftime('%B %d, %Y')}</p>
            </div>
            
            <div class="summary">
                <h2>Summary</h2>
                <table>
                    <tr>
                        <th>Metric</th>
                        <th>Value</th>
                    </tr>
                    <tr>
                        <td>Total Transactions</td>
                        <td>{total_transactions:,}</td>
                    </tr>
                    <tr>
                        <td>Total Quantity</td>
                        <td>{total_quantity:,.2f}</td>
                    </tr>
                    <tr>
                        <td>Total Amount</td>
                        <td>${total_amount:,.2f}</td>
                    </tr>
                </table>
            </div>
            
            <div class="section">
                <h2>Visualizations</h2>
                <div class="grid">
                    <div class="card">
                        <h3>Daily Trend</h3>
                        <img src="{data['charts']['daily']}" alt="Daily Trend">
                    </div>
                    <div class="card">
                        <h3>By Part Group</h3>
                        <img src="{data['charts']['part_groups']}" alt="By Part Group">
                    </div>
                    <div class="card">
                        <h3>Top Parts</h3>
                        <img src="{data['charts']['top_parts']}" alt="Top Parts">
                    </div>
                    <div class="card">
                        <h3>By Location</h3>
                        <img src="{data['charts']['locations']}" alt="By Location">
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>Top Parts Details</h2>
                {data['top_parts'].to_html(index=False, float_format=lambda x: f"{x:,.2f}" if isinstance(x, (int, float)) else str(x))}
            </div>
            
            <div class="section">
                <h2>Part Group Summary</h2>
                {data['part_groups'].to_html(index=False, float_format=lambda x: f"{x:,.2f}" if isinstance(x, (int, float)) else str(x))}
            </div>
            
            <div class="section">
                <h2>Location Summary</h2>
                {data['locations'].to_html(index=False, float_format=lambda x: f"{x:,.2f}" if isinstance(x, (int, float)) else str(x))}
            </div>
        </div>
    </body>
    </html>
    """
    
    # Save the HTML report
    report_path = OUTPUT_DIR / 'rct_wo_analysis_report.html'
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return report_path


def main():
    """Main function to run the analysis"""
    print("Starting RCT-WO Analysis...")
    
    # Set up date range (last complete month)
    end_date = datetime.now().replace(day=1) - timedelta(days=1)  # Last day of last month
    start_date = end_date.replace(day=1)  # First day of last month
    
    print(f"Analyzing data from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    
    try:
        # Set up environment
        setup_plotting()
        
        # Connect to database
        print("Connecting to database...")
        engine = get_db_connection()
        
        # Generate visualizations and get data
        data = generate_visualizations(engine, start_date, end_date)
        
        # Generate HTML report
        report_path = generate_html_report(data, start_date, end_date)
        
        print(f"\nAnalysis complete!")
        print(f"Report generated at: {report_path}")
        print(f"Visualizations saved in: {OUTPUT_DIR}")
        
    except Exception as e:
        print(f"Error during analysis: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
