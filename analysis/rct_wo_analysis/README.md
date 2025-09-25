# RCT-WO Analysis

This analysis focuses on the 'RCT-WO' transaction type from the `tr_hist` table, joined with the `pt_mstr` table to provide insights into work order receipts.

## Prerequisites

1. Python 3.7 or higher
2. Access to the SQL Server database (a265m001)
3. Database credentials with read access to `tr_hist` and `pt_mstr` tables

## Setup

1. Clone this repository
2. Navigate to the analysis directory:
   ```
   cd analysis/rct_wo_analysis
   ```
3. Create a Python virtual environment:
   ```
   python -m venv venv
   ```
4. Activate the virtual environment:
   - On Windows:
     ```
     .\venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```
5. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
6. Set up your environment variables:
   - Create a `.env` file in the analysis directory
   - Add your database credentials:
     ```
     DB_USERNAME=your_username
     DB_PASSWORD=your_password
     ```

## Running the Analysis

1. Execute the SQL queries directly (optional):
   ```
   sqlcmd -S a265m001 -d QADEE2798 -U your_username -P your_password -i rct_wo_analysis.sql -o query_results.txt
   ```

2. Generate the full analysis report:
   ```
   python generate_report.py
   ```

## Output

The analysis will generate the following files in the `output` directory:

- `daily_trend.png`: Line chart showing daily transaction quantities
- `part_group.png`: Bar chart showing quantities by part group
- `top_parts.png`: Bar chart showing top 10 parts by quantity
- `location.png`: Bar chart showing quantities by location
- `rct_wo_analysis_report.html`: Complete HTML report with all visualizations and data tables

## Report Contents

The generated HTML report includes:

1. **Summary**: Key metrics (total transactions, quantities, amounts)
2. **Visualizations**:
   - Daily trend of RCT-WO quantities
   - Distribution by part group
   - Top 10 parts by quantity
   - Distribution by location
3. **Detailed Data Tables**:
   - Top parts with descriptions and quantities
   - Part group summaries
   - Location summaries

## Notes

- The analysis focuses on the most recent complete month of data
- All monetary values are in the database's default currency
- Quantities are shown in their original units of measure

## Troubleshooting

- If you encounter connection issues, verify your database credentials and network access
- Ensure the required Python packages are installed
- Check the console output for specific error messages

## License

This analysis is provided as-is under the MIT License.
